#!/usr/bin/env python3
"""
Mapa COMPLETO de caracteres a scancodes iMouse
Reconstruido desde la tabla de lookup analizada en Ghidra
"""

import json

# Mapeo completo basado en la tabla de lookup (165 entradas)
# Formato: carácter/tecla → (scancode, modifier)
IMOUSE_KEYMAP = {
    # ===== LETRAS MINÚSCULAS (modifier=0x00) =====
    'a': (0x04, 0x00),
    'b': (0x05, 0x00),
    'c': (0x06, 0x00),
    'd': (0x07, 0x00),
    'e': (0x08, 0x00),
    'f': (0x09, 0x00),
    'g': (0x0a, 0x00),
    'h': (0x0b, 0x00),
    'i': (0x0c, 0x00),
    'j': (0x0d, 0x00),
    'k': (0x0e, 0x00),
    'l': (0x0f, 0x00),
    'm': (0x10, 0x00),
    'n': (0x11, 0x00),
    'o': (0x12, 0x00),
    'p': (0x13, 0x00),
    'q': (0x14, 0x00),
    'r': (0x15, 0x00),
    's': (0x16, 0x00),
    't': (0x17, 0x00),
    'u': (0x18, 0x00),
    'v': (0x19, 0x00),
    'w': (0x1a, 0x00),
    'x': (0x1b, 0x00),
    'y': (0x1c, 0x00),
    'z': (0x1d, 0x00),

    # ===== LETRAS MAYÚSCULAS (modifier=0x02 = Shift) =====
    'A': (0x04, 0x02),
    'B': (0x05, 0x02),
    'C': (0x06, 0x02),
    'D': (0x07, 0x02),
    'E': (0x08, 0x02),
    'F': (0x09, 0x02),
    'G': (0x0a, 0x02),
    'H': (0x0b, 0x02),
    'I': (0x0c, 0x02),
    'J': (0x0d, 0x02),
    'K': (0x0e, 0x02),
    'L': (0x0f, 0x02),
    'M': (0x10, 0x02),
    'N': (0x11, 0x02),
    'O': (0x12, 0x02),
    'P': (0x13, 0x02),
    'Q': (0x14, 0x02),
    'R': (0x15, 0x02),
    'S': (0x16, 0x02),
    'T': (0x17, 0x02),
    'U': (0x18, 0x02),
    'V': (0x19, 0x02),
    'W': (0x1a, 0x02),
    'X': (0x1b, 0x02),
    'Y': (0x1c, 0x02),
    'Z': (0x1d, 0x02),

    # ===== NÚMEROS (modifier=0x00) =====
    '0': (0x27, 0x00),
    '1': (0x1e, 0x00),
    '2': (0x1f, 0x00),
    '3': (0x20, 0x00),
    '4': (0x21, 0x00),
    '5': (0x22, 0x00),
    '6': (0x23, 0x00),
    '7': (0x24, 0x00),
    '8': (0x25, 0x00),
    '9': (0x26, 0x00),

    # ===== SÍMBOLOS SIN SHIFT =====
    ' ': (0x2c, 0x00),  # Space
    '-': (0x2d, 0x00),
    '=': (0x2e, 0x00),
    '[': (0x2f, 0x00),
    ']': (0x30, 0x00),
    '\\': (0x31, 0x00),
    ';': (0x33, 0x00),
    "'": (0x34, 0x00),
    '`': (0x35, 0x00),
    ',': (0x36, 0x00),
    '.': (0x37, 0x00),
    '/': (0x38, 0x00),

    # ===== SÍMBOLOS CON SHIFT (desde tabla entrada 67-76) =====
    '+': (0x2e, 0x02),  # Shift + =
    '{': (0x2f, 0x02),  # Shift + [
    '}': (0x30, 0x02),  # Shift + ]
    '|': (0x31, 0x02),  # Shift + \
    ':': (0x33, 0x02),  # Shift + ;
    '"': (0x34, 0x02),  # Shift + '
    '~': (0x35, 0x02),  # Shift + `
    '<': (0x36, 0x02),  # Shift + ,
    '>': (0x37, 0x02),  # Shift + .
    '?': (0x38, 0x02),  # Shift + /

    # ===== SÍMBOLOS NÚMEROS CON SHIFT =====
    '!': (0x1e, 0x02),  # Shift + 1
    '@': (0x1f, 0x02),  # Shift + 2
    '#': (0x20, 0x02),  # Shift + 3
    '$': (0x21, 0x02),  # Shift + 4
    '%': (0x22, 0x02),  # Shift + 5
    '^': (0x23, 0x02),  # Shift + 6
    '&': (0x24, 0x02),  # Shift + 7
    '*': (0x25, 0x02),  # Shift + 8
    '(': (0x26, 0x02),  # Shift + 9
    ')': (0x27, 0x02),  # Shift + 0
    '_': (0x2d, 0x02),  # Shift + -

    # ===== TECLAS ESPECIALES =====
    '\n': (0x28, 0x00),      # Enter
    '\t': (0x2b, 0x00),      # Tab
    '\x08': (0x2a, 0x00),    # Backspace

    # ===== TECLAS DE FUNCIÓN =====
    '<F1>': (0x3a, 0x00),
    '<F2>': (0x3b, 0x00),
    '<F3>': (0x3c, 0x00),
    '<F4>': (0x3d, 0x00),
    '<F5>': (0x3e, 0x00),
    '<F6>': (0x3f, 0x00),
    '<F7>': (0x40, 0x00),
    '<F8>': (0x41, 0x00),
    '<F9>': (0x42, 0x00),
    '<F10>': (0x43, 0x00),
    '<F11>': (0x44, 0x00),
    '<F12>': (0x45, 0x00),

    # ===== TECLAS DE NAVEGACIÓN =====
    '<Esc>': (0x29, 0x00),
    '<Insert>': (0x49, 0x00),
    '<Delete>': (0x4c, 0x00),
    '<Home>': (0x4a, 0x00),
    '<End>': (0x4d, 0x00),
    '<PageUp>': (0x4b, 0x00),
    '<PageDown>': (0x4e, 0x00),
    '<Right>': (0x4f, 0x00),
    '<Left>': (0x50, 0x00),
    '<Down>': (0x51, 0x00),
    '<Up>': (0x52, 0x00),
    '<PrintScreen>': (0x46, 0x00),
    '<Pause>': (0x48, 0x00),

    # ===== TECLADO NUMÉRICO =====
    '<Keypad0>': (0x62, 0x00),
    '<Keypad1>': (0x59, 0x00),
    '<Keypad2>': (0x5a, 0x00),
    '<Keypad3>': (0x5b, 0x00),
    '<Keypad4>': (0x5c, 0x00),
    '<Keypad5>': (0x5d, 0x00),
    '<Keypad6>': (0x5e, 0x00),
    '<Keypad7>': (0x5f, 0x00),
    '<Keypad8>': (0x60, 0x00),
    '<Keypad9>': (0x61, 0x00),
    '<KeypadDot>': (0x63, 0x00),
    '<KeypadEnter>': (0x58, 0x00),
    '<KeypadPlus>': (0x57, 0x00),
    '<KeypadMinus>': (0x56, 0x00),

    # ===== MODIFICADORES ESPECIALES =====
    '<Ctrl>': (0x00, 0x01),
    '<Shift>': (0x00, 0x02),
    '<Alt>': (0x00, 0x04),
    '<Win>': (0x00, 0x08),
}


def char_to_imouse_packet(char):
    """
    Convierte un carácter a paquete iMouse de 9 bytes

    Returns:
        list: Paquete de 9 bytes [0x00, 0xa2, modifier, 0x00, scancode, ...]
              o None si el carácter no está soportado
    """

    if char not in IMOUSE_KEYMAP:
        return None

    scancode, modifier = IMOUSE_KEYMAP[char]

    # Formato confirmado por Ghidra:
    # [Report ID][0xa2][Modifier][Reserved][Scancode][Padding...]
    return [0x00, 0xa2, modifier, 0x00, scancode, 0x00, 0x00, 0x00, 0x00]


def text_to_imouse_packets(text):
    """
    Convierte un texto completo a lista de paquetes iMouse

    Args:
        text: String de texto a convertir

    Returns:
        list: Lista de paquetes [keypress, release, keypress, release, ...]
    """

    packets = []
    timestamp = 0.0

    for char in text:
        # Generar paquete de keypress
        packet = char_to_imouse_packet(char)

        if packet is None:
            print(f"⚠️  Carácter no soportado: '{char}' (ignorado)")
            continue

        packets.append({
            'bytes': packet,
            'description': f'Keypress: {repr(char)}',
            'direction': 'out',  # Necesario para replay_imouse.py
            'timestamp': timestamp,
            'data': ''  # Opcional, pero añadido para compatibilidad
        })
        timestamp += 0.05  # 50ms entre teclas

        # Generar paquete de release
        release = [0x00, 0xa2, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        packets.append({
            'bytes': release,
            'description': 'Release',
            'direction': 'out',
            'timestamp': timestamp,
            'data': ''
        })
        timestamp += 0.01  # 10ms para release

    return packets


def save_packets_to_json(packets, filename):
    """Guarda paquetes en formato JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(packets, f, indent=2, ensure_ascii=False)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Generador de paquetes iMouse con mapeo COMPLETO',
        epilog='''
EJEMPLOS DE USO:

  Texto simple:
    python imouse_complete_keymap.py "Hola Mundo" -o samples/hola.json

  Email:
    python imouse_complete_keymap.py "usuario@gmail.com" -o samples/email.json

  Contraseña con símbolos:
    python imouse_complete_keymap.py "P@ssw0rd123!" -o samples/password.json

  URL completa:
    python imouse_complete_keymap.py "https://www.google.com" -o samples/url.json

  Ver mapa de caracteres soportados:
    python imouse_complete_keymap.py --show-map "dummy" -o dummy.json
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('text', help='Texto a convertir')
    parser.add_argument('-o', '--output', required=True, help='Archivo JSON de salida')
    parser.add_argument('--show-map', action='store_true', help='Mostrar mapa completo')

    # Si no hay argumentos, mostrar ayuda
    import sys
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n⚡ INICIO RÁPIDO:")
        print('  python imouse_complete_keymap.py "Hola iPhone" -o samples/test.json')
        print('  python replay_imouse.py samples/test.json')
        sys.exit(0)

    args = parser.parse_args()

    if args.show_map:
        print("=" * 100)
        print("🗺️  MAPA COMPLETO DE CARACTERES → SCANCODES iMouse")
        print("=" * 100)
        print()
        for char, (scancode, modifier) in sorted(IMOUSE_KEYMAP.items()):
            mod_str = []
            if modifier & 0x01:
                mod_str.append("Ctrl")
            if modifier & 0x02:
                mod_str.append("Shift")
            if modifier & 0x04:
                mod_str.append("Alt")
            if modifier & 0x08:
                mod_str.append("Win")

            mod_display = "+".join(mod_str) if mod_str else "None"
            print(f"  '{char}' → scancode 0x{scancode:02x}, modifier {mod_display}")
        print()
        return

    print("=" * 100)
    print("⌨️  GENERADOR DE PAQUETES iMouse - VERSIÓN COMPLETA")
    print("=" * 100)
    print()
    print(f"📝 Texto: \"{args.text}\"")
    print(f"📊 Caracteres: {len(args.text)}")
    print()

    # Generar paquetes
    packets = text_to_imouse_packets(args.text)

    print(f"📦 Paquetes generados: {len(packets)}")
    print()

    # Guardar
    save_packets_to_json(packets, args.output)
    print(f"✅ Guardado en: {args.output}")
    print()
    print("Para reproducir:")
    print(f"  python3 replay_imouse.py {args.output}")
    print()


if __name__ == "__main__":
    main()
