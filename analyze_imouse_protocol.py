#!/usr/bin/env python3
"""
Análisis del protocolo iMouse
Captura y analiza cómo iMouse procesa los comandos USB
"""

import sys
import time
import threading
import json

try:
    import pywinusb.hid as hid
except ImportError:
    print("❌ pywinusb no instalado")
    sys.exit(1)


class iMouseProtocolAnalyzer:
    """Analizador del protocolo iMouse"""

    def __init__(self, vendor_id=0x720a, product_id=0x3dab):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device = None
        self.input_buffer = []
        self.receiving = False

    def on_input_data(self, data):
        """Callback cuando el dispositivo envía datos al host"""
        if self.receiving:
            timestamp = time.time()
            self.input_buffer.append({
                'timestamp': timestamp,
                'data': data,
                'hex': ' '.join(f'{b:02x}' for b in data)
            })
            print(f"  ← INPUT: {' '.join(f'{b:02x}' for b in data[:16])}")

    def connect(self):
        """Conecta al dispositivo iMouse"""
        devices = hid.HidDeviceFilter(
            vendor_id=self.vendor_id,
            product_id=self.product_id
        ).get_devices()

        if not devices:
            print(f"❌ Dispositivo no encontrado")
            return False

        self.device = devices[0]
        self.device.open()

        # Configurar callback para datos entrantes
        self.device.set_raw_data_handler(self.on_input_data)

        print(f"✅ Conectado a: {self.device.product_name}")
        print(f"   VID:PID = 0x{self.vendor_id:04x}:0x{self.product_id:04x}")

        return True

    def send_packet(self, packet_bytes, description=""):
        """Envía un paquete y espera respuesta"""

        if not self.device:
            return False

        # Obtener output report
        out_reports = self.device.find_output_reports()
        if not out_reports:
            print("❌ No hay output reports")
            return False

        out_report = out_reports[0]
        report_size = len(out_report.get_raw_data())

        # Ajustar tamaño
        data = packet_bytes[:]
        while len(data) < report_size:
            data.append(0x00)
        if len(data) > report_size:
            data = data[:report_size]

        # Limpiar buffer de entrada
        self.input_buffer.clear()
        self.receiving = True

        # Enviar
        hex_str = ' '.join(f'{b:02x}' for b in data)
        print(f"\n  → OUTPUT: {hex_str}")
        if description:
            print(f"     Desc: {description}")

        try:
            out_report.set_raw_data(data)
            out_report.send()

            # Esperar respuesta
            time.sleep(0.1)

            if self.input_buffer:
                print(f"     ✓ Recibidas {len(self.input_buffer)} respuestas")
                return self.input_buffer.copy()
            else:
                print(f"     ⚠️  Sin respuesta del dispositivo")
                return []

        except Exception as e:
            print(f"     ✗ Error: {e}")
            return None

    def analyze_keyboard_protocol(self):
        """Analiza el protocolo de teclado"""

        print("\n" + "=" * 80)
        print("🔬 ANÁLISIS DEL PROTOCOLO iMouse - TECLADO")
        print("=" * 80)

        # Formato base: [Report ID][0xa2][Modifier][Reserved][Scancode][...padding]
        # ⚠️ CONFIRMADO: Ghidra muestra que el marcador es 0xa2, no 0xa1

        test_cases = [
            {
                "name": "Tecla 'H' simple (sin modificador)",
                "packet": [0x00, 0xa2, 0x00, 0x00, 0x0b, 0x00, 0x00, 0x00, 0x00],
                "expected": "Envía scancode 0x0b (H) al iPhone"
            },
            {
                "name": "Tecla 'H' con Shift (mayúscula)",
                "packet": [0x00, 0xa2, 0x02, 0x00, 0x0b, 0x00, 0x00, 0x00, 0x00],
                "expected": "Envía scancode 0x0b + Shift → 'H' mayúscula"
            },
            {
                "name": "Release (liberar todas las teclas)",
                "packet": [0x00, 0xa2, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                "expected": "Libera todas las teclas presionadas"
            },
            {
                "name": "Ctrl+C (copiar)",
                "packet": [0x00, 0xa2, 0x01, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00],
                "expected": "Ctrl (0x01) + C (0x06)"
            },
            {
                "name": "Alt+Tab (cambiar app)",
                "packet": [0x00, 0xa2, 0x04, 0x00, 0x2b, 0x00, 0x00, 0x00, 0x00],
                "expected": "Alt (0x04) + Tab (0x2b)"
            },
            {
                "name": "Comando alternativo - byte 1 = 0xa1",
                "packet": [0x00, 0xa1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                "expected": "¿Protocolo alternativo? (0xa1 vs 0xa2 estándar)"
            },
            {
                "name": "Comando especial - byte 1 = 0xa3",
                "packet": [0x00, 0xa3, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                "expected": "¿Otro tipo de comando?"
            },
        ]

        results = []

        for i, test in enumerate(test_cases, 1):
            print(f"\n{'='*80}")
            print(f"Prueba {i}/{len(test_cases)}: {test['name']}")
            print(f"Esperado: {test['expected']}")
            print(f"{'='*80}")

            response = self.send_packet(test['packet'], test['name'])

            results.append({
                'test': test['name'],
                'packet': test['packet'],
                'response': response,
                'expected': test['expected']
            })

            time.sleep(0.2)

        return results

    def analyze_mouse_protocol(self):
        """Analiza el protocolo de mouse"""

        print("\n" + "=" * 80)
        print("🔬 ANÁLISIS DEL PROTOCOLO iMouse - MOUSE")
        print("=" * 80)

        # Protocolo de mouse típicamente:
        # [Report ID][Type][Buttons][X_low][X_high][Y_low][Y_high][Wheel]

        test_cases = [
            {
                "name": "Mouse: Click izquierdo",
                "packet": [0x00, 0xa1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                "expected": "Click botón izquierdo"
            },
            {
                "name": "Mouse: Mover a coordenadas",
                "packet": [0x00, 0xa1, 0x00, 0x64, 0x00, 0x64, 0x00, 0x00, 0x00],
                "expected": "Mover cursor a X=100, Y=100"
            },
        ]

        results = []

        for i, test in enumerate(test_cases, 1):
            print(f"\n{'='*80}")
            print(f"Prueba {i}/{len(test_cases)}: {test['name']}")
            print(f"{'='*80}")

            response = self.send_packet(test['packet'], test['name'])

            results.append({
                'test': test['name'],
                'packet': test['packet'],
                'response': response
            })

            time.sleep(0.2)

        return results

    def save_results(self, results, filename):
        """Guarda los resultados del análisis"""

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        print(f"\n💾 Resultados guardados en: {filename}")

    def disconnect(self):
        """Desconecta del dispositivo"""
        self.receiving = False
        if self.device:
            self.device.close()
            print("\n✅ Desconectado")


def main():
    analyzer = iMouseProtocolAnalyzer()

    print("=" * 80)
    print("🔬 ANALIZADOR DE PROTOCOLO iMouse")
    print("=" * 80)
    print()
    print("Este script analiza cómo iMouse procesa los comandos USB")
    print("y los traduce para enviarlos al iPhone/iPad")
    print()

    if not analyzer.connect():
        return

    try:
        # Analizar protocolo de teclado
        keyboard_results = analyzer.analyze_keyboard_protocol()

        # Analizar protocolo de mouse
        # mouse_results = analyzer.analyze_mouse_protocol()

        # Guardar resultados
        all_results = {
            'device': {
                'vendor_id': f"0x{analyzer.vendor_id:04x}",
                'product_id': f"0x{analyzer.product_id:04x}",
                'product_name': analyzer.device.product_name
            },
            'keyboard_tests': keyboard_results,
            # 'mouse_tests': mouse_results
        }

        analyzer.save_results(all_results, 'imouse_protocol_analysis.json')

        # Resumen
        print("\n" + "=" * 80)
        print("📊 RESUMEN DEL ANÁLISIS")
        print("=" * 80)
        print()
        print("FORMATO DEL PAQUETE DE TECLADO:")
        print("  Byte 0: 0x00          (Report ID)")
        print("  Byte 1: 0xa2          (Marcador de protocolo iMouse - CONFIRMADO EN GHIDRA)")
        print("  Byte 2: Modifier      (0x00=none, 0x01=Ctrl, 0x02=Shift, 0x04=Alt, 0x08=Win)")
        print("  Byte 3: Reserved      (0x00)")
        print("  Byte 4: Scancode      (HID keyboard scancode)")
        print("  Byte 5-8: Padding     (0x00)")
        print()
        print("NOTA: El código fuente (FUN_100024b0) confirma: local_57 = 0xa2")
        print()
        print("MODIFICADORES (Byte 2):")
        print("  0x01 = Left Ctrl")
        print("  0x02 = Left Shift")
        print("  0x04 = Left Alt")
        print("  0x08 = Left Win/Cmd")
        print("  0x10 = Right Ctrl")
        print("  0x20 = Right Shift")
        print("  0x40 = Right Alt")
        print("  0x80 = Right Win/Cmd")
        print()
        print("PROCESO:")
        print("  1. PC recibe paquete USB → iMouseSrv.exe")
        print("  2. iMouseSrv.exe decodifica el paquete")
        print("  3. iMouseSrv.exe envía comando por WiFi/AirPlay al iPhone")
        print("  4. iPhone ejecuta la tecla/acción")
        print()

    finally:
        analyzer.disconnect()


if __name__ == "__main__":
    main()
