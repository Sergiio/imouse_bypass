#!/usr/bin/env python3
"""
iMouse HID Protocol Generator
Genera paquetes HID para control de mouse basado en ingeniería inversa de MouseKeyItem.dll
"""

import struct
from typing import Tuple, Optional
from enum import IntEnum


class MouseCommand(IntEnum):
    """Comandos HID confirmados"""
    MOVE_ABSOLUTE = 0xa0  # Movimiento absoluto + estado de botón
    MOVE_RELATIVE = 0xa1  # Movimiento relativo + estado de botón
    RESTART = 0xa4        # Comando de restart/reset (HT_Restart)


class ButtonState(IntEnum):
    """Estados de botones (offset 2 en paquetes HID)"""
    NONE = 0              # Sin botón presionado
    LEFT = 1              # Botón izquierdo presionado
    RIGHT = 2             # Botón derecho presionado


class iMouseHIDProtocol:
    """Generador de paquetes HID para iMouse"""

    def __init__(self, screen_width: int = 365, screen_height: int = 667):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_x = 0
        self.current_y = 0
        self.button_state = ButtonState.NONE

    def reset_position(self) -> bytes:
        """
        Genera paquete para resetear posición del mouse a (0,0) usando HT_ResetMousePos

        Envía coordenadas especiales (65535, 65535) = (0xFFFF, 0xFFFF)
        que activan la función de reset en HT_MoveToAA

        Returns:
            bytes: Paquete HID de 9 bytes para reset
        """
        # Coordenadas especiales 0xFFFF = 65535
        # Esto activa FUN_100044b0(param_3) en el código decompilado

        packet = bytearray(9)
        packet[0] = 0x00                              # Padding
        packet[1] = MouseCommand.MOVE_ABSOLUTE        # Comando
        packet[2] = self.button_state                 # Button state
        packet[3] = 0xFF                              # X = 0xFFFF (low byte)
        packet[4] = 0xFF                              # X = 0xFFFF (high byte)
        packet[5] = 0xFF                              # Y = 0xFFFF (low byte)
        packet[6] = 0xFF                              # Y = 0xFFFF (high byte)
        packet[7] = 0x00                              # Padding
        packet[8] = 0x00                              # Padding

        # Resetear tracking interno
        self.current_x = 0
        self.current_y = 0

        return bytes(packet)

    def restart(self) -> bytes:
        """
        Genera paquete de restart usando HT_Restart (comando 0xa4)

        Alternativa al reset_position() usando comando específico 0xa4
        con datos mágicos 0xa4 0xa3

        Returns:
            bytes: Paquete HID de 9 bytes para restart
        """
        packet = bytearray(9)
        packet[0] = 0x00                              # Padding
        packet[1] = MouseCommand.RESTART              # Comando 0xa4
        packet[2] = 0xa4                              # Dato mágico 1
        packet[3] = 0xa3                              # Dato mágico 2
        packet[4] = 0x00                              # Padding
        packet[5] = 0x00                              # Padding
        packet[6] = 0x00                              # Padding
        packet[7] = 0x00                              # Padding
        packet[8] = 0x00                              # Padding

        # Resetear tracking interno
        self.current_x = 0
        self.current_y = 0

        return bytes(packet)

    def move_absolute(self, x: int, y: int, button: Optional[ButtonState] = None) -> bytes:
        """
        Genera paquete de movimiento absoluto (comando 0xa0)

        Args:
            x: Coordenada X en píxeles (0 - screen_width)
            y: Coordenada Y en píxeles (0 - screen_height)
            button: Estado del botón (None = mantener estado actual)

        Returns:
            bytes: Paquete HID de 9 bytes
        """
        # Validar coordenadas
        if not (0 <= x <= self.screen_width):
            raise ValueError(f"X fuera de rango: {x} (max: {self.screen_width})")
        if not (0 <= y <= self.screen_height):
            raise ValueError(f"Y fuera de rango: {y} (max: {self.screen_height})")

        # Actualizar estado de botón si se especifica
        if button is not None:
            self.button_state = button

        # Normalizar coordenadas a rango 0-32767
        x_norm = int((x / self.screen_width) * 32767)
        y_norm = int((y / self.screen_height) * 32767)

        # Construir paquete HID
        packet = bytearray(9)
        packet[0] = 0x00                              # Padding
        packet[1] = MouseCommand.MOVE_ABSOLUTE        # Comando
        packet[2] = self.button_state                 # Button state
        packet[3] = x_norm & 0xFF                     # X low byte
        packet[4] = (x_norm >> 8) & 0xFF              # X high byte
        packet[5] = y_norm & 0xFF                     # Y low byte
        packet[6] = (y_norm >> 8) & 0xFF              # Y high byte
        packet[7] = 0x00                              # Padding
        packet[8] = 0x00                              # Padding

        # Actualizar posición actual
        self.current_x = x
        self.current_y = y

        return bytes(packet)

    def move_relative(self, delta_x: int, delta_y: int, button: Optional[ButtonState] = None) -> bytes:
        """
        Genera paquete de movimiento relativo (comando 0xa1)

        Args:
            delta_x: Desplazamiento X en píxeles (puede ser negativo)
            delta_y: Desplazamiento Y en píxeles (puede ser negativo)
            button: Estado del botón (None = mantener estado actual)

        Returns:
            bytes: Paquete HID de 9 bytes
        """
        # Validar que el delta no exceda los límites de la pantalla
        new_x = self.current_x + delta_x
        new_y = self.current_y + delta_y

        if not (0 <= new_x <= self.screen_width):
            raise ValueError(f"Delta X resultaría en posición fuera de rango: {new_x}")
        if not (0 <= new_y <= self.screen_height):
            raise ValueError(f"Delta Y resultaría en posición fuera de rango: {new_y}")

        # Actualizar estado de botón si se especifica
        if button is not None:
            self.button_state = button

        # Convertir a formato con signo (complemento a dos si es necesario)
        if delta_x < 0:
            delta_x = (1 << 24) + delta_x  # Complemento a dos de 24 bits
        if delta_y < 0:
            delta_y = (1 << 24) + delta_y

        # Construir paquete HID
        packet = bytearray(9)
        packet[0] = 0x00                              # Padding
        packet[1] = MouseCommand.MOVE_RELATIVE        # Comando
        packet[2] = self.button_state                 # Button state
        packet[3] = delta_x & 0xFF                    # Delta X byte 0
        packet[4] = (delta_x >> 8) & 0xFF             # Delta X byte 1
        packet[5] = (delta_x >> 16) & 0xFF            # Delta X byte 2
        packet[6] = delta_y & 0xFF                    # Delta Y byte 0
        packet[7] = (delta_y >> 8) & 0xFF             # Delta Y byte 1
        packet[8] = 0x00                              # Padding

        # Actualizar posición actual
        self.current_x = new_x
        self.current_y = new_y

        return bytes(packet)

    def alternative_protocol_move(self, delta_x: int = 0, delta_y: int = 0,
                                 firmware_version: int = 0x37, button: Optional[ButtonState] = None) -> bytes:
        """
        Genera paquete con protocolo alternativo (header 'W' 0xAB)

        Args:
            delta_x: Desplazamiento X
            delta_y: Desplazamiento Y (actualmente solo soporta uno a la vez)
            firmware_version: Versión del firmware del dispositivo
            button: Estado del botón (None = mantener estado actual)

        Returns:
            bytes: Paquete de 11 bytes
        """
        # Actualizar estado de botón si se especifica
        if button is not None:
            self.button_state = button

        packet = bytearray(11)
        packet[0] = ord('W')                          # Magic byte 1
        packet[1] = 0xAB                              # Magic byte 2
        packet[2] = 0x00                              # Reserved

        delta = delta_x if delta_x != 0 else delta_y

        if firmware_version < 0x37 and delta == 0:
            # Variante A: Sin movimiento
            packet[3] = 0x04                          # Command type
            packet[4] = 0x07                          # Subtype
            packet[5] = 0x02                          # Data length
            packet[6] = self.button_state             # Button state
            packet[7] = 0x00                          # No delta
            packet[8] = 0x00
            packet[9] = 0x00
            # Checksum
            checksum = sum(packet[0:10]) & 0xFF
            packet[10] = checksum
        else:
            # Variante B: Con movimiento
            packet[3] = 0x05                          # Command type
            packet[4] = 0x05                          # Subtype
            packet[5] = 0x01                          # Data length
            packet[6] = self.button_state             # Button state
            packet[7] = delta & 0xFF                  # Delta byte 0
            packet[8] = (delta >> 8) & 0xFF           # Delta byte 1
            packet[9] = (delta >> 16) & 0xFF          # Delta byte 2
            # Checksum simple
            packet[10] = (self.button_state + (delta & 0xFF) + 0x0d) & 0xFF

        return bytes(packet)

    def left_down(self) -> bytes:
        """
        Genera paquete para presionar botón izquierdo (basado en HT_LeftDown)

        Returns:
            bytes: Paquete HID de 9 bytes con botón izquierdo presionado
        """
        self.button_state = ButtonState.LEFT

        packet = bytearray(9)
        packet[0] = 0x00                              # Padding
        packet[1] = MouseCommand.MOVE_RELATIVE        # Comando
        packet[2] = ButtonState.LEFT                  # Button state = izquierdo
        packet[3] = 0x00                              # Sin movimiento
        packet[4] = 0x00
        packet[5] = 0x00
        packet[6] = 0x00
        packet[7] = 0x00
        packet[8] = 0x00

        return bytes(packet)

    def left_up(self) -> bytes:
        """
        Genera paquete para soltar botón izquierdo

        Returns:
            bytes: Paquete HID de 9 bytes sin botón presionado
        """
        self.button_state = ButtonState.NONE

        packet = bytearray(9)
        packet[0] = 0x00                              # Padding
        packet[1] = MouseCommand.MOVE_RELATIVE        # Comando
        packet[2] = ButtonState.NONE                  # Button state = ninguno
        packet[3] = 0x00                              # Sin movimiento
        packet[4] = 0x00
        packet[5] = 0x00
        packet[6] = 0x00
        packet[7] = 0x00
        packet[8] = 0x00

        return bytes(packet)

    def right_down(self) -> bytes:
        """
        Genera paquete para presionar botón derecho (basado en HT_RightDown)

        Returns:
            bytes: Paquete HID de 9 bytes con botón derecho presionado
        """
        self.button_state = ButtonState.RIGHT

        packet = bytearray(9)
        packet[0] = 0x00                              # Padding
        packet[1] = MouseCommand.MOVE_RELATIVE        # Comando
        packet[2] = ButtonState.RIGHT                 # Button state = derecho
        packet[3] = 0x00                              # Sin movimiento
        packet[4] = 0x00
        packet[5] = 0x00
        packet[6] = 0x00
        packet[7] = 0x00
        packet[8] = 0x00

        return bytes(packet)

    def right_up(self) -> bytes:
        """
        Genera paquete para soltar botón derecho

        Returns:
            bytes: Paquete HID de 9 bytes sin botón presionado
        """
        self.button_state = ButtonState.NONE

        packet = bytearray(9)
        packet[0] = 0x00                              # Padding
        packet[1] = MouseCommand.MOVE_RELATIVE        # Comando
        packet[2] = ButtonState.NONE                  # Button state = ninguno
        packet[3] = 0x00                              # Sin movimiento
        packet[4] = 0x00
        packet[5] = 0x00
        packet[6] = 0x00
        packet[7] = 0x00
        packet[8] = 0x00

        return bytes(packet)

    def click_left(self) -> Tuple[bytes, bytes]:
        """
        Genera par de paquetes para click izquierdo completo (down + up)

        Returns:
            Tuple[bytes, bytes]: (left_down_packet, left_up_packet)
        """
        return (self.left_down(), self.left_up())

    def click_right(self) -> Tuple[bytes, bytes]:
        """
        Genera par de paquetes para click derecho completo (down + up)

        Returns:
            Tuple[bytes, bytes]: (right_down_packet, right_up_packet)
        """
        return (self.right_down(), self.right_up())

    def format_packet_hex(self, packet: bytes) -> str:
        """Formatea paquete como string hexadecimal para debug"""
        return ' '.join(f'{b:02x}' for b in packet)

    def format_packet_detailed(self, packet: bytes) -> str:
        """Formatea paquete con detalles de cada byte"""
        if len(packet) == 9 and packet[1] in [MouseCommand.MOVE_ABSOLUTE, MouseCommand.MOVE_RELATIVE]:
            cmd_name = "MOVE_ABSOLUTE" if packet[1] == MouseCommand.MOVE_ABSOLUTE else "MOVE_RELATIVE"

            # Traducir button state
            button_names = {0: "NONE", 1: "LEFT", 2: "RIGHT"}
            button_str = button_names.get(packet[2], f"UNKNOWN({packet[2]})")

            output = [
                f"Comando: 0x{packet[1]:02x} ({cmd_name})",
                f"Button State: {packet[2]} ({button_str})",
            ]

            if packet[1] == MouseCommand.MOVE_ABSOLUTE:
                x_norm = packet[3] | (packet[4] << 8)
                y_norm = packet[5] | (packet[6] << 8)
                x_px = int((x_norm / 32767.0) * self.screen_width)
                y_px = int((y_norm / 32767.0) * self.screen_height)
                output.extend([
                    f"X normalizado: {x_norm} -> {x_px}px",
                    f"Y normalizado: {y_norm} -> {y_px}px",
                ])
            else:
                delta_x = packet[3] | (packet[4] << 8) | (packet[5] << 16)
                delta_y = packet[6] | (packet[7] << 8)
                # Ajustar por complemento a dos si es necesario
                if delta_x & 0x800000:
                    delta_x = delta_x - (1 << 24)
                if delta_y & 0x8000:
                    delta_y = delta_y - (1 << 16)
                output.extend([
                    f"Delta X: {delta_x:+d}",
                    f"Delta Y: {delta_y:+d}",
                ])

            output.append(f"Raw: {self.format_packet_hex(packet)}")
            return '\n'.join(output)

        elif len(packet) == 11 and packet[0] == ord('W') and packet[1] == 0xAB:
            button_names = {0: "NONE", 1: "LEFT", 2: "RIGHT"}
            button_str = button_names.get(packet[6], f"UNKNOWN({packet[6]})")

            output = [
                "Protocolo alternativo (W 0xAB)",
                f"Command: 0x{packet[3]:02x}",
                f"Subtype: 0x{packet[4]:02x}",
                f"Length: {packet[5]}",
                f"Button State: {packet[6]} ({button_str})",
                f"Checksum: 0x{packet[10]:02x}",
                f"Raw: {self.format_packet_hex(packet)}",
            ]
            return '\n'.join(output)

        return f"Unknown packet: {self.format_packet_hex(packet)}"


def demo():
    """Demostración del uso del protocolo"""
    print("=== iMouse HID Protocol Demo (iPhone 667x365) ===\n")

    # Inicializar con resolución iPhone 667x365 (por defecto)
    protocol = iMouseHIDProtocol()

    # Ejemplo 1: Movimiento absoluto al centro de la pantalla iPhone
    print("1. Movimiento absoluto al centro (333, 182):")
    packet = protocol.move_absolute(333, 182)
    print(protocol.format_packet_detailed(packet))
    print()

    # Ejemplo 2: Movimiento relativo +50 píxeles a la derecha
    print("2. Movimiento relativo (+50, 0):")
    packet = protocol.move_relative(50, 0)
    print(protocol.format_packet_detailed(packet))
    print()

    # Ejemplo 3: Movimiento relativo negativo
    print("3. Movimiento relativo (-50, -30):")
    packet = protocol.move_relative(-50, -30)
    print(protocol.format_packet_detailed(packet))
    print()

    # Ejemplo 4: Click izquierdo
    print("4. Click izquierdo completo (down + up):")
    down, up = protocol.click_left()
    print("Down packet:")
    print(protocol.format_packet_detailed(down))
    print("\nUp packet:")
    print(protocol.format_packet_detailed(up))
    print()

    # Ejemplo 5: Click derecho
    print("5. Click derecho completo (down + up):")
    down, up = protocol.click_right()
    print("Down packet:")
    print(protocol.format_packet_detailed(down))
    print("\nUp packet:")
    print(protocol.format_packet_detailed(up))
    print()

    # Ejemplo 6: Arrastrar (movimiento con botón presionado)
    print("6. Arrastrar con botón izquierdo:")
    protocol.left_down()  # Presionar botón
    packet = protocol.move_relative(50, 30)  # Mover con botón presionado
    print("Mover mientras botón está presionado:")
    print(protocol.format_packet_detailed(packet))
    protocol.left_up()  # Soltar botón
    print()

    # Ejemplo 7: Protocolo alternativo con botón
    print("7. Protocolo alternativo (botón izquierdo):")
    packet = protocol.alternative_protocol_move(delta_x=10, button=ButtonState.LEFT)
    print(protocol.format_packet_detailed(packet))
    print()

    print("Posición final del cursor:", (protocol.current_x, protocol.current_y))
    print(f"Estado del botón: {protocol.button_state.name}")


if __name__ == "__main__":
    demo()
