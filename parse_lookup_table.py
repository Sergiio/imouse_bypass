#!/usr/bin/env python3
"""
Parser de la tabla de lookup de caracteres de iMouse
Extrae la estructura: [ptr_string][ptr_data][modifier][scancode]
"""

import struct

# Dump hexadecimal de la tabla (0x1001901c - 0x10019a7c)
HEX_DUMP = """
a8 55 01 10 b4 55 01 10 00 00 00 00 02 00 00 00 c4 55 01 10 d0 55 01 10 00 00 00 00 03 00 00 00 e0 55 01 10 ec 55 01 10 00 00 00 00 04 00 00 00 fc 55 01 10 08 56 01 10 00 00 00 00 2a 00 00 00 18 56 01 10 24 56 01 10 00 00 00 00 2b 00 00 00 34 56 01 10 38 56 01 10 00 00 00 00 00 00 00 00 48 56 01 10 4c 56 01 10 08 00 00 00 28 00 00 00 5c 56 01 10 64 56 01 10 00 00 00 00 00 00 00 00 74 56 01 10 7c 56 01 10 02 00 00 00 00 00 00 00 8c 56 01 10 94 56 01 10 01 00 00 00 00 00 00 00 a4 56 01 10 a8 56 01 10 04 00 00 00 14 00 00 00 b8 56 01 10 c4 56 01 10 00 00 00 00 29 00 00 00 d4 56 01 10 d8 56 01 10 00 00 00 00 4b 00 00 00 e8 56 01 10 f0 56 01 10 00 00 00 00 4e 00 00 00 00 57 01 10 0c 57 01 10 00 00 00 00 4d 00 00 00 1c 57 01 10 20 57 01 10 00 00 00 00 4a 00 00 00 30 57 01 10 38 57 01 10 00 00 00 00 48 00 00 00 48 57 01 10 50 57 01 10 00 00 00 00 49 00 00 00 60 57 01 10 68 57 01 10 00 00 00 00 4c 00 00 00 78 57 01 10 80 57 01 10 00 00 00 00 4f 00 00 00 90 57 01 10 9c 57 01 10 00 00 00 00 50 00 00 00 a4 57 01 10 b0 57 01 10 00 00 00 00 51 00 00 00 b8 57 01 10 c4 57 01 10 00 00 00 00 52 00 00 00 cc 57 01 10 d4 57 01 10 00 00 00 00 29 00 00 00 dc 57 01 10 e4 57 01 10 00 00 00 00 46 00 00 00 f4 57 01 10 00 58 01 10 00 00 00 00 2b 00 00 00 10 58 01 10 18 58 01 10 00 00 00 00 2c 00 00 00 28 58 01 10 34 58 01 10 00 00 00 00 2f 00 00 00 44 58 01 10 4c 58 01 10 00 00 00 00 90 00 00 00 5c 58 01 10 64 58 01 10 00 00 00 00 2c 00 00 00 74 58 01 10 78 58 01 10 00 00 00 00 04 00 00 00 88 58 01 10 8c 58 01 10 00 00 00 00 05 00 00 00 9c 58 01 10 a0 58 01 10 00 00 00 00 06 00 00 00 b0 58 01 10 b4 58 01 10 00 00 00 00 07 00 00 00 c4 58 01 10 c8 58 01 10 00 00 00 00 08 00 00 00 d8 58 01 10 dc 58 01 10 00 00 00 00 09 00 00 00 ec 58 01 10 f0 58 01 10 00 00 00 00 0a 00 00 00 00 59 01 10 04 59 01 10 00 00 00 00 0b 00 00 00 14 59 01 10 18 59 01 10 00 00 00 00 0c 00 00 00 28 59 01 10 2c 59 01 10 00 00 00 00 0d 00 00 00 3c 59 01 10 40 59 01 10 00 00 00 00 0e 00 00 00 50 59 01 10 54 59 01 10 00 00 00 00 0f 00 00 00 64 59 01 10 68 59 01 10 00 00 00 00 10 00 00 00 78 59 01 10 7c 59 01 10 00 00 00 00 11 00 00 00 8c 59 01 10 90 59 01 10 00 00 00 00 12 00 00 00 a0 59 01 10 a4 59 01 10 00 00 00 00 13 00 00 00 b4 59 01 10 b8 59 01 10 00 00 00 00 14 00 00 00 c8 59 01 10 cc 59 01 10 00 00 00 00 15 00 00 00 dc 59 01 10 e0 59 01 10 00 00 00 00 16 00 00 00 f0 59 01 10 f4 59 01 10 00 00 00 00 17 00 00 00 04 5a 01 10 08 5a 01 10 00 00 00 00 18 00 00 00 18 5a 01 10 1c 5a 01 10 00 00 00 00 19 00 00 00 2c 5a 01 10 30 5a 01 10 00 00 00 00 1a 00 00 00 40 5a 01 10 44 5a 01 10 00 00 00 00 1b 00 00 00 54 5a 01 10 58 5a 01 10 00 00 00 00 1c 00 00 00 68 5a 01 10 6c 5a 01 10 00 00 00 00 1d 00 00 00 7c 5a 01 10 80 5a 01 10 00 00 00 00 27 00 00 00 90 5a 01 10 94 5a 01 10 00 00 00 00 1e 00 00 00 a4 5a 01 10 a8 5a 01 10 00 00 00 00 1f 00 00 00 b8 5a 01 10 bc 5a 01 10 00 00 00 00 20 00 00 00 cc 5a 01 10 d0 5a 01 10 00 00 00 00 21 00 00 00 e0 5a 01 10 e4 5a 01 10 00 00 00 00 22 00 00 00 f4 5a 01 10 f8 5a 01 10 00 00 00 00 23 00 00 00 08 5b 01 10 0c 5b 01 10 00 00 00 00 24 00 00 00 1c 5b 01 10 20 5b 01 10 00 00 00 00 25 00 00 00 30 5b 01 10 34 5b 01 10 00 00 00 00 26 00 00 00 44 5b 01 10 48 5b 01 10 00 00 00 00 2d 00 00 00 58 5b 01 10 5c 5b 01 10 02 00 00 00 2e 00 00 00 10 55 01 10 5c 5b 01 10 02 00 00 00 2f 00 00 00 6c 5b 01 10 5c 5b 01 10 02 00 00 00 30 00 00 00 70 5b 01 10 5c 5b 01 10 02 00 00 00 31 00 00 00 84 54 01 10 5c 5b 01 10 02 00 00 00 33 00 00 00 74 5b 01 10 5c 5b 01 10 02 00 00 00 34 00 00 00 78 5b 01 10 5c 5b 01 10 02 00 00 00 35 00 00 00 7c 5b 01 10 5c 5b 01 10 02 00 00 00 36 00 00 00 80 5b 01 10 5c 5b 01 10 02 00 00 00 37 00 00 00 84 5b 01 10 5c 5b 01 10 02 00 00 00 38 00 00 00 88 5b 01 10 5c 5b 01 10 02 00 00 00 04 00 00 00 8c 5b 01 10 8c 58 01 10 02 00 00 00 05 00 00 00 90 5b 01 10 a0 58 01 10 02 00 00 00 06 00 00 00 94 5b 01 10 b4 58 01 10 02 00 00 00 07 00 00 00 98 5b 01 10 c8 58 01 10 02 00 00 00 08 00 00 00 9c 5b 01 10 dc 58 01 10 02 00 00 00 09 00 00 00 a0 5b 01 10 f0 58 01 10 02 00 00 00 0a 00 00 00 a4 5b 01 10 04 59 01 10 02 00 00 00 0b 00 00 00 a8 5b 01 10 18 59 01 10 02 00 00 00 0c 00 00 00 ac 5b 01 10 2c 59 01 10 02 00 00 00 0d 00 00 00 b0 5b 01 10 40 59 01 10 02 00 00 00 0e 00 00 00 b4 5b 01 10 54 59 01 10 02 00 00 00 0f 00 00 00 b8 5b 01 10 68 59 01 10 02 00 00 00 10 00 00 00 bc 5b 01 10 7c 59 01 10 02 00 00 00 11 00 00 00 c0 5b 01 10 90 59 01 10 02 00 00 00 12 00 00 00 c4 5b 01 10 a4 59 01 10 02 00 00 00 13 00 00 00 c8 5b 01 10 b8 59 01 10 02 00 00 00 14 00 00 00 cc 5b 01 10 cc 59 01 10 02 00 00 00 15 00 00 00 d0 5b 01 10 e0 59 01 10 02 00 00 00 16 00 00 00 d4 5b 01 10 f4 59 01 10 02 00 00 00 17 00 00 00 d8 5b 01 10 08 5a 01 10 02 00 00 00 18 00 00 00 dc 5b 01 10 1c 5a 01 10 02 00 00 00 19 00 00 00 e0 5b 01 10 30 5a 01 10 02 00 00 00 1a 00 00 00 e4 5b 01 10 44 5a 01 10 02 00 00 00 1b 00 00 00 e8 5b 01 10 58 5a 01 10 02 00 00 00 1c 00 00 00 ec 5b 01 10 6c 5a 01 10 02 00 00 00 1d 00 00 00 f0 5b 01 10 80 5a 01 10 02 00 00 00 1e 00 00 00 f4 5b 01 10 a8 5a 01 10 02 00 00 00 1f 00 00 00 f8 5b 01 10 bc 5a 01 10 02 00 00 00 20 00 00 00 fc 5b 01 10 d0 5a 01 10 02 00 00 00 21 00 00 00 00 5c 01 10 e4 5a 01 10 02 00 00 00 22 00 00 00 04 5c 01 10 f8 5a 01 10 02 00 00 00 23 00 00 00 08 5c 01 10 0c 5b 01 10 02 00 00 00 24 00 00 00 0c 5c 01 10 20 5b 01 10 02 00 00 00 25 00 00 00 10 5c 01 10 34 5b 01 10 02 00 00 00 26 00 00 00 14 5c 01 10 48 5b 01 10 02 00 00 00 27 00 00 00 18 5c 01 10 94 5a 01 10 02 00 00 00 2d 00 00 00 1c 5c 01 10 5c 5b 01 10 00 00 00 00 2e 00 00 00 20 5c 01 10 5c 5b 01 10 00 00 00 00 2f 00 00 00 24 5c 01 10 5c 5b 01 10 00 00 00 00 30 00 00 00 28 5c 01 10 5c 5b 01 10 00 00 00 00 32 00 00 00 2c 5c 01 10 5c 5b 01 10 00 00 00 00 33 00 00 00 30 5c 01 10 38 5c 01 10 00 00 00 00 35 00 00 00 48 5c 01 10 5c 5b 01 10 00 00 00 00 36 00 00 00 e4 54 01 10 5c 5b 01 10 00 00 00 00 37 00 00 00 4c 5c 01 10 50 5c 01 10 00 00 00 00 38 00 00 00 5c 5c 01 10 60 5c 01 10 00 00 00 00 60 00 00 00 90 5a 01 10 6c 5c 01 10 00 00 00 00 61 00 00 00 a4 5a 01 10 7c 5c 01 10 00 00 00 00 62 00 00 00 b8 5a 01 10 8c 5c 01 10 00 00 00 00 63 00 00 00 cc 5a 01 10 9c 5c 01 10 00 00 00 00 64 00 00 00 e0 5a 01 10 ac 5c 01 10 00 00 00 00 65 00 00 00 f4 5a 01 10 bc 5c 01 10 00 00 00 00 66 00 00 00 08 5b 01 10 cc 5c 01 10 00 00 00 00 67 00 00 00 1c 5b 01 10 dc 5c 01 10 00 00 00 00 68 00 00 00 30 5b 01 10 ec 5c 01 10 00 00 00 00 69 00 00 00 44 5b 01 10 fc 5c 01 10 00 00 00 00 6a 00 00 00 10 5c 01 10 0c 5d 01 10 00 00 00 00 6b 00 00 00 10 55 01 10 1c 5d 01 10 00 00 00 00 6c 00 00 00 74 58 01 10 2c 5d 01 10 00 00 00 00 6d 00 00 00 1c 5c 01 10 3c 5d 01 10 00 00 00 00 6e 00 00 00 4c 5c 01 10 4c 5d 01 10 00 00 00 00 6f 00 00 00 5c 5c 01 10 5c 5d 01 10 00 00 00 00 3a 00 00 00 6c 5d 01 10 70 5d 01 10 00 00 00 00 3b 00 00 00 80 5d 01 10 84 5d 01 10 00 00 00 00 3c 00 00 00 94 5d 01 10 98 5d 01 10 00 00 00 00 3d 00 00 00 a8 5d 01 10 ac 5d 01 10 00 00 00 00 3e 00 00 00 bc 5d 01 10 c0 5d 01 10 00 00 00 00 3f 00 00 00 d0 5d 01 10 d4 5d 01 10 00 00 00 00 40 00 00 00 e4 5d 01 10 e8 5d 01 10 00 00 00 00 41 00 00 00 f8 5d 01 10 fc 5d 01 10 00 00 00 00 42 00 00 00 0c 5e 01 10 10 5e 01 10 00 00 00 00 43 00 00 00 20 5e 01 10 24 5e 01 10 00 00 00 00 44 00 00 00 34 5e 01 10 38 5e 01 10 00 00 00 00 45 00 00 00 48 5e 01 10 4c 5e 01 10 00 00 00 00 68 00 00 00 5c 5e 01 10 60 5e 01 10 00 00 00 00 69 00 00 00 70 5e 01 10 74 5e 01 10 00 00 00 00 6a 00 00 00 84 5e 01 10 88 5e 01 10 00 00 00 00 6b 00 00 00 98 5e 01 10 9c 5e 01 10 00 00 00 00 6c 00 00 00 ac 5e 01 10 b0 5e 01 10 00 00 00 00 6d 00 00 00 b8 5e 01 10 9c 5e 01 10 00 00 00 00 6e 00 00 00 bc 5e 01 10 9c 5e 01 10 00 00 00 00 6f 00 00 00 c0 5e 01 10 9c 5e 01 10 00 00 00 00 70 00 00 00 c4 5e 01 10 9c 5e 01 10 00 00 00 00 71 00 00 00 c8 5e 01 10 9c 5e 01 10 00 00 00 00 72 00 00 00 cc 5e 01 10 9c 5e 01 10 00 00 00 00 73 00 00 00 d0 5e 01 10 9c 5e 01 10 00 00 00 00 01 02 00 00 d4 5e 01 10 d4 5e 01 10 02 00 00 00 00 00 00 00
"""


def parse_table():
    """Parsea el dump hexadecimal de la tabla"""

    # Limpiar y convertir hex a bytes
    hex_clean = HEX_DUMP.replace('\n', ' ').strip()
    hex_bytes = bytes.fromhex(hex_clean)

    print("=" * 100)
    print("🔬 PARSER DE TABLA DE LOOKUP - iMouse")
    print("=" * 100)
    print()
    print(f"📊 Tamaño total: {len(hex_bytes)} bytes")
    print(f"📦 Entradas: {len(hex_bytes) // 16}")
    print()

    entries = []

    # Cada entrada son 16 bytes (4 dwords)
    for i in range(0, len(hex_bytes), 16):
        if i + 16 > len(hex_bytes):
            break

        chunk = hex_bytes[i:i+16]

        # Parsear 4 dwords (little endian)
        ptr_string = struct.unpack('<I', chunk[0:4])[0]
        ptr_data = struct.unpack('<I', chunk[4:8])[0]
        modifier = struct.unpack('<I', chunk[8:12])[0]
        scancode = struct.unpack('<I', chunk[12:16])[0]

        entry = {
            'index': len(entries),
            'ptr_string': ptr_string,
            'ptr_data': ptr_data,
            'modifier': modifier,
            'scancode': scancode,
        }

        entries.append(entry)

    return entries


def print_entries(entries):
    """Imprime las entradas parseadas"""

    print("=" * 100)
    print("📋 ENTRADAS DE LA TABLA DE LOOKUP")
    print("=" * 100)
    print()
    print(f"{'#':<4} {'Ptr String':<12} {'Ptr Data':<12} {'Modifier':<10} {'Scancode':<10} {'Notes'}")
    print("-" * 100)

    for e in entries:
        # Decodificar el modificador
        mod_str = []
        if e['modifier'] == 0x00:
            mod_str.append("None")
        if e['modifier'] & 0x01:
            mod_str.append("Ctrl")
        if e['modifier'] & 0x02:
            mod_str.append("Shift")
        if e['modifier'] & 0x04:
            mod_str.append("Alt")
        if e['modifier'] & 0x08:
            mod_str.append("Win/Cmd")

        mod_display = "+".join(mod_str) if mod_str else f"0x{e['modifier']:02x}"

        # Intentar identificar el scancode
        scancode_name = get_scancode_name(e['scancode'])

        notes = ""
        if e['scancode'] == 0x00:
            notes = "⚠️ Release/Empty"

        print(f"{e['index']:<4} 0x{e['ptr_string']:08x}   0x{e['ptr_data']:08x}   "
              f"{mod_display:<10} 0x{e['scancode']:02x} ({scancode_name:<10})  {notes}")

    print()
    print("=" * 100)


def get_scancode_name(scancode):
    """Convierte scancode HID a nombre de tecla"""

    HID_MAP = {
        0x00: "None",
        0x02: "F1", 0x03: "F2", 0x04: "F3", 0x05: "F4",
        0x06: "F5", 0x07: "F6", 0x08: "F7", 0x09: "F8",
        0x0a: "F9", 0x0b: "F10", 0x0c: "F11", 0x0d: "F12",
        0x04: "a", 0x05: "b", 0x06: "c", 0x07: "d",
        0x08: "e", 0x09: "f", 0x0a: "g", 0x0b: "h",
        0x0c: "i", 0x0d: "j", 0x0e: "k", 0x0f: "l",
        0x10: "m", 0x11: "n", 0x12: "o", 0x13: "p",
        0x14: "q", 0x15: "r", 0x16: "s", 0x17: "t",
        0x18: "u", 0x19: "v", 0x1a: "w", 0x1b: "x",
        0x1c: "y", 0x1d: "z",
        0x1e: "1", 0x1f: "2", 0x20: "3", 0x21: "4",
        0x22: "5", 0x23: "6", 0x24: "7", 0x25: "8",
        0x26: "9", 0x27: "0",
        0x28: "Enter", 0x29: "Esc", 0x2a: "Backspace",
        0x2b: "Tab", 0x2c: "Space", 0x2d: "-", 0x2e: "=",
        0x2f: "[", 0x30: "]", 0x31: "\\", 0x33: ";",
        0x34: "'", 0x35: "`", 0x36: ",", 0x37: ".",
        0x38: "/",
        0x3a: "F1", 0x3b: "F2", 0x3c: "F3", 0x3d: "F4",
        0x3e: "F5", 0x3f: "F6", 0x40: "F7", 0x41: "F8",
        0x42: "F9", 0x43: "F10", 0x44: "F11", 0x45: "F12",
        0x46: "PrtScn", 0x48: "Pause", 0x49: "Insert",
        0x4a: "Home", 0x4b: "PageUp", 0x4c: "Delete",
        0x4d: "End", 0x4e: "PageDown", 0x4f: "Right",
        0x50: "Left", 0x51: "Down", 0x52: "Up",
        0x60: "RightAlt", 0x61: "RightGui", 0x62: "Keypad1",
        0x63: "Keypad2", 0x64: "Keypad3", 0x65: "Keypad4",
        0x66: "Keypad5", 0x67: "Keypad6", 0x68: "Keypad7",
        0x69: "Keypad8", 0x6a: "Keypad9", 0x6b: "Keypad0",
        0x6c: "KeypadDot", 0x6d: "KeypadEnt", 0x6e: "KeypadPlus",
        0x6f: "KeypadMin",
        0x90: "LangKor",
        0x0201: "Ctrl+A?",
    }

    return HID_MAP.get(scancode, "?")


def analyze_patterns(entries):
    """Analiza patrones en la tabla"""

    print()
    print("=" * 100)
    print("🔍 ANÁLISIS DE PATRONES")
    print("=" * 100)
    print()

    # Agrupar por modificador
    by_modifier = {}
    for e in entries:
        mod = e['modifier']
        if mod not in by_modifier:
            by_modifier[mod] = []
        by_modifier[mod].append(e)

    print("📊 Distribución por Modificador:")
    print()
    for mod in sorted(by_modifier.keys()):
        count = len(by_modifier[mod])
        mod_name = []
        if mod == 0x00:
            mod_name.append("None")
        if mod & 0x01:
            mod_name.append("Ctrl")
        if mod & 0x02:
            mod_name.append("Shift")
        if mod & 0x04:
            mod_name.append("Alt")
        if mod & 0x08:
            mod_name.append("Win")

        display = "+".join(mod_name) if mod_name else f"0x{mod:02x}"
        print(f"  {display:<15} : {count:3d} entradas")

    print()
    print("📌 Observaciones:")
    print("  - Muchas entradas con modifier=0x02 (Shift) → Mayúsculas")
    print("  - Entradas con modifier=0x00 → Minúsculas/teclas sin modificador")
    print("  - Algunas entradas especiales con modifier=0x01 (Ctrl), 0x04 (Alt), 0x08 (Win)")
    print()


def main():
    entries = parse_table()
    print_entries(entries)
    analyze_patterns(entries)

    print()
    print("=" * 100)
    print("⚠️  SIGUIENTE PASO NECESARIO")
    print("=" * 100)
    print()
    print("Para completar el mapeo necesitamos los STRINGS apuntados por ptr_string.")
    print()
    print("En Ghidra, por favor extrae los strings de estas direcciones:")
    print()
    print("  Rango aproximado: 0x10015410 - 0x10015ed0")
    print()
    print("Método 1 - Buscar strings:")
    print("  1. Window → Defined Strings")
    print("  2. Filtrar por rango 0x10015400 - 0x10016000")
    print("  3. Copiar toda la lista")
    print()
    print("Método 2 - Exportar memoria:")
    print("  1. Window → Memory Map")
    print("  2. Encontrar sección .rdata o .data")
    print("  3. Export rango 0x10015400 - 0x10016000")
    print()
    print("Con esos strings, podré crear el mapeo completo:")
    print("  'a' → scancode 0x04, modifier 0x00")
    print("  'A' → scancode 0x04, modifier 0x02 (Shift)")
    print("  'F1' → scancode 0x3a, modifier 0x00")
    print("  etc.")
    print()


if __name__ == "__main__":
    main()
