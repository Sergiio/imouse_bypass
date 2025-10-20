#!/usr/bin/env python3
"""
Inyección DIRECTA de teclas en Windows sin usar USB
Alternativa cuando iMouseSrv.exe no está corriendo
"""

import sys
import time
import json

try:
    import ctypes
    from ctypes import wintypes
except ImportError:
    print("❌ Este script solo funciona en Windows")
    sys.exit(1)

# Constantes de Windows
KEYEVENTF_KEYUP = 0x0002
VK_SHIFT = 0x10

# Mapeo de scancodes HID a Virtual Key Codes de Windows
HID_TO_VK = {
    0x04: 0x41,  # A
    0x05: 0x42,  # B
    0x06: 0x43,  # C
    0x07: 0x44,  # D
    0x08: 0x45,  # E
    0x09: 0x46,  # F
    0x0a: 0x47,  # G
    0x0b: 0x48,  # H
    0x0c: 0x49,  # I
    0x0d: 0x4A,  # J
    0x0e: 0x4B,  # K
    0x0f: 0x4C,  # L
    0x10: 0x4D,  # M
    0x11: 0x4E,  # N
    0x12: 0x4F,  # O
    0x13: 0x50,  # P
    0x14: 0x51,  # Q
    0x15: 0x52,  # R
    0x16: 0x53,  # S
    0x17: 0x54,  # T
    0x18: 0x55,  # U
    0x19: 0x56,  # V
    0x1a: 0x57,  # W
    0x1b: 0x58,  # X
    0x1c: 0x59,  # Y
    0x1d: 0x5A,  # Z
    0x1e: 0x31,  # 1
    0x1f: 0x32,  # 2
    0x20: 0x33,  # 3
    0x21: 0x34,  # 4
    0x22: 0x35,  # 5
    0x23: 0x36,  # 6
    0x24: 0x37,  # 7
    0x25: 0x38,  # 8
    0x26: 0x39,  # 9
    0x27: 0x30,  # 0
    0x28: 0x0D,  # Enter
    0x2c: 0x20,  # Space
}

# Cargar user32.dll
user32 = ctypes.WinDLL('user32', use_last_error=True)

def press_key(vk_code, modifier=0x00):
    """Presiona y suelta una tecla"""

    # Presionar Shift si es necesario
    if modifier & 0x02:  # Left Shift
        user32.keybd_event(VK_SHIFT, 0, 0, 0)
        time.sleep(0.01)

    # Presionar tecla
    user32.keybd_event(vk_code, 0, 0, 0)
    time.sleep(0.05)

    # Soltar tecla
    user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.01)

    # Soltar Shift si fue presionado
    if modifier & 0x02:
        user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.01)


def inject_from_json(json_file, delay_ms=50):
    """Lee un JSON de capturas e inyecta las teclas directamente"""

    print("=" * 80)
    print("⌨️  INYECCIÓN DIRECTA DE TECLADO (Windows API)")
    print("=" * 80)
    print()

    # Cargar JSON
    try:
        with open(json_file, 'r') as f:
            packets = json.load(f)
    except Exception as e:
        print(f"❌ Error al cargar JSON: {e}")
        return False

    print(f"📂 Archivo: {json_file}")
    print(f"📦 Total paquetes: {len(packets)}")
    print()

    # Filtrar solo keypresses (ignorar releases)
    keypresses = []
    for p in packets:
        data = p.get('bytes', [])
        if len(data) >= 5:
            # Formato: [0x00][0xa2][modifier][reserved][scancode]...
            # Nota: También acepta 0xa1 por compatibilidad
            if data[0] == 0x00 and (data[1] == 0xa2 or data[1] == 0xa1):
                modifier = data[2]
                scancode = data[4]

                if scancode != 0x00:  # Es un keypress, no un release
                    keypresses.append({
                        'scancode': scancode,
                        'modifier': modifier,
                        'description': p.get('description', '')
                    })

    print(f"⌨️  Teclas a inyectar: {len(keypresses)}")
    print()
    print("⚠️  IMPORTANTE:")
    print("   1. Pon el cursor en el Notepad o donde quieras escribir")
    print("   2. Tienes 3 segundos para cambiar de ventana")
    print()

    for i in range(3, 0, -1):
        print(f"   Comenzando en {i}...")
        time.sleep(1)

    print()
    print("⌨️  INYECTANDO TECLAS...")
    print("=" * 80)

    injected = 0
    for i, key in enumerate(keypresses, 1):
        scancode = key['scancode']
        modifier = key['modifier']
        desc = key['description']

        # Convertir scancode HID a Virtual Key Code
        vk_code = HID_TO_VK.get(scancode)

        if vk_code is None:
            print(f"  [{i:3d}] ⚠️  Scancode 0x{scancode:02x} no soportado")
            continue

        # Inyectar tecla
        press_key(vk_code, modifier)
        injected += 1

        print(f"  [{injected:3d}] ✓ Scancode 0x{scancode:02x} → VK 0x{vk_code:02x}  # {desc}")

        # Delay entre teclas
        time.sleep(delay_ms / 1000.0)

    print()
    print("=" * 80)
    print(f"✅ INYECCIÓN COMPLETADA: {injected} teclas")
    print("=" * 80)

    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Inyecta teclas directamente en Windows sin usar USB',
        epilog='Ejemplo: python inject_keyboard_direct.py test_hola_imouse.json'
    )

    parser.add_argument('json_file', help='Archivo JSON con las capturas')
    parser.add_argument('-d', '--delay', type=int, default=50,
                        help='Delay entre teclas en ms (default: 50)')

    args = parser.parse_args()

    inject_from_json(args.json_file, args.delay)


if __name__ == "__main__":
    main()
