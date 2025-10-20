#!/usr/bin/env python3
"""
Generador de archivos JSON para replay_imouse.py
Crea secuencias de clicks en posiciones específicas
"""

import json
import sys
from imouse_hid_protocol import iMouseHIDProtocol, ButtonState


def generate_click_json(x: int, y: int, output_file: str,
                       screen_width: int = 365, screen_height: int = 667,
                       button: str = "left", reset: bool = True, use_restart: bool = False):
    """
    Genera archivo JSON para hacer click en (x, y)

    Args:
        x, y: Coordenadas del click
        output_file: Nombre del archivo JSON de salida
        screen_width, screen_height: Resolución de la pantalla
        button: "left" o "right"
        reset: Si True, resetea posición del mouse antes de mover
        use_restart: Si True, usa HT_Restart (0xa4) en lugar de reset normal
    """

    protocol = iMouseHIDProtocol(screen_width=screen_width, screen_height=screen_height)

    packets = []
    t = 0.0

    # Paquete 0: Reset (opcional)
    if reset:
        if use_restart:
            reset_packet = protocol.restart()
            desc = "Restart mouse (0xa4)"
        else:
            reset_packet = protocol.reset_position()
            desc = "Reset mouse a (0,0)"

        packets.append({
            "timestamp": t,
            "direction": "out",
            "description": desc,
            "bytes": list(reset_packet)
        })
        t += 0.050  # Esperar 50ms después del reset

    # Paquete 1: Mover a la posición
    move_packet = protocol.move_absolute(x, y)
    packets.append({
        "timestamp": t,
        "direction": "out",
        "description": f"Mover a ({x}, {y})",
        "bytes": list(move_packet)
    })
    t += 0.100

    # Paquete 2: Presionar botón
    if button.lower() == "left":
        down_packet = protocol.left_down()
        desc = "Click izquierdo DOWN"
    else:
        down_packet = protocol.right_down()
        desc = "Click derecho DOWN"

    packets.append({
        "timestamp": t,
        "direction": "out",
        "description": desc,
        "bytes": list(down_packet)
    })
    t += 0.065  # Tiempo promedio de click (50-80ms)

    # Paquete 3: Soltar botón
    if button.lower() == "left":
        up_packet = protocol.left_up()
        desc = "Click izquierdo UP"
    else:
        up_packet = protocol.right_up()
        desc = "Click derecho UP"

    packets.append({
        "timestamp": t,
        "direction": "out",
        "description": desc,
        "bytes": list(up_packet)
    })

    # Guardar JSON
    with open(output_file, 'w') as f:
        json.dump(packets, f, indent=2)

    print(f"✅ Archivo generado: {output_file}")
    print(f"   Click {button} en ({x}, {y})")
    print(f"   Resolución: {screen_width}x{screen_height}")
    print(f"   Total paquetes: {len(packets)}")
    print()
    print(f"Para ejecutar:")
    print(f"  python replay_imouse.py {output_file}")


def generate_double_click_json(x: int, y: int, output_file: str,
                               screen_width: int = 365, screen_height: int = 667):
    """Genera JSON para doble click"""

    protocol = iMouseHIDProtocol(screen_width=screen_width, screen_height=screen_height)

    packets = []
    t = 0.0

    # Mover
    move_packet = protocol.move_absolute(x, y)
    packets.append({
        "timestamp": t,
        "direction": "out",
        "description": f"Mover a ({x}, {y})",
        "bytes": list(move_packet)
    })

    # Primer click
    t += 0.100
    packets.append({
        "timestamp": t,
        "direction": "out",
        "description": "Primer click DOWN",
        "bytes": list(protocol.left_down())
    })

    t += 0.065
    packets.append({
        "timestamp": t,
        "direction": "out",
        "description": "Primer click UP",
        "bytes": list(protocol.left_up())
    })

    # Pausa entre clicks (150ms)
    t += 0.150

    # Segundo click
    packets.append({
        "timestamp": t,
        "direction": "out",
        "description": "Segundo click DOWN",
        "bytes": list(protocol.left_down())
    })

    t += 0.065
    packets.append({
        "timestamp": t,
        "direction": "out",
        "description": "Segundo click UP",
        "bytes": list(protocol.left_up())
    })

    # Guardar
    with open(output_file, 'w') as f:
        json.dump(packets, f, indent=2)

    print(f"✅ Archivo generado: {output_file}")
    print(f"   Doble click en ({x}, {y})")
    print(f"   Total paquetes: {len(packets)}")


def generate_drag_json(x1: int, y1: int, x2: int, y2: int, output_file: str,
                      screen_width: int = 365, screen_height: int = 667):
    """Genera JSON para arrastrar desde (x1,y1) hasta (x2,y2)"""

    protocol = iMouseHIDProtocol(screen_width=screen_width, screen_height=screen_height)

    packets = []
    t = 0.0

    # Mover al inicio
    packets.append({
        "timestamp": t,
        "direction": "out",
        "description": f"Mover a ({x1}, {y1})",
        "bytes": list(protocol.move_absolute(x1, y1))
    })

    # Presionar botón
    t += 0.100
    packets.append({
        "timestamp": t,
        "direction": "out",
        "description": "Presionar botón izquierdo",
        "bytes": list(protocol.left_down())
    })

    # Mover al destino (con botón presionado)
    t += 0.050
    packets.append({
        "timestamp": t,
        "direction": "out",
        "description": f"Arrastrar a ({x2}, {y2})",
        "bytes": list(protocol.move_absolute(x2, y2, button=ButtonState.LEFT))
    })

    # Soltar botón
    t += 0.100
    packets.append({
        "timestamp": t,
        "direction": "out",
        "description": "Soltar botón",
        "bytes": list(protocol.left_up())
    })

    # Guardar
    with open(output_file, 'w') as f:
        json.dump(packets, f, indent=2)

    print(f"✅ Archivo generado: {output_file}")
    print(f"   Arrastrar desde ({x1}, {y1}) hasta ({x2}, {y2})")
    print(f"   Total paquetes: {len(packets)}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Genera archivos JSON para replay_imouse.py',
        epilog='Ejemplos:\n'
               '  python generate_click_json.py -x 300 -y 300 -o click.json\n'
               '  python generate_click_json.py -x 100 -y 200 --double -o dclick.json\n'
               '  python generate_click_json.py -x1 100 -y1 100 -x2 500 -y2 500 --drag -o drag.json',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-x', '--x', type=int, help='Coordenada X')
    parser.add_argument('-y', '--y', type=int, help='Coordenada Y')
    parser.add_argument('-x1', type=int, help='Coordenada X inicial (para drag)')
    parser.add_argument('-y1', type=int, help='Coordenada Y inicial (para drag)')
    parser.add_argument('-x2', type=int, help='Coordenada X final (para drag)')
    parser.add_argument('-y2', type=int, help='Coordenada Y final (para drag)')
    parser.add_argument('-o', '--output', required=True, help='Archivo JSON de salida')
    parser.add_argument('-w', '--width', type=int, default=365, help='Ancho de pantalla (default: 365 - iPhone portrait)')
    parser.add_argument('--height', type=int, default=667, help='Alto de pantalla (default: 667 - iPhone portrait)')
    parser.add_argument('--button', choices=['left', 'right'], default='left', help='Botón del mouse')
    parser.add_argument('--double', action='store_true', help='Generar doble click')
    parser.add_argument('--drag', action='store_true', help='Generar drag & drop')
    parser.add_argument('--no-reset', action='store_true', help='No resetear posición antes de mover')
    parser.add_argument('--restart', action='store_true', help='Usar HT_Restart (0xa4) en lugar de reset normal')

    args = parser.parse_args()

    reset = not args.no_reset
    use_restart = args.restart

    if args.drag:
        if not all([args.x1, args.y1, args.x2, args.y2]):
            parser.error("--drag requiere -x1, -y1, -x2, -y2")
        generate_drag_json(args.x1, args.y1, args.x2, args.y2, args.output, args.width, args.height)
    elif args.double:
        if not all([args.x, args.y]):
            parser.error("--double requiere -x y -y")
        generate_double_click_json(args.x, args.y, args.output, args.width, args.height)
    else:
        if not all([args.x, args.y]):
            parser.error("Se requiere -x y -y")
        generate_click_json(args.x, args.y, args.output, args.width, args.height, args.button, reset, use_restart)


if __name__ == "__main__":
    main()
