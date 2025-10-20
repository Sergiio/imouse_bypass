# Cómo Hacer Click en iMouse

## 📦 Archivos Necesarios

Ya tienes todo listo en `/mnt/c/imouse/`:

1. **`replay_imouse.py`** - Script que envía paquetes al dispositivo USB
2. **`imouse_hid_protocol.py`** - Generador de paquetes HID
3. **`generate_click_json.py`** - Generador de archivos JSON
4. **`click_300_300.json`** - JSON listo para click en (300, 300)

---

## 🚀 Uso Rápido

### Opción 1: Usar el JSON ya generado

El archivo `click_300_300.json` ya está listo para hacer click en (300, 300):

```bash
python replay_imouse.py click_300_300.json
```

### Opción 2: Generar JSON para otras posiciones

```bash
# Click en (500, 400)
python generate_click_json.py -x 500 -y 400 -o click_500_400.json
python replay_imouse.py click_500_400.json

# Click derecho en (100, 200)
python generate_click_json.py -x 100 -y 200 --button right -o right_click.json
python replay_imouse.py right_click.json

# Doble click en (600, 300)
python generate_click_json.py -x 600 -y 300 --double -o double_click.json
python replay_imouse.py double_click.json

# Arrastrar desde (100,100) hasta (500,500)
python generate_click_json.py -x1 100 -y1 100 -x2 500 -y2 500 --drag -o drag.json
python replay_imouse.py drag.json
```

---

## 📋 Requisitos Previos

### 1. Instalar pywinusb (Windows)

```bash
pip install pywinusb
```

### 2. Conectar el dispositivo iMouse

- VID: `0x720a`
- PID: `0x3dab`

Verificar que esté conectado:

```bash
python replay_imouse.py --help
```

---

## 📄 Contenido de click_300_300.json

```json
[
  {
    "timestamp": 0.000,
    "direction": "out",
    "description": "Mover a (300, 300)",
    "bytes": [0x00, 0xa0, 0x00, 0xff, 0x13, 0x8d, 0x23, 0x00, 0x00]
  },
  {
    "timestamp": 0.100,
    "direction": "out",
    "description": "Click izquierdo DOWN",
    "bytes": [0x00, 0xa1, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
  },
  {
    "timestamp": 0.165,
    "direction": "out",
    "description": "Click izquierdo UP",
    "bytes": [0x00, 0xa1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
  }
]
```

---

## 🔧 Resolución de Pantalla

Por defecto usa **1920x1080**. Para cambiar:

```bash
python generate_click_json.py -x 300 -y 300 -w 2560 -h 1440 -o click.json
```

---

## 🎯 Estructura del Paquete HID

### Movimiento (0xa0)
```
00 a0 00 ff 13 8d 23 00 00
│  │  │  └──┴──┴──┴──── Coordenadas normalizadas
│  │  └───────────────── Button state (0=none)
│  └──────────────────── Comando (0xa0 = absoluto)
└─────────────────────── Report ID (0x00)
```

### Click DOWN (0xa1)
```
00 a1 01 00 00 00 00 00 00
│  │  │  └──┴──┴──┴──── Sin movimiento
│  │  └───────────────── Button state (1=LEFT, 2=RIGHT)
│  └──────────────────── Comando (0xa1 = relativo)
└─────────────────────── Report ID (0x00)
```

### Click UP (0xa1)
```
00 a1 00 00 00 00 00 00 00
│  │  │  └──┴──┴──┴──── Sin movimiento
│  │  └───────────────── Button state (0=none, soltado)
│  └──────────────────── Comando (0xa1 = relativo)
└─────────────────────── Report ID (0x00)
```

---

## 🐛 Solución de Problemas

### Error: Dispositivo no encontrado

```
❌ Dispositivo no encontrado: 0x720a:0x3dab
```

**Solución:**
1. Verifica que el dispositivo esté conectado
2. Comprueba VID:PID en el Administrador de dispositivos
3. Usa los parámetros `-v` y `-p` si son diferentes:

```bash
python replay_imouse.py click_300_300.json -v 0x1234 -p 0x5678
```

### Error: pywinusb no instalado

```
❌ Error: pywinusb no está instalado
```

**Solución:**
```bash
pip install pywinusb
```

### No pasa nada al ejecutar

**Solución:**
- Verifica que el otro PC (con el iPhone) tenga iMouseSrv.exe corriendo
- Asegúrate de estar en Windows (no WSL) al ejecutar `replay_imouse.py`
- Comprueba que el JSON tenga el formato correcto

---

## 📚 Documentación Completa

- **PROTOCOLO_IMOUSE_HID.md** - Análisis completo del protocolo
- **RESUMEN_PAQUETES_HID.md** - Referencia rápida de paquetes
- **imouse_hid_protocol.py** - API Python para generar paquetes

---

## 💡 Ejemplos Avanzados

### Secuencia de múltiples clicks

Crear JSON manualmente combinando paquetes:

```json
[
  {"timestamp": 0.000, "direction": "out", "description": "Click 1", "bytes": [...]},
  {"timestamp": 0.500, "direction": "out", "description": "Click 2", "bytes": [...]},
  {"timestamp": 1.000, "direction": "out", "description": "Click 3", "bytes": [...]}
]
```

### Velocidad de reproducción

```bash
# Reproducir 2x más rápido
python replay_imouse.py click_300_300.json --speed 2.0

# Reproducir en cámara lenta (0.5x)
python replay_imouse.py click_300_300.json --speed 0.5
```

---

## ✅ Checklist

- [ ] pywinusb instalado
- [ ] Dispositivo iMouse conectado (0x720a:0x3dab)
- [ ] JSON generado con coordenadas correctas
- [ ] Ejecutar desde Windows (no WSL)
- [ ] iMouseSrv.exe corriendo en el otro PC (si aplica)
