#!/usr/bin/env python3
"""
iMouse Realtime - Envío de teclas en tiempo real al iPhone
Cada tecla que presiones se envía instantáneamente al dispositivo
"""

import sys
import time
import threading
from queue import Queue

try:
    import pywinusb.hid as hid
except ImportError:
    print("❌ Error: pywinusb no está instalado")
    print("   pip install pywinusb")
    sys.exit(1)

try:
    from pynput import keyboard
except ImportError:
    print("❌ Error: pynput no está instalado")
    print("   pip install pynput")
    sys.exit(1)


# ===== CONFIGURACIÓN =====
VENDOR_ID = 0x720a
PRODUCT_ID = 0x3dab

# Tecla de activación/desactivación
# Opciones comunes:
# - keyboard.Key.f9          (Tecla F9)
# - keyboard.Key.f10         (Tecla F10)
# - keyboard.Key.f12         (Tecla F12)
# - keyboard.Key.pause       (Tecla Pause/Break)
# - keyboard.Key.scroll_lock (Scroll Lock - no todos los teclados la tienen)
# - keyboard.Key.insert      (Tecla Insert)
TOGGLE_KEY = keyboard.Key.f9  # Cambiado a F9 que todos los teclados tienen

# ===== KEYMAP =====
IMOUSE_KEYMAP = {
    # Letras minúsculas
    'a': (0x04, 0x00), 'b': (0x05, 0x00), 'c': (0x06, 0x00), 'd': (0x07, 0x00),
    'e': (0x08, 0x00), 'f': (0x09, 0x00), 'g': (0x0a, 0x00), 'h': (0x0b, 0x00),
    'i': (0x0c, 0x00), 'j': (0x0d, 0x00), 'k': (0x0e, 0x00), 'l': (0x0f, 0x00),
    'm': (0x10, 0x00), 'n': (0x11, 0x00), 'o': (0x12, 0x00), 'p': (0x13, 0x00),
    'q': (0x14, 0x00), 'r': (0x15, 0x00), 's': (0x16, 0x00), 't': (0x17, 0x00),
    'u': (0x18, 0x00), 'v': (0x19, 0x00), 'w': (0x1a, 0x00), 'x': (0x1b, 0x00),
    'y': (0x1c, 0x00), 'z': (0x1d, 0x00),

    # Letras mayúsculas
    'A': (0x04, 0x02), 'B': (0x05, 0x02), 'C': (0x06, 0x02), 'D': (0x07, 0x02),
    'E': (0x08, 0x02), 'F': (0x09, 0x02), 'G': (0x0a, 0x02), 'H': (0x0b, 0x02),
    'I': (0x0c, 0x02), 'J': (0x0d, 0x02), 'K': (0x0e, 0x02), 'L': (0x0f, 0x02),
    'M': (0x10, 0x02), 'N': (0x11, 0x02), 'O': (0x12, 0x02), 'P': (0x13, 0x02),
    'Q': (0x14, 0x02), 'R': (0x15, 0x02), 'S': (0x16, 0x02), 'T': (0x17, 0x02),
    'U': (0x18, 0x02), 'V': (0x19, 0x02), 'W': (0x1a, 0x02), 'X': (0x1b, 0x02),
    'Y': (0x1c, 0x02), 'Z': (0x1d, 0x02),

    # Números
    '0': (0x27, 0x00), '1': (0x1e, 0x00), '2': (0x1f, 0x00), '3': (0x20, 0x00),
    '4': (0x21, 0x00), '5': (0x22, 0x00), '6': (0x23, 0x00), '7': (0x24, 0x00),
    '8': (0x25, 0x00), '9': (0x26, 0x00),

    # Símbolos sin Shift
    ' ': (0x2c, 0x00), '-': (0x2d, 0x00), '=': (0x2e, 0x00), '[': (0x2f, 0x00),
    ']': (0x30, 0x00), '\\': (0x31, 0x00), ';': (0x33, 0x00), "'": (0x34, 0x00),
    '`': (0x35, 0x00), ',': (0x36, 0x00), '.': (0x37, 0x00), '/': (0x38, 0x00),

    # Símbolos con Shift
    '+': (0x2e, 0x02), '{': (0x2f, 0x02), '}': (0x30, 0x02), '|': (0x31, 0x02),
    ':': (0x33, 0x02), '"': (0x34, 0x02), '~': (0x35, 0x02), '<': (0x36, 0x02),
    '>': (0x37, 0x02), '?': (0x38, 0x02),

    # Símbolos números con Shift
    '!': (0x1e, 0x02), '@': (0x1f, 0x02), '#': (0x20, 0x02), '$': (0x21, 0x02),
    '%': (0x22, 0x02), '^': (0x23, 0x02), '&': (0x24, 0x02), '*': (0x25, 0x02),
    '(': (0x26, 0x02), ')': (0x27, 0x02), '_': (0x2d, 0x02),
}

# Mapeo de teclas especiales de pynput a scancodes
SPECIAL_KEYS = {
    keyboard.Key.enter: (0x28, 0x00),       # Enter
    keyboard.Key.tab: (0x2b, 0x00),         # Tab
    keyboard.Key.backspace: (0x2a, 0x00),   # Backspace
    keyboard.Key.space: (0x2c, 0x00),       # Space
    keyboard.Key.esc: (0x29, 0x00),         # Escape
    keyboard.Key.delete: (0x4c, 0x00),      # Delete
    keyboard.Key.home: (0x4a, 0x00),        # Home
    keyboard.Key.end: (0x4d, 0x00),         # End
    keyboard.Key.page_up: (0x4b, 0x00),     # Page Up
    keyboard.Key.page_down: (0x4e, 0x00),   # Page Down
    keyboard.Key.right: (0x4f, 0x00),       # Right Arrow
    keyboard.Key.left: (0x50, 0x00),        # Left Arrow
    keyboard.Key.down: (0x51, 0x00),        # Down Arrow
    keyboard.Key.up: (0x52, 0x00),          # Up Arrow
}


class RealtimeTyper:
    def __init__(self):
        self.device = None
        self.out_report = None
        self.report_size = 0
        self.active = False
        self.running = True
        self.key_queue = Queue()
        self.shift_pressed = False
        self.caps_lock = False
        self.stats = {'keys': 0, 'errors': 0}

    def connect_device(self):
        """Conecta con el dispositivo iMouse"""
        print("🔌 Conectando con dispositivo iMouse...")
        devices = hid.HidDeviceFilter(vendor_id=VENDOR_ID, product_id=PRODUCT_ID).get_devices()

        if not devices:
            print(f"❌ Dispositivo no encontrado: 0x{VENDOR_ID:04x}:0x{PRODUCT_ID:04x}")
            return False

        self.device = devices[0]

        try:
            self.device.open()
        except Exception as e:
            print(f"❌ No se pudo abrir el dispositivo: {e}")
            return False

        print(f"✅ Conectado a: {self.device.product_name}")

        # Obtener output report
        for report in self.device.find_output_reports():
            self.out_report = report
            break

        if not self.out_report:
            print("❌ No se encontró output report")
            self.device.close()
            return False

        self.report_size = len(self.out_report.get_raw_data())
        return True

    def send_key(self, scancode, modifier):
        """Envía una tecla al dispositivo"""
        if not self.out_report:
            return False

        try:
            # Preparar paquete keypress
            packet = [0x00, 0xa2, modifier, 0x00, scancode]
            while len(packet) < self.report_size:
                packet.append(0x00)

            # Enviar keypress
            self.out_report.set_raw_data(packet)
            self.out_report.send()

            # Pequeño delay
            time.sleep(0.01)

            # Enviar release
            release = [0x00, 0xa2, 0x00, 0x00, 0x00]
            while len(release) < self.report_size:
                release.append(0x00)

            self.out_report.set_raw_data(release)
            self.out_report.send()

            self.stats['keys'] += 1
            return True

        except Exception as e:
            self.stats['errors'] += 1
            return False

    def process_queue(self):
        """Procesa la cola de teclas en un thread separado"""
        while self.running:
            try:
                key_data = self.key_queue.get(timeout=0.1)
                if key_data:
                    scancode, modifier = key_data
                    self.send_key(scancode, modifier)
            except:
                continue

    def on_press(self, key):
        """Callback cuando se presiona una tecla"""
        # Detectar tecla de toggle
        if key == TOGGLE_KEY:
            self.active = not self.active
            status = "ACTIVADO 🟢" if self.active else "DESACTIVADO 🔴"
            print(f"\r{'=' * 60}")
            print(f"   Modo espejo: {status}")
            print(f"{'=' * 60}")
            if self.active:
                print("   📡 Enviando teclas en tiempo real...")
            else:
                print("   ⏸️  Modo espejo pausado")
            return

        # Detectar Escape para salir
        if key == keyboard.Key.esc and not self.active:
            print("\n👋 Saliendo...")
            self.running = False
            return False

        # Si no está activo, ignorar
        if not self.active:
            return

        # Actualizar estado de Shift y Caps Lock
        if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
            self.shift_pressed = True
            return
        elif key == keyboard.Key.caps_lock:
            self.caps_lock = not self.caps_lock
            return

        # Procesar la tecla
        key_data = None

        # Verificar si es una tecla especial
        if key in SPECIAL_KEYS:
            key_data = SPECIAL_KEYS[key]

        # Si es un carácter normal
        elif hasattr(key, 'char') and key.char:
            char = key.char

            # Determinar si necesita mayúscula
            if char.isalpha():
                if self.caps_lock ^ self.shift_pressed:
                    char = char.upper()
                else:
                    char = char.lower()

            # Buscar en el keymap
            if char in IMOUSE_KEYMAP:
                key_data = IMOUSE_KEYMAP[char]

        # Enviar la tecla si se encontró mapping
        if key_data:
            self.key_queue.put(key_data)
            # Mostrar feedback visual
            print(".", end="", flush=True)

    def on_release(self, key):
        """Callback cuando se suelta una tecla"""
        # Actualizar estado de Shift
        if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
            self.shift_pressed = False

    def run(self):
        """Ejecuta el modo tiempo real"""
        if not self.connect_device():
            return

        print()
        print("=" * 80)
        print("⌨️  iMOUSE REALTIME - MODO ESPEJO EN TIEMPO REAL")
        print("=" * 80)
        print()
        print("📝 Instrucciones:")
        print(f"   • Presiona {TOGGLE_KEY.name.upper()} para ACTIVAR/DESACTIVAR el modo espejo")
        print("   • Cuando está ACTIVO, todo lo que teclees se envía al iPhone")
        print("   • Presiona ESC (con modo desactivado) para salir")
        print()
        print("⚠️  IMPORTANTE:")
        print("   • Desactiva el modo antes de cambiar de ventana")
        print("   • El texto aparece tanto en tu PC como en el iPhone")
        print()
        print("=" * 80)
        print("   Modo espejo: DESACTIVADO 🔴")
        print("=" * 80)
        print(f"   Presiona {TOGGLE_KEY.name.upper()} para activar...")

        # Iniciar thread para procesar teclas
        processor_thread = threading.Thread(target=self.process_queue, daemon=True)
        processor_thread.start()

        # Iniciar listener de teclado
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        ) as listener:
            listener.join()

        # Limpiar
        self.running = False
        if self.device:
            self.device.close()

        # Mostrar estadísticas
        print()
        print("=" * 80)
        print("📊 ESTADÍSTICAS DE LA SESIÓN:")
        print(f"   Teclas enviadas: {self.stats['keys']}")
        print(f"   Errores:         {self.stats['errors']}")
        print("=" * 80)


def main():
    typer = RealtimeTyper()

    try:
        typer.run()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupción detectada")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    input("\nPresiona ENTER para salir...")


if __name__ == "__main__":
    main()