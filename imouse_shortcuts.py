#!/usr/bin/env python3
"""
iMouse Shortcuts - Envío de atajos de teclado al iPhone/iPad
Envía combinaciones de teclas como Win+H (Home), Win+Tab (App Switcher), etc.
"""

import sys
import time
import os

try:
    import pywinusb.hid as hid
except ImportError:
    print("❌ Error: pywinusb no está instalado")
    print("   pip install pywinusb")
    sys.exit(1)


# Modificadores de teclado (pueden combinarse con OR)
MODIFIER_NONE = 0x00
MODIFIER_CTRL = 0x01
MODIFIER_SHIFT = 0x02
MODIFIER_ALT = 0x04
MODIFIER_WIN = 0x08  # Tecla Windows/Command/iOS Home


# Scancodes de teclas utilizadas
SCANCODE_H = 0x0b       # Tecla H (para Home)
SCANCODE_TAB = 0x2b     # Tecla Tab (para App Switcher)
SCANCODE_SPACE = 0x2c   # Barra espaciadora (para Spotlight)
SCANCODE_3 = 0x20       # Número 3 (para Screenshot)


class ShortcutSender:
    def __init__(self):
        self.device = None
        self.out_report = None
        self.report_size = 0
        self.stats = {'shortcuts': 0, 'errors': 0}

    def connect_device(self):
        """Conecta con el dispositivo iMouse"""
        VENDOR_ID = 0x720a
        PRODUCT_ID = 0x3dab

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

    def send_key_combo(self, scancode, modifier=MODIFIER_NONE, hold_time=0.05):
        """
        Envía una combinación de tecla con modificador

        Args:
            scancode: Código de la tecla principal
            modifier: Modificadores (CTRL, SHIFT, ALT, WIN)
            hold_time: Tiempo que se mantiene presionada la combinación
        """
        if not self.out_report:
            return False

        try:
            # Preparar paquete keypress con modificador
            packet = [0x00, 0xa2, modifier, 0x00, scancode]
            while len(packet) < self.report_size:
                packet.append(0x00)

            # Enviar keypress
            self.out_report.set_raw_data(packet)
            self.out_report.send()

            # Mantener presionado
            time.sleep(hold_time)

            # Enviar release
            release = [0x00, 0xa2, 0x00, 0x00, 0x00]
            while len(release) < self.report_size:
                release.append(0x00)

            self.out_report.set_raw_data(release)
            self.out_report.send()

            # Pequeña pausa después de soltar
            time.sleep(0.05)

            self.stats['shortcuts'] += 1
            return True

        except Exception as e:
            self.stats['errors'] += 1
            print(f"❌ Error enviando combinación: {e}")
            return False

    def go_home(self):
        """Win+H - Ir a la pantalla de inicio"""
        print("🏠 Enviando: Win+H (Home Screen)...", end='', flush=True)
        if self.send_key_combo(SCANCODE_H, MODIFIER_WIN):
            print(" ✓")
            return True
        print(" ✗")
        return False

    def app_switcher(self):
        """Win+Tab - Abrir selector de aplicaciones"""
        print("📱 Enviando: Win+Tab (App Switcher)...", end='', flush=True)
        if self.send_key_combo(SCANCODE_TAB, MODIFIER_WIN):
            print(" ✓")
            return True
        print(" ✗")
        return False

    def spotlight_search(self):
        """Win+Space - Búsqueda Spotlight"""
        print("🔍 Enviando: Win+Space (Spotlight Search)...", end='', flush=True)
        if self.send_key_combo(SCANCODE_SPACE, MODIFIER_WIN):
            print(" ✓")
            return True
        print(" ✗")
        return False

    def screenshot(self):
        """Win+Shift+3 - Captura de pantalla"""
        print("📸 Enviando: Win+Shift+3 (Screenshot)...", end='', flush=True)
        if self.send_key_combo(SCANCODE_3, MODIFIER_WIN | MODIFIER_SHIFT):
            print(" ✓")
            return True
        print(" ✗")
        return False

    def run(self):
        """Ejecuta el modo interactivo"""
        if not self.connect_device():
            return

        shortcuts = {
            '1': ('Home Screen', self.go_home),
            '2': ('App Switcher', self.app_switcher),
            '3': ('Spotlight Search', self.spotlight_search),
            '4': ('Screenshot', self.screenshot),
        }

        print()
        print("=" * 80)
        print("⌨️  iMOUSE SHORTCUTS - ATAJOS DE TECLADO PARA iOS")
        print("=" * 80)
        print()
        print("📱 ATAJOS DISPONIBLES:")
        print()
        print("  1. Win+H         → 🏠 Home Screen (Pantalla de inicio)")
        print("  2. Win+Tab       → 📱 App Switcher (Selector de apps)")
        print("  3. Win+Space     → 🔍 Spotlight Search (Búsqueda)")
        print("  4. Win+Shift+3   → 📸 Screenshot (Captura de pantalla)")
        print()
        print("  === ATAJOS RÁPIDOS ===")
        print("  h     → Ir directamente a Home (Win+H)")
        print("  s     → Abrir búsqueda Spotlight (Win+Space)")
        print("  p     → Tomar screenshot (Win+Shift+3)")
        print()
        print("  clear → Limpiar pantalla")
        print("  exit  → Salir")
        print()
        print("=" * 80)
        print()

        try:
            while True:
                try:
                    choice = input("⌨️  Elige un atajo (número o comando) > ").strip().lower()
                except KeyboardInterrupt:
                    print("\n⚠️  Interrupción detectada")
                    break

                if not choice:
                    continue

                # Comandos especiales
                if choice in ['exit', 'quit', 'salir', 'q']:
                    print("\n👋 Saliendo...")
                    break

                if choice in ['clear', 'cls']:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("⌨️  iMOUSE SHORTCUTS")
                    print("=" * 80)
                    print("Escribe el número del atajo o 'h' para Home")
                    continue

                # Atajos directos
                if choice == 'h':
                    self.go_home()
                    continue
                elif choice == 's':
                    self.spotlight_search()
                    continue
                elif choice == 'p':
                    self.screenshot()
                    continue

                # Ejecutar atajo por número
                if choice in shortcuts:
                    name, func = shortcuts[choice]
                    func()
                else:
                    print("❌ Opción no válida. Usa 1-4, o atajos rápidos: h, s, p")

        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")

        finally:
            # Cerrar dispositivo
            if self.device:
                self.device.close()

            # Mostrar estadísticas
            print()
            print("=" * 80)
            print("📊 ESTADÍSTICAS DE LA SESIÓN:")
            print(f"   Atajos enviados: {self.stats['shortcuts']}")
            print(f"   Errores:         {self.stats['errors']}")
            print("=" * 80)


def main():
    sender = ShortcutSender()

    try:
        sender.run()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupción detectada")

    input("\nPresiona ENTER para salir...")


if __name__ == "__main__":
    main()