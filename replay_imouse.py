#!/usr/bin/env python3
"""
Replay especializado para dispositivo iMouse
El protocolo iMouse usa 0xa1 como marcador, NO como Report ID
"""

import sys
import json
import time

try:
    import pywinusb.hid as hid
except ImportError:
    print("❌ Error: pywinusb no está instalado")
    print("   pip install pywinusb")
    sys.exit(1)


def replay_imouse(vendor_id: int, product_id: int, capture_file: str, speed: float = 1.0):
    """Reenvía datos al dispositivo iMouse"""

    print("\n🔄 REPLAY IMOUSE")
    print("=" * 80)

    # Cargar datos capturados
    try:
        with open(capture_file, 'r') as f:
            packets = json.load(f)
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {capture_file}")
        return False
    except json.JSONDecodeError:
        print(f"❌ Error al leer JSON: {capture_file}")
        return False

    print(f"📂 Archivo: {capture_file}")
    print(f"📦 Total paquetes: {len(packets)}")

    # Filtrar paquetes OUT con datos o bytes
    out_packets = [p for p in packets if p.get('direction') == 'out' and (p.get('data') or p.get('bytes'))]

    if not out_packets:
        print("\n❌ No hay paquetes OUT para enviar")
        print("   Verifica que el JSON tenga 'direction': 'out' y 'bytes' o 'data'")
        return False

    print(f"📤 Paquetes a enviar: {len(out_packets)}")
    print()

    # Buscar dispositivo
    print("🔌 Buscando dispositivo...")
    devices = hid.HidDeviceFilter(vendor_id=vendor_id, product_id=product_id).get_devices()
    
    if not devices:
        print(f"❌ Dispositivo no encontrado: 0x{vendor_id:04x}:0x{product_id:04x}")
        return False

    device = devices[0]
    device.open()

    print(f"✅ Conectado a: {device.product_name}")
    print(f"   VID: 0x{vendor_id:04x}")
    print(f"   PID: 0x{product_id:04x}")

    # Obtener output report
    out_report = None
    for report in device.find_output_reports():
        out_report = report
        break

    if not out_report:
        print("❌ No se encontró output report")
        device.close()
        return False

    report_size = len(out_report.get_raw_data())
    current_data = out_report.get_raw_data()
    device_report_id = current_data[0]

    print(f"   Report size: {report_size} bytes")
    print(f"   Report ID:   0x{device_report_id:02x}")
    print()

    print("⌨️  ENVIANDO DATOS (protocolo iMouse)...")
    print("=" * 80)

    first_timestamp = out_packets[0]['timestamp']
    start_time = time.time()
    sent = 0
    errors = 0

    for i, packet in enumerate(out_packets, 1):
        # Timing
        target_time = (packet['timestamp'] - first_timestamp) / speed
        current_time = time.time() - start_time
        sleep_time = target_time - current_time

        if sleep_time > 0:
            time.sleep(sleep_time)

        # Obtener datos (priorizar 'bytes' sobre 'data')
        data_bytes = None

        if 'bytes' in packet and packet['bytes']:
            data_bytes = packet['bytes']
        elif packet.get('data'):
            try:
                data_bytes = list(bytes.fromhex(packet['data']))
            except ValueError:
                print(f"  [{i:3d}] ⚠️  Datos hex inválidos")
                continue

        if not data_bytes:
            continue

        # PROTOCOLO iMouse:
        # El formato correcto es [0x00][0xa1][mod][res][key][0][0][0][0]
        # donde 0x00 es el Report ID del dispositivo

        data_list = data_bytes[:]

        # Ajustar al tamaño del reporte
        while len(data_list) < report_size:
            data_list.append(0x00)

        if len(data_list) > report_size:
            data_list = data_list[:report_size]

        # El JSON ya debería tener el formato correcto con 0x00 al inicio
        # Si no lo tiene, verificamos y corregimos
        if data_list[0] != 0x00:
            # El paquete no tiene Report ID, añadirlo
            data_list = [0x00] + data_list[:(report_size-1)]

        # Enviar
        try:
            out_report.set_raw_data(data_list)
            out_report.send()
            sent += 1

            # Mostrar progreso
            if sent <= 10 or sent % 10 == 0:
                data_str = ' '.join(f'{b:02x}' for b in data_list[:8])
                desc = packet.get('description', '')
                if desc:
                    print(f"  [{sent:3d}] ✓ {data_str}  # {desc}")
                else:
                    print(f"  [{sent:3d}] ✓ {data_str}")

        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  [{i:3d}] ✗ Error: {e}")

    elapsed = time.time() - start_time

    device.close()

    print("\n" + "=" * 80)
    print("✅ REPLAY COMPLETADO")
    print(f"   Paquetes enviados: {sent}/{len(out_packets)}")
    print(f"   Errores:           {errors}")
    print(f"   Tiempo:            {elapsed:.3f}s")
    print("=" * 80)

    return sent > 0


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Replay de capturas para dispositivo iMouse',
        epilog='Ejemplo: python replay_imouse.py test_hola.json'
    )

    parser.add_argument('capture_file',
                        help='Archivo JSON con datos capturados')
    parser.add_argument('-v', '--vendor', type=lambda x: int(x, 0),
                        default=0x720a,
                        help='Vendor ID (default: 0x720a)')
    parser.add_argument('-p', '--product', type=lambda x: int(x, 0),
                        default=0x3dab,
                        help='Product ID (default: 0x3dab)')
    parser.add_argument('-s', '--speed', type=float, default=1.0,
                        help='Velocidad de reproducción (default: 1.0)')

    args = parser.parse_args()

    replay_imouse(args.vendor, args.product, args.capture_file, args.speed)


if __name__ == "__main__":
    main()
