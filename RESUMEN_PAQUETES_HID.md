# Resumen Rápido - Paquetes HID de iMouse

## Estructura General (9 bytes)

```
┌────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ 00 │CMD │BTN │ X0 │ X1 │ X2 │ Y0 │ Y1 │ 00 │
└────┴────┴────┴────┴────┴────┴────┴────┴────┘
  0    1    2    3    4    5    6    7    8

00:  Padding (siempre 0x00)
CMD: Comando (0xa0 o 0xa1)
BTN: Button State (0=none, 1=left, 2=right)
X0-X2: Datos X (absoluto: 2 bytes, relativo: 3 bytes)
Y0-Y1: Datos Y (2 bytes)
```

---

## Comandos Confirmados

### 0xa0 - Movimiento Absoluto
Coordenadas normalizadas (0-32767)

### 0xa1 - Movimiento Relativo
Deltas con signo (complemento a dos)

### Button States
- **0x00**: Sin botón presionado
- **0x01**: Botón izquierdo presionado
- **0x02**: Botón derecho presionado

---

## Ejemplos de Paquetes Comunes

### Movimiento Simple

**Mover al centro absoluto (960, 540 en 1920x1080):**
```
00 a0 00 ff 3f ff 3f 00 00
   │  │  └───┴───┴─── Y normalizado: 16383 (0x3fff)
   │  └─────────────── Button: none (0)
   └────────────────── Comando: absoluto (0xa0)
```

**Mover +100px relativo a la derecha:**
```
00 a1 00 64 00 00 00 00 00
   │  │  └───┴───┴─── Delta X: +100 (0x000064)
   │  └─────────────── Button: none (0)
   └────────────────── Comando: relativo (0xa1)
```

**Mover -50px relativo (izquierda):**
```
00 a1 00 ce ff ff e2 ff 00
   │  │  └───┴───┴─── Delta X: -50 (0xffffce en complemento a dos)
   │  │              └─ Delta Y: -30 (0xffe2)
   │  └─────────────── Button: none (0)
   └────────────────── Comando: relativo (0xa1)
```

---

### Clicks

**Click izquierdo DOWN:**
```
00 a1 01 00 00 00 00 00 00
   │  │  └───┴───┴─── Sin movimiento
   │  └─────────────── Button: LEFT (1) ✓
   └────────────────── Comando: relativo (0xa1)
```

**Click izquierdo UP:**
```
00 a1 00 00 00 00 00 00 00
   │  │  └───┴───┴─── Sin movimiento
   │  └─────────────── Button: NONE (0) - soltado
   └────────────────── Comando: relativo (0xa1)
```

**Click derecho DOWN:**
```
00 a1 02 00 00 00 00 00 00
   │  │  └───┴───┴─── Sin movimiento
   │  └─────────────── Button: RIGHT (2) ✓
   └────────────────── Comando: relativo (0xa1)
```

**Click derecho UP:**
```
00 a1 00 00 00 00 00 00 00
   (igual que click izquierdo UP)
```

---

### Operaciones Avanzadas

**Arrastrar (drag) - mover con botón presionado:**
```
1. 00 a1 01 00 00 00 00 00 00    ← LEFT DOWN
2. 00 a1 01 32 00 00 1e 00 00    ← Mover +50,+30 con botón presionado
                └─ Button: LEFT (1) permanece
3. 00 a1 00 00 00 00 00 00 00    ← LEFT UP
```

---

## Flujo Típico de Click

### Según `HT_LeftClick()`:

```c
1. HT_LeftDown()      → 00 a1 01 00 00 00 00 00 00
2. Sleep(50-80ms)     → (aleatorio para simular humano)
3. HT_LeftUp()        → 00 a1 00 00 00 00 00 00 00
```

### Timing Crítico

- **Entre comandos**: `WaitForSingleObject(100ms)`
- **Down → Up**: `Sleep(rand() % 31 + 50)` = **50-80ms**
- **Timeout HID**: `hid_write_timeout(..., 500ms)`

---

## Protocolo Alternativo (11 bytes)

Usado cuando `*(void**)((int)param_3 + 0x21f) != NULL`

### Estructura
```
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ 57 │ AB │ 00 │ TY │ ST │ LN │BTN │ D0 │ D1 │ D2 │ CS │
└────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
  0    1    2    3    4    5    6    7    8    9   10

57 AB:  Magic header ('W' 0xAB)
TY:     Type (0x04 o 0x05)
ST:     Subtype (0x07 o 0x05)
LN:     Length
BTN:    Button state (0/1/2)
D0-D2:  Data/delta
CS:     Checksum
```

### Ejemplo - Click izquierdo alternativo:
```
57 ab 00 05 05 01 01 00 00 00 0e
   │     │  │  │  │           └─ Checksum: 0x0e
   │     │  │  │  └──────────── Button: LEFT (1)
   │     │  │  └─────────────── Length: 1
   │     │  └────────────────── Subtype: 0x05
   │     └───────────────────── Type: 0x05
   └─────────────────────────── Magic: 'W' 0xAB
```

---

## Notas de Implementación

1. **Normalización de coordenadas absolutas:**
   ```
   x_normalized = (x_pixels / screen_width) * 32767
   y_normalized = (y_pixels / screen_height) * 32767
   ```

2. **Complemento a dos para deltas negativos:**
   ```
   if delta < 0:
       delta = (1 << 24) + delta  # Para X (24 bits)
       delta = (1 << 16) + delta  # Para Y (16 bits)
   ```

3. **Orden de bytes (little-endian):**
   ```
   Valor: 0x1234
   Bytes: [0x34, 0x12]
   ```

---

## Herramientas de Análisis

- **Ghidra**: Para decompilación de MouseKeyItem.dll
- **Wireshark/USBPcap**: Para captura de tráfico HID
- **Python script**: `/mnt/c/imouse/imouse_hid_protocol.py`

### Filtro Wireshark recomendado:
```
usb.endpoint_address.direction == OUT && usb.transfer_type == 0x01
```

---

## Referencias de Funciones (MouseKeyItem.dll)

| Función | Offset | Descripción |
|---------|--------|-------------|
| `HT_MoveToAA` | 0x81d0 | Movimiento con suavizado |
| `HT_LeftClick` | 0x3870 | Click izquierdo completo |
| `HT_LeftDown` | 0x34f0 | Presionar botón izquierdo |
| `HT_LeftUp` | (estimado) | Soltar botón izquierdo |
| `HT_RightDown` | 0x38a0 | Presionar botón derecho |
| `HT_RightUp` | (estimado) | Soltar botón derecho |

---

## Generación de Paquetes con Python

```python
from imouse_hid_protocol import iMouseHIDProtocol, ButtonState

protocol = iMouseHIDProtocol(screen_width=1920, screen_height=1080)

# Movimiento
packet = protocol.move_absolute(960, 540)
packet = protocol.move_relative(100, 50)

# Clicks
down, up = protocol.click_left()
down, up = protocol.click_right()

# Arrastrar
protocol.left_down()
packet = protocol.move_relative(100, 50)  # Mover con botón presionado
protocol.left_up()
```
