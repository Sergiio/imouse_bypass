# 🖱️ iMouse Bypass - Control Remoto para iPhone/iPad

Suite de herramientas para controlar iPhone/iPad desde Windows usando el protocolo iMouse HID.

## 📁 Estructura del Proyecto

```
imouse-bypass/
├── 📂 docs/           # Documentación técnica
├── 📂 samples/        # Archivos JSON de ejemplo
├── 📂 scripts/        # Scripts de análisis y utilidades
└── 🐍 *.py           # Scripts principales
```

## 🚀 Scripts Principales

### 1. **imouse_typer.py** - Escritor de Texto
Envía texto al iPhone en modo bucle continuo.
```bash
python imouse_typer.py
```
- Escribe texto y pulsa ENTER para enviarlo
- Comandos: `exit`, `clear`, `speed 0.05`

### 2. **imouse_realtime.py** - Modo Espejo en Tiempo Real
Replica cada tecla que presiones instantáneamente en el iPhone.
```bash
python imouse_realtime.py
```
- Presiona **F9** para activar/desactivar
- Todo lo que teclees se envía en tiempo real

### 3. **imouse_clicker.py** - Control de Mouse
Envía clicks a coordenadas específicas.
```bash
python imouse_clicker.py
```
- Formato: `300, 30` para click simple
- `double 300, 30` para doble click
- `drag 100, 100, 500, 500` para arrastrar

### 4. **imouse_shortcuts.py** - Atajos de Teclado
Envía atajos del sistema iOS.
```bash
python imouse_shortcuts.py
```
Atajos disponibles:
- `h` → Home (Win+H)
- `s` → Search (Win+Space)
- `p` → Screenshot (Win+Shift+3)

## 🔧 Scripts de Utilidad

### **generate_click_json.py**
Genera archivos JSON para clicks personalizados:
```bash
python generate_click_json.py -x 300 -y 300 -o samples/mi_click.json
```

### **replay_imouse.py**
Reproduce archivos JSON guardados:
```bash
python replay_imouse.py samples/click_300_300.json
```

### **imouse_complete_keymap.py**
Genera archivos JSON para texto:
```bash
python imouse_complete_keymap.py "Hola Mundo" -o samples/texto.json
```

## 📋 Requisitos

```bash
pip install pywinusb
pip install pynput  # Solo para imouse_realtime.py
```

## 🎯 Guía Rápida de Uso

### Escribir texto continuamente:
```bash
python imouse_typer.py
# Escribe y presiona Enter para enviar
```

### Hacer click en posición específica:
```bash
python imouse_clicker.py
# Ingresa: 300, 30
```

### Ir a la pantalla de inicio:
```bash
python imouse_shortcuts.py
# Presiona: h
```

### Modo espejo (tiempo real):
```bash
python imouse_realtime.py
# Presiona F9 para activar
```

## 📱 Resoluciones Soportadas

- **iPhone Portrait**: 365x667 (por defecto)
- **iPhone Landscape**: 667x365
- **iPad Portrait**: 768x1024
- **iPad Landscape**: 1024x768

Puedes cambiar la resolución en `imouse_clicker.py` con:
```
res 768x1024
```

## ⚙️ Configuración del Dispositivo

- **Vendor ID**: 0x720a
- **Product ID**: 0x3dab
- **Report Size**: 9 bytes (teclado) / 9 bytes (mouse)

## 📚 Documentación

Ver carpeta `docs/` para documentación técnica detallada:
- Protocolo HID completo
- Análisis de Ghidra
- Mapeo de teclas y scancodes
- Resoluciones y coordenadas

## 🛠️ Desarrollo

El protocolo principal está implementado en:
- `imouse_hid_protocol.py` - Protocolo de mouse
- `imouse_complete_keymap.py` - Mapeo de teclado

## ⚠️ Notas Importantes

1. El dispositivo iMouse debe estar conectado por USB
2. Windows puede requerir permisos de administrador
3. No uses el modo tiempo real mientras cambias de ventana
4. Algunos atajos solo funcionan en iPadOS

## 🤝 Contribuciones

Este proyecto es resultado de ingeniería inversa del protocolo iMouse.
Los scripts están optimizados para uso práctico y educativo.

---
*Desarrollado mediante análisis del protocolo HID de iMouse*