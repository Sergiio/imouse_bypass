#!/usr/bin/env python3
"""
iMouse Swipe - Control de gestos y swipes para iPhone/iPad
Implementa swipes fluidos con múltiples puntos intermedios y easing natural
"""

import sys
import time

try:
    import pywinusb.hid as hid
except ImportError:
    print("❌ Error: pywinusb no está instalado")
    print("   pip install pywinusb")
    sys.exit(1)

from imouse_hid_protocol import iMouseHIDProtocol, ButtonState


class SwipeController:
    def __init__(self, screen_width=365, screen_height=667):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.protocol = iMouseHIDProtocol(screen_width=screen_width, screen_height=screen_height)
        self.device = None
        self.out_report = None
        self.report_size = 0

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
            data_list = list(packet)
            while len(data_list) < self.report_size:
                data_list.append(0x00)

            self.out_report.set_raw_data(data_list)
            self.out_report.send()

            if delay > 0:
                time.sleep(delay)

            return True

        except Exception as e:
            print(f"❌ Error enviando paquete: {e}")
            return False

    def swipe(self, start_x, start_y, end_x, end_y, duration=0.3, steps=10):
        """
        Realiza un swipe suave con múltiples puntos intermedios

        Args:
            start_x, start_y: Punto inicial
            end_x, end_y: Punto final
            duration: Duración total del swipe en segundos
            steps: Número de pasos intermedios (más pasos = más suave)
        """

        print(f"\n📱 SWIPE: ({start_x}, {start_y}) → ({end_x}, {end_y})")
        print(f"   Duración: {duration}s, Pasos: {steps}")

        # Reset posición inicial
        print("   ↻ Reseteando posición...", end='', flush=True)
        reset_packet = self.protocol.reset_position()
        if self.send_packet(reset_packet, 0.05):
            print(" ✓")
        else:
            print(" ✗")
            return False

        # Mover al punto inicial
        print(f"   → Moviendo a punto inicial ({start_x}, {start_y})...", end='', flush=True)
        move_packet = self.protocol.move_absolute(start_x, start_y)
        if self.send_packet(move_packet, 0.1):
            print(" ✓")
        else:
            print(" ✗")
            return False

        # Presionar el "dedo" (botón izquierdo)
        print("   • Iniciando toque...", end='', flush=True)
        down_packet = self.protocol.left_down()
        if self.send_packet(down_packet, 0.05):
            print(" ✓")
        else:
            print(" ✗")
            return False

        # Calcular los puntos intermedios
        delta_x = end_x - start_x
        delta_y = end_y - start_y
        step_delay = duration / steps

        print(f"   ↗ Deslizando ({steps} pasos):", end='', flush=True)

        # Enviar cada punto intermedio
        for i in range(1, steps + 1):
            # Calcular posición interpolada
            progress = i / steps

            # Usar una curva de easing para movimiento más natural
            # ease_out_cubic para desaceleración al final
            eased_progress = 1 - pow(1 - progress, 3)

            current_x = int(start_x + delta_x * eased_progress)
            current_y = int(start_y + delta_y * eased_progress)

            # Mover a la posición manteniendo el botón presionado
            move_packet = self.protocol.move_absolute(current_x, current_y, button=ButtonState.LEFT)

            if self.send_packet(move_packet, step_delay):
                if i % (steps // 5) == 0 or i == steps:  # Mostrar progreso cada 20%
                    print(".", end='', flush=True)
            else:
                print(" ✗")
                return False

        print(" ✓")

        # Soltar el "dedo"
        print("   • Soltando toque...", end='', flush=True)
        up_packet = self.protocol.left_up()
        if self.send_packet(up_packet, 0.05):
            print(" ✓")
            print("   ✅ Swipe completado")
            return True
        else:
            print(" ✗")
            return False

    def swipe_down(self, duration=0.15):
        """Swipe hacia abajo con margen seguro para no activar centro de notificaciones"""
        center_x = self.screen_width // 2
        start_y = 120  # Margen seguro desde arriba (evita centro de notificaciones)
        end_y = self.screen_height - 80  # Margen seguro desde abajo

        print("\n⬇️  SWIPE HACIA ABAJO (RÁPIDO)")
        return self.swipe(center_x, start_y, center_x, end_y, duration, steps=8)

    def swipe_up(self, duration=0.15):
        """Swipe hacia arriba con margen seguro"""
        center_x = self.screen_width // 2
        start_y = self.screen_height - 80  # Margen seguro desde abajo
        end_y = 120  # Margen seguro desde arriba (evita centro de notificaciones)

        print("\n⬆️  SWIPE HACIA ARRIBA (RÁPIDO)")
        return self.swipe(center_x, start_y, center_x, end_y, duration, steps=8)

    def swipe_left(self, duration=0.2):
        """Swipe hacia la izquierda (cambiar página) con margen seguro"""
        center_y = self.screen_height // 2
        start_x = self.screen_width - 60  # Margen seguro desde el borde derecho
        end_x = 60  # Margen seguro desde el borde izquierdo

        print("\n⬅️  SWIPE HACIA LA IZQUIERDA (RÁPIDO)")
        return self.swipe(start_x, center_y, end_x, center_y, duration, steps=8)

    def swipe_right(self, duration=0.2):
        """Swipe hacia la derecha (regresar) con margen seguro"""
        center_y = self.screen_height // 2
        start_x = 60  # Margen seguro desde el borde izquierdo
        end_x = self.screen_width - 60  # Margen seguro desde el borde derecho

        print("\n➡️  SWIPE HACIA LA DERECHA (RÁPIDO)")
        return self.swipe(start_x, center_y, end_x, center_y, duration, steps=8)

    def scroll_down_slow(self):
        """Scroll medio para lectura controlada"""
        center_x = self.screen_width // 2
        start_y = self.screen_height // 3  # Tercio superior
        end_y = self.screen_height * 2 // 3  # Tercio inferior

        print("\n📜 SCROLL MEDIO (LECTURA)")
        return self.swipe(center_x, start_y, center_x, end_y, duration=0.25, steps=10)

    def pull_to_refresh(self):
        """Gesto de pull-to-refresh (arrastrar hacia abajo desde arriba)"""
        center_x = self.screen_width // 2
        start_y = 80  # Margen seguro pero aún cerca del borde superior
        end_y = self.screen_height // 2  # Hasta la mitad

        print("\n🔄 PULL TO REFRESH")
        return self.swipe(center_x, start_y, center_x, end_y, duration=0.3, steps=12)

    def swipe_down_super_fast(self):
        """Swipe súper rápido hacia abajo para scroll veloz"""
        center_x = self.screen_width // 2
        start_y = 150  # Margen más seguro para evitar centro de notificaciones
        end_y = self.screen_height - 100  # Margen desde abajo

        print("\n⚡ SWIPE SÚPER RÁPIDO HACIA ABAJO")
        return self.swipe(center_x, start_y, center_x, end_y, duration=0.1, steps=5)

    def swipe_up_super_fast(self):
        """Swipe súper rápido hacia arriba para scroll veloz"""
        center_x = self.screen_width // 2
        start_y = self.screen_height - 100  # Margen desde abajo
        end_y = 150  # Margen más seguro arriba

        print("\n⚡ SWIPE SÚPER RÁPIDO HACIA ARRIBA")
        return self.swipe(center_x, start_y, center_x, end_y, duration=0.1, steps=5)

    def close(self):
        """Cierra la conexión con el dispositivo"""
        if self.device:
            self.device.close()


def main():
    controller = SwipeController()

    if not controller.connect_device():
        input("\nPresiona ENTER para salir...")
        return

    print("\n" + "=" * 80)
    print("📱 iMOUSE SWIPE TEST - PRUEBA DE GESTOS")
    print("=" * 80)
    print()
    print("SWIPES RÁPIDOS (Navegación):")
    print("  1. ⬇️  Swipe ABAJO RÁPIDO (0.15s, recorrido largo)")
    print("  2. ⬆️  Swipe ARRIBA RÁPIDO (0.15s, recorrido largo)")
    print("  3. ⬅️  Swipe IZQUIERDA RÁPIDO (cambiar página)")
    print("  4. ➡️  Swipe DERECHA RÁPIDO (regresar)")
    print()
    print("SWIPES SÚPER RÁPIDOS:")
    print("  5. ⚡ Swipe ABAJO SÚPER RÁPIDO (0.1s)")
    print("  6. ⚡ Swipe ARRIBA SÚPER RÁPIDO (0.1s)")
    print()
    print("OTROS GESTOS:")
    print("  7. 📜 Scroll MEDIO (lectura controlada)")
    print("  8. 🔄 Pull to Refresh")
    print()
    print("  9. Swipe personalizado (ingresar coordenadas)")
    print()
    print("  0. Salir")
    print()
    print("=" * 80)

    try:
        while True:
            choice = input("\n🎯 Elige una opción (0-9): ").strip()

            if choice == '0':
                print("\n👋 Saliendo...")
                break
            elif choice == '1':
                controller.swipe_down()
            elif choice == '2':
                controller.swipe_up()
            elif choice == '3':
                controller.swipe_left()
            elif choice == '4':
                controller.swipe_right()
            elif choice == '5':
                controller.swipe_down_super_fast()
            elif choice == '6':
                controller.swipe_up_super_fast()
            elif choice == '7':
                controller.scroll_down_slow()
            elif choice == '8':
                controller.pull_to_refresh()
            elif choice == '9':
                print("\n📍 SWIPE PERSONALIZADO")
                try:
                    start_coords = input("   Coordenadas iniciales (x, y): ").strip()
                    sx, sy = map(int, start_coords.replace(' ', '').split(','))

                    end_coords = input("   Coordenadas finales (x, y): ").strip()
                    ex, ey = map(int, end_coords.replace(' ', '').split(','))

                    duration = float(input("   Duración en segundos (0.3): ") or "0.3")
                    steps = int(input("   Número de pasos (10): ") or "10")

                    controller.swipe(sx, sy, ex, ey, duration, steps)

                except (ValueError, IndexError):
                    print("❌ Formato inválido")
            else:
                print("❌ Opción no válida")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupción detectada")

    finally:
        controller.close()
        print("\n📊 Sesión finalizada")

    input("\nPresiona ENTER para salir...")


if __name__ == "__main__":
    main()