# 📡 Protocolo iMouse - Documentación Completa

## 🔄 Flujo de Comunicación

```
┌─────────────┐         ┌──────────────┐        ┌─────────────┐        ┌──────────┐
│   PC/App    │  USB    │ Dispositivo  │  USB   │ iMouseSrv   │  WiFi  │  iPhone  │
│  (Scripts)  │────────▶│   Virtual    │───────▶│   .exe      │───────▶│   iOS    │
│             │         │ 0x720a:0x3dab│        │ (Servidor)  │WebSock │          │
└─────────────┘         └──────────────┘        └─────────────┘        └──────────┘
```

## 📦 Formato del Paquete USB

### Estructura (9 bytes)

```
┌────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ 00 │ a1 │ MM │ 00 │ KK │ 00 │ 00 │ 00 │ 00 │
└────┴────┴────┴────┴────┴────┴────┴────┴────┘
  │    │    │    │    │    └─────────────────┘
  │    │    │    │    │       Padding (4 bytes)
  │    │    │    │    └─ Scancode (HID)
  │    │    │    └─ Reserved (siempre 0x00)
  │    │    └─ Modifier Byte
  │    └─ Marcador iMouse (0xa1)
  └─ Report ID (0x00)
```

### Byte 0: Report ID
- **Valor**: `0x00`
- **Función**: Identificador requerido por el dispositivo HID

### Byte 1: Marcador de Protocolo
- **Valor**: `0xa2` ⚠️ **CONFIRMADO POR GHIDRA**
- **Función**: Indica que es un comando de teclado iMouse
- **Nota**: Código fuente muestra `local_57 = 0xa2` en FUN_100024b0
- **Otros valores posibles**:
  - `0xa1`: Posiblemente protocolo alternativo o comandos especiales
  - `0xa3`: Otros comandos especiales

### Byte 2: Modificadores
Bitfield que indica qué teclas modificadoras están presionadas:

| Bit | Valor | Tecla         |
|-----|-------|---------------|
| 0   | 0x01  | Left Ctrl     |
| 1   | 0x02  | Left Shift    |
| 2   | 0x04  | Left Alt      |
| 3   | 0x08  | Left Win/Cmd  |
| 4   | 0x10  | Right Ctrl    |
| 5   | 0x20  | Right Shift   |
| 6   | 0x40  | Right Alt     |
| 7   | 0x80  | Right Win/Cmd |

**Ejemplos**:
- `0x00`: Sin modificadores
- `0x02`: Shift presionado (mayúsculas)
- `0x01`: Ctrl presionado
- `0x03`: Ctrl + Shift (0x01 | 0x02)

### Byte 3: Reserved
- **Valor**: `0x00`
- **Función**: Reservado, siempre cero

### Byte 4: Scancode
- **Formato**: HID Keyboard Scancode estándar
- **Valores comunes**:

```
0x04 = 'a'   0x0b = 'h'   0x12 = 'o'   0x19 = 'v'
0x05 = 'b'   0x0c = 'i'   0x13 = 'p'   0x1a = 'w'
0x06 = 'c'   0x0d = 'j'   0x14 = 'q'   0x1b = 'x'
0x07 = 'd'   0x0e = 'k'   0x15 = 'r'   0x1c = 'y'
0x08 = 'e'   0x0f = 'l'   0x16 = 's'   0x1d = 'z'
0x09 = 'f'   0x10 = 'm'   0x17 = 't'   0x1e = '1'
0x0a = 'g'   0x11 = 'n'   0x18 = 'u'   ...

0x28 = Enter    0x2c = Space    0x2b = Tab
0x2a = Backspace
```

### Bytes 5-8: Padding
- **Valor**: `0x00`
- **Función**: Relleno hasta completar 9 bytes

## 🔑 Ejemplos de Paquetes

### Ejemplo 1: Letra 'H' mayúscula
```
00 a2 02 00 0b 00 00 00 00
│  │  │  │  │
│  │  │  │  └─ Scancode: 0x0b ('h')
│  │  │  └─ Reserved
│  │  └─ Shift presionado (0x02)
│  └─ Marcador iMouse (0xa2)
└─ Report ID
```

### Ejemplo 2: Letra 'o' minúscula
```
00 a2 00 00 12 00 00 00 00
│  │  │  │  │
│  │  │  │  └─ Scancode: 0x12 ('o')
│  │  │  └─ Reserved
│  │  └─ Sin modificadores
│  └─ Marcador iMouse (0xa2)
└─ Report ID
```

### Ejemplo 3: Ctrl+C (Copiar)
```
00 a2 01 00 06 00 00 00 00
│  │  │  │  │
│  │  │  │  └─ Scancode: 0x06 ('c')
│  │  │  └─ Reserved
│  │  └─ Ctrl presionado (0x01)
│  └─ Marcador iMouse (0xa2)
└─ Report ID
```

### Ejemplo 4: Release (liberar todas las teclas)
```
00 a2 00 00 00 00 00 00 00
│  │  │  │  │
│  │  │  │  └─ Sin tecla
│  │  │  └─ Reserved
│  │  └─ Sin modificadores
│  └─ Marcador iMouse (0xa2)
└─ Report ID
```

## 🌐 Procesamiento en iMouseSrv.exe

1. **Recepción USB**: iMouseSrv.exe lee los paquetes del dispositivo virtual USB
2. **Decodificación**: Interpreta el byte marcador (0xa1), modificadores y scancode
3. **Traducción**: Convierte el scancode HID a comandos de teclado de iOS
4. **Envío WebSocket**: Transmite el comando al iPhone vía WiFi/AirPlay
5. **Ejecución**: El iPhone ejecuta la pulsación de tecla

## 📱 Comunicación con iPhone

### Tecnologías Usadas
- **AirPlay**: Para descubrimiento y conexión inicial
- **mDNS**: Para descubrimiento de dispositivos en la red local
- **WebSockets**: Para envío de comandos en tiempo real
- **HTTP**: Para interfaz web de control

### Comandos WebSocket (extraídos de las strings)
```javascript
// Formato de mensajes WebSocket
ws.onopen = function() { ... }
ws.send("move," + x + "," + y);           // Movimiento de mouse
ws.send("click," + button);               // Click
ws.send("key," + scancode + "," + mod);   // Tecla
```

## 🔧 Funciones del DLL (MouseKeyItem.dll)

### Funciones de Teclado
- `CusKeyInput_DownUP`: Simula presionar y soltar tecla
- `CusKeyInput_FunKeyEx`: Teclas de función extendidas
- `CusKeyInput_InputStringEx2`: Entrada de cadenas de texto
- `CusKeyInput_Union_KeyEx`: Combinaciones de teclas
- `Group_CusKeyInput_StringEx2`: Entrada de grupo
- `Group_CusKeyInput_Union_KeyEx`: Combinaciones de grupo

### Funciones de Mouse
- `opMouseMove`: Mover cursor
- `opMouseXY`: Posicionar cursor en X,Y
- `opMouseReset`: Resetear posición
- `opMouseClick`: Simular click
- `cmd_MouseMove`: Comando de movimiento
- `cmd_MouseXY`: Comando de posicionamiento

### Funciones HID
- `openHID`: Abrir dispositivo HID
- `closeHID`: Cerrar dispositivo HID
- `bindMouse`: Vincular mouse
- `hid_open`: Abrir dispositivo
- `hid_open_path`: Abrir por ruta

## 🚀 Uso Práctico

### 1. Enviar una tecla simple
```python
import pywinusb.hid as hid

# Conectar al dispositivo
devices = hid.HidDeviceFilter(vendor_id=0x720a, product_id=0x3dab).get_devices()
device = devices[0]
device.open()

# Obtener output report
out_report = device.find_output_reports()[0]

# Enviar 'H' mayúscula (Shift + h)
packet = [0x00, 0xa1, 0x02, 0x00, 0x0b, 0x00, 0x00, 0x00, 0x00]
out_report.set_raw_data(packet)
out_report.send()

# Release
release = [0x00, 0xa1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
out_report.set_raw_data(release)
out_report.send()

device.close()
```

### 2. Escribir texto completo
Usar el script `text_to_hid_json.py`:
```bash
python3 text_to_hid_json.py "Hola Mundo" -o hola.json
python3 replay_imouse.py hola.json
```

## ⚠️ Requisitos

1. **Dispositivo Virtual**: El driver `老猫子虚拟设备` debe estar instalado
2. **Servicio iMouseSrv**: Debe estar corriendo para procesar comandos
3. **iPhone Conectado**: Debe estar conectado por AirPlay al PC
4. **Misma Red WiFi**: PC e iPhone en la misma red

## 🔬 Investigación Futura

### Protocolo de Mouse
El byte marcador `0xa2` probablemente indica comandos de mouse:
```
00 a2 BB XX YY ZZ WW 00 00
   │  │  └───┴───┴───┘
   │  │      Coordenadas X,Y y Wheel
   │  └─ Botones presionados
   └─ Marcador mouse
```

### Comandos Especiales
El byte `0xa3` u otros valores podrían indicar:
- Gestos multitouch
- Comandos de sistema (Home, Sleep, etc.)
- Configuración del dispositivo

### Captura de Respuestas
El dispositivo puede enviar respuestas INPUT al host:
- Estado de conexión con iPhone
- Confirmaciones de comandos
- Estado de batería del iPhone
- Errores

## 📚 Referencias

- **HID Usage Tables**: [USB.org HID Specification](https://www.usb.org/hid)
- **AirPlay Protocol**: Propietario de Apple
- **WebSocket RFC**: [RFC 6455](https://tools.ietf.org/html/rfc6455)
