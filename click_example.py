#!/usr/bin/env python3
"""
Ejemplo: Click en posición específica (300px, 300px)
"""

from imouse_hid_protocol import iMouseHIDProtocol, ButtonState

# Crear protocolo con resolución 1920x1080 (ajustar según tu pantalla)
protocol = iMouseHIDProtocol(screen_width=1920, screen_height=1080)

print("=== Click en (300px, 300px) ===\n")

# Paso 1: Mover a la posición
print("Paso 1: Mover mouse a (300, 300)")
move_packet = protocol.move_absolute(300, 300)
print(protocol.format_packet_detailed(move_packet))
print()

# Paso 2: Click izquierdo (down)
print("Paso 2: Presionar botón izquierdo")
down_packet = protocol.left_down()
print(protocol.format_packet_detailed(down_packet))
print()

# Paso 3: Esperar (50-80ms en el código real)
print("Paso 3: Esperar 50-80ms (simulado)")
print()

# Paso 4: Soltar botón (up)
print("Paso 4: Soltar botón izquierdo")
up_packet = protocol.left_up()
print(protocol.format_packet_detailed(up_packet))
print()

print("=" * 50)
print("\nSECUENCIA COMPLETA DE PAQUETES:\n")
print(f"1. MOVE:  {protocol.format_packet_hex(move_packet)}")
print(f"2. DOWN:  {protocol.format_packet_hex(down_packet)}")
print(f"   (esperar 50-80ms)")
print(f"3. UP:    {protocol.format_packet_hex(up_packet)}")
print()

# Guardar paquetes en formato para análisis
print("=" * 50)
print("\nPAQUETES EN FORMATO HEXADECIMAL PURO:\n")
print("Paquete 1 (MOVE):")
print(" ".join(f"0x{b:02x}" for b in move_packet))
print()
print("Paquete 2 (DOWN):")
print(" ".join(f"0x{b:02x}" for b in down_packet))
print()
print("Paquete 3 (UP):")
print(" ".join(f"0x{b:02x}" for b in up_packet))
