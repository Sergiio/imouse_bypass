#!/usr/bin/env python3
"""
iMouse Clicker - Envío interactivo de clicks al iPhone
Pide coordenadas y envía clicks directamente al dispositivo
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

from imouse_hid_protocol import iMouseHIDProtocol, ButtonState


class InteractiveClicker:
    def __init__(self, screen_width=365, screen_height=667):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.protocol = iMouseHIDProtocol(screen_width=screen_width, screen_height=screen_height)
        self.device = None
        self.out_report = None
        self.report_size = 0
        self.stats = {'clicks': 0, 'double_clicks': 0, 'drags': 0, 'errors': 0}

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
        print(f"   Report size: {self.report_size} bytes")
        print(f"   Resolución: {self.screen_width}x{self.screen_height}")
        return True

    def send_packet(self, packet, delay=0):
        """Envía un paquete al dispositivo"""
        if not self.out_report:
            return False

        try:
            # Ajustar al tamaño del reporte
            data_list = list(packet)
            while len(data_list) < self.report_size:
                data_list.append(0x00)

            self.out_report.set_raw_data(data_list)
            self.out_report.send()

            if delay > 0:
                time.sleep(delay)

            return True

        except Exception as e:
            self.stats['errors'] += 1
            print(f"❌ Error enviando paquete: {e}")
            return False

    def perform_click(self, x, y, button='left', reset=True):
        """Realiza un click simple en las coordenadas especificadas"""
        print(f"\n🖱️  Click {button} en ({x}, {y})")

        # Reset opcional
        if reset:
            print("   ↻ Reseteando posición...", end='', flush=True)
            reset_packet = self.protocol.reset_position()
            if self.send_packet(reset_packet, 0.05):
                print(" ✓")
            else:
                print(" ✗")

        # Mover a la posición
        print(f"   → Moviendo a ({x}, {y})...", end='', flush=True)
        move_packet = self.protocol.move_absolute(x, y)
        if self.send_packet(move_packet, 0.1):
            print(" ✓")
        else:
            print(" ✗")
            return False

        # Click
        print(f"   • Click {button}...", end='', flush=True)
        if button == 'left':
            down_packet = self.protocol.left_down()
            up_packet = self.protocol.left_up()
        else:
            down_packet = self.protocol.right_down()
            up_packet = self.protocol.right_up()

        if self.send_packet(down_packet, 0.065) and self.send_packet(up_packet, 0):
            print(" ✓")
            self.stats['clicks'] += 1
            return True
        else:
            print(" ✗")
            return False

    def perform_double_click(self, x, y):
        """Realiza un doble click en las coordenadas especificadas"""
        print(f"\n🖱️🖱️  Doble click en ({x}, {y})")

        # Mover a la posición
        print(f"   → Moviendo a ({x}, {y})...", end='', flush=True)
        move_packet = self.protocol.move_absolute(x, y)
        if self.send_packet(move_packet, 0.1):
            print(" ✓")
        else:
            print(" ✗")
            return False

        # Primer click
        print("   • Primer click...", end='', flush=True)
        if self.send_packet(self.protocol.left_down(), 0.065) and \
           self.send_packet(self.protocol.left_up(), 0.15):
            print(" ✓")
        else:
            print(" ✗")
            return False

        # Segundo click
        print("   • Segundo click...", end='', flush=True)
        if self.send_packet(self.protocol.left_down(), 0.065) and \
           self.send_packet(self.protocol.left_up(), 0):
            print(" ✓")
            self.stats['double_clicks'] += 1
            return True
        else:
            print(" ✗")
            return False

    def perform_drag(self, x1, y1, x2, y2):
        """Realiza un arrastre desde (x1,y1) hasta (x2,y2)"""
        print(f"\n↔️  Arrastrando desde ({x1}, {y1}) hasta ({x2}, {y2})")

        # Mover al punto inicial
        print(f"   → Moviendo a ({x1}, {y1})...", end='', flush=True)
        move_packet = self.protocol.move_absolute(x1, y1)
        if self.send_packet(move_packet, 0.1):
            print(" ✓")
        else:
            print(" ✗")
            return False

        # Presionar botón
        print("   • Presionando botón...", end='', flush=True)
        if self.send_packet(self.protocol.left_down(), 0.05):
            print(" ✓")
        else:
            print(" ✗")
            return False

        # Arrastrar al destino
        print(f"   ↗ Arrastrando a ({x2}, {y2})...", end='', flush=True)
        drag_packet = self.protocol.move_absolute(x2, y2, button=ButtonState.LEFT)
        if self.send_packet(drag_packet, 0.1):
            print(" ✓")
        else:
            print(" ✗")
            return False

        # Soltar botón
        print("   • Soltando botón...", end='', flush=True)
        if self.send_packet(self.protocol.left_up(), 0):
            print(" ✓")
            self.stats['drags'] += 1
            return True
        else:
            print(" ✗")
            return False

    def parse_coordinates(self, input_str):
        """Parsea una entrada de coordenadas en formato 'x, y' o 'x,y'"""
        try:
            parts = input_str.replace(' ', '').split(',')
            if len(parts) != 2:
                return None
            x = int(parts[0])
            y = int(parts[1])

            # Validar rango
            if not (0 <= x <= self.screen_width):
                print(f"❌ X fuera de rango (0-{self.screen_width})")
                return None
            if not (0 <= y <= self.screen_height):
                print(f"❌ Y fuera de rango (0-{self.screen_height})")
                return None

            return x, y
        except ValueError:
            return None

    def run(self):
        """Ejecuta el modo interactivo"""
        if not self.connect_device():
            return

        print()
        print("=" * 80)
        print("🖱️  iMOUSE CLICKER - MODO INTERACTIVO")
        print("=" * 80)
        print()
        print("📝 Instrucciones:")
        print("   • Ingresa coordenadas en formato: x, y  (ej: 300, 30)")
        print("   • Comandos especiales:")
        print("     - 'double x, y': Doble click en (x, y)")
        print("     - 'drag x1, y1, x2, y2': Arrastrar desde (x1,y1) a (x2,y2)")
        print("     - 'right x, y': Click derecho en (x, y)")
        print("     - 'res WIDTHxHEIGHT': Cambiar resolución (ej: res 768x1024)")
        print("     - 'clear' o 'cls': Limpiar pantalla")
        print("     - 'exit' o 'quit': Salir")
        print()
        print(f"📱 Resolución actual: {self.screen_width}x{self.screen_height}")
        print("=" * 80)
        print()

        try:
            while True:
                try:
                    user_input = input("🎯 > ").strip()
                except KeyboardInterrupt:
                    print("\n⚠️  Interrupción detectada")
                    break

                if not user_input:
                    continue

                # Comandos de salida
                if user_input.lower() in ['exit', 'quit', 'salir', 'q']:
                    print("\n👋 Saliendo...")
                    break

                # Limpiar pantalla
                if user_input.lower() in ['clear', 'cls']:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("🖱️  iMOUSE CLICKER - MODO INTERACTIVO")
                    print("=" * 80)
                    print(f"📱 Resolución: {self.screen_width}x{self.screen_height}")
                    print()
                    continue

                # Cambiar resolución
                if user_input.lower().startswith('res '):
                    try:
                        res_str = user_input[4:].strip()
                        width, height = res_str.split('x')
                        self.screen_width = int(width)
                        self.screen_height = int(height)
                        self.protocol = iMouseHIDProtocol(screen_width=self.screen_width,
                                                         screen_height=self.screen_height)
                        print(f"✅ Resolución cambiada a {self.screen_width}x{self.screen_height}")
                    except:
                        print("❌ Formato inválido. Usa: res WIDTHxHEIGHT (ej: res 768x1024)")
                    continue

                # Doble click
                if user_input.lower().startswith('double '):
                    coords_str = user_input[7:].strip()
                    coords = self.parse_coordinates(coords_str)
                    if coords:
                        self.perform_double_click(coords[0], coords[1])
                    else:
                        print("❌ Formato inválido. Usa: double x, y")
                    continue

                # Drag
                if user_input.lower().startswith('drag '):
                    coords_str = user_input[5:].strip()
                    try:
                        parts = coords_str.replace(' ', '').split(',')
                        if len(parts) == 4:
                            x1, y1, x2, y2 = map(int, parts)
                            # Validar rangos
                            if all(0 <= x <= self.screen_width for x in [x1, x2]) and \
                               all(0 <= y <= self.screen_height for y in [y1, y2]):
                                self.perform_drag(x1, y1, x2, y2)
                            else:
                                print(f"❌ Coordenadas fuera de rango (0-{self.screen_width}, 0-{self.screen_height})")
                        else:
                            print("❌ Formato inválido. Usa: drag x1, y1, x2, y2")
                    except ValueError:
                        print("❌ Formato inválido. Usa: drag x1, y1, x2, y2")
                    continue

                # Click derecho
                if user_input.lower().startswith('right '):
                    coords_str = user_input[6:].strip()
                    coords = self.parse_coordinates(coords_str)
                    if coords:
                        self.perform_click(coords[0], coords[1], button='right')
                    else:
                        print("❌ Formato inválido. Usa: right x, y")
                    continue

                # Click normal (izquierdo)
                coords = self.parse_coordinates(user_input)
                if coords:
                    self.perform_click(coords[0], coords[1])
                else:
                    print("❌ Formato inválido. Usa: x, y  (ej: 300, 30)")
                    print("   O prueba: 'double x, y', 'right x, y', 'drag x1, y1, x2, y2'")

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
            print(f"   Clicks simples:  {self.stats['clicks']}")
            print(f"   Dobles clicks:   {self.stats['double_clicks']}")
            print(f"   Arrastres:       {self.stats['drags']}")
            print(f"   Errores:         {self.stats['errors']}")
            print("=" * 80)


def main():
    # Verificar si el archivo de protocolo existe
    try:
        from imouse_hid_protocol import iMouseHIDProtocol, ButtonState
    except ImportError:
        print("❌ Error: No se encontró imouse_hid_protocol.py")
        print("   Asegúrate de que el archivo esté en el mismo directorio")
        input("\nPresiona ENTER para salir...")
        sys.exit(1)

    clicker = InteractiveClicker()

    try:
        clicker.run()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupción detectada")

    input("\nPresiona ENTER para salir...")


if __name__ == "__main__":
    main()