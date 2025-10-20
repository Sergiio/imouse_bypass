#!/usr/bin/env python3
"""
iMouse Typer - Envío continuo de texto al iPhone
Escribe texto y pulsa Enter para enviarlo directamente al dispositivo
"""

import sys
import json
import time
import os
import tempfile

try:
    import pywinusb.hid as hid
except ImportError:
    print("❌ Error: pywinusb no está instalado")
    print("   pip install pywinusb")
    sys.exit(1)


# ===== KEYMAP DESDE imouse_complete_keymap.py =====
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

    # Teclas especiales
    '\n': (0x28, 0x00),      # Enter
    '\t': (0x2b, 0x00),      # Tab
    '\x08': (0x2a, 0x00),    # Backspace
}


def char_to_imouse_packet(char):
    """Convierte un carácter a paquete iMouse de 9 bytes"""
    if char not in IMOUSE_KEYMAP:
        return None

    scancode, modifier = IMOUSE_KEYMAP[char]
    # Formato: [Report ID][0xa2][Modifier][Reserved][Scancode][Padding...]
    return [0x00, 0xa2, modifier, 0x00, scancode, 0x00, 0x00, 0x00, 0x00]


def send_text_directly(text, device, out_report, typing_delay=0.03):
    """
    Envía texto directamente al dispositivo sin crear archivo intermedio

    Args:
        text: Texto a enviar
        device: Dispositivo HID abierto
        out_report: Output report del dispositivo
        typing_delay: Retraso entre teclas (segundos)
    """

    sent_count = 0
    error_count = 0
    report_size = len(out_report.get_raw_data())

    for char in text:
        # Generar paquete de keypress
        packet = char_to_imouse_packet(char)

        if packet is None:
            print(f"  ⚠️  Carácter no soportado: '{char}'", end='')
            continue

        # Ajustar al tamaño del reporte
        data_list = packet[:]
        while len(data_list) < report_size:
            data_list.append(0x00)

        # Enviar keypress
        try:
            out_report.set_raw_data(data_list)
            out_report.send()
            sent_count += 1

            # Pequeño delay para keypress
            time.sleep(typing_delay)

            # Enviar release
            release = [0x00, 0xa2, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            while len(release) < report_size:
                release.append(0x00)

            out_report.set_raw_data(release)
            out_report.send()

            # Delay entre teclas
            time.sleep(typing_delay / 2)

        except Exception as e:
            error_count += 1
            if error_count <= 3:
                print(f"\n  ❌ Error enviando '{char}': {e}")

    return sent_count, error_count


def main():
    # Configuración del dispositivo
    VENDOR_ID = 0x720a
    PRODUCT_ID = 0x3dab

    print("=" * 80)
    print("⌨️  iMOUSE TYPER - MODO CONTINUO")
    print("=" * 80)
    print()
    print("📝 Instrucciones:")
    print("   - Escribe tu texto y pulsa ENTER para enviarlo")
    print("   - Escribe 'exit' o 'salir' para terminar")
    print("   - Escribe 'clear' o 'cls' para limpiar pantalla")
    print("   - Escribe 'speed <valor>' para cambiar velocidad (ej: speed 0.05)")
    print()

    # Buscar dispositivo
    print("🔌 Conectando con dispositivo iMouse...")
    devices = hid.HidDeviceFilter(vendor_id=VENDOR_ID, product_id=PRODUCT_ID).get_devices()

    if not devices:
        print(f"❌ Dispositivo no encontrado: 0x{VENDOR_ID:04x}:0x{PRODUCT_ID:04x}")
        print("   Asegúrate de que el dispositivo esté conectado")
        input("\nPresiona ENTER para salir...")
        return

    device = devices[0]

    try:
        device.open()
    except Exception as e:
        print(f"❌ No se pudo abrir el dispositivo: {e}")
        print("   Puede que esté siendo usado por otro programa")
        input("\nPresiona ENTER para salir...")
        return

    print(f"✅ Conectado a: {device.product_name}")
    print(f"   VID: 0x{VENDOR_ID:04x}")
    print(f"   PID: 0x{PRODUCT_ID:04x}")

    # Obtener output report
    out_report = None
    for report in device.find_output_reports():
        out_report = report
        break

    if not out_report:
        print("❌ No se encontró output report")
        device.close()
        input("\nPresiona ENTER para salir...")
        return

    print(f"   Report size: {len(out_report.get_raw_data())} bytes")
    print()
    print("=" * 80)
    print("🚀 ¡Listo! Comienza a escribir:")
    print()

    # Variables de configuración
    typing_delay = 0.03  # Velocidad de escritura por defecto
    total_chars_sent = 0
    total_messages = 0

    try:
        while True:
            # Obtener input del usuario
            try:
                text = input("📝 > ")
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupción detectada")
                break

            # Comandos especiales
            if text.lower() in ['exit', 'salir', 'quit', 'q']:
                print("\n👋 Saliendo...")
                break

            if text.lower() in ['clear', 'cls']:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("⌨️  iMOUSE TYPER - MODO CONTINUO")
                print("=" * 80)
                continue

            if text.lower().startswith('speed '):
                try:
                    new_speed = float(text.split()[1])
                    if 0.001 <= new_speed <= 1.0:
                        typing_delay = new_speed
                        print(f"⚡ Velocidad cambiada a: {typing_delay:.3f}s entre teclas")
                    else:
                        print("❌ La velocidad debe estar entre 0.001 y 1.0")
                except (IndexError, ValueError):
                    print("❌ Uso: speed <valor>  (ej: speed 0.05)")
                continue

            # Ignorar líneas vacías
            if not text.strip():
                continue

            # Enviar el texto
            print(f"   📤 Enviando {len(text)} caracteres...", end='', flush=True)

            sent, errors = send_text_directly(text, device, out_report, typing_delay)

            if sent > 0:
                print(f" ✅ ({sent} teclas enviadas)")
                total_chars_sent += sent
                total_messages += 1
            else:
                print(" ❌ No se pudo enviar")

            if errors > 0:
                print(f"   ⚠️  {errors} caracteres no soportados")

    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

    finally:
        # Cerrar dispositivo
        device.close()

        # Mostrar estadísticas
        print()
        print("=" * 80)
        print("📊 ESTADÍSTICAS DE LA SESIÓN:")
        print(f"   Mensajes enviados:    {total_messages}")
        print(f"   Caracteres enviados:  {total_chars_sent}")
        print("=" * 80)

        input("\nPresiona ENTER para salir...")


if __name__ == "__main__":
    main()