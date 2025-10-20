# Resolución iPhone para iMouse

## 📱 Tu iPhone: 365 x 667 píxeles (Portrait/Vertical)

Esta es la resolución que se usa por defecto para generar todos los clicks.

```
  365px ancho
  ┌─────┐
  │     │
  │     │ 667px
  │     │ alto
  │     │
  └─────┘
```

---

## 🎯 Generar Clicks (Resolución Automática)

Por defecto, todos los comandos usan **365x667** automáticamente:

### Click Simple

```bash
# Click en (300, 300) - usa 365x667 por defecto
python generate_click_json.py -x 300 -y 300 -o click.json
python replay_imouse.py click.json
```

### Click en Diferentes Posiciones

```bash
# Esquina superior izquierda (50, 50)
python generate_click_json.py -x 50 -y 50 -o click_tl.json

# Centro de la pantalla (182, 333)
python generate_click_json.py -x 182 -y 333 -o click_center.json

# Esquina inferior derecha (315, 617)
python generate_click_json.py -x 315 -y 617 -o click_br.json
```

### Opciones Adicionales

```bash
# Sin reset (relativo a posición actual)
python generate_click_json.py -x 300 -y 300 --no-reset -o click.json

# Click derecho
python generate_click_json.py -x 300 -y 300 --button right -o right.json

# Doble click
python generate_click_json.py -x 300 -y 300 --double -o dclick.json

# Arrastrar
python generate_click_json.py -x1 100 -y1 100 -x2 200 -y2 500 --drag -o drag.json
```

---

## 📐 Sistema de Coordenadas

```
iPhone Portrait (365 x 667)

(0,0) ┌─────────┐ (365,0)
      │         │
      │ (182,   │
      │  333)   │  Centro
      │    •    │
      │         │
      │         │
(0,667)└─────────┘ (365,667)
```

---

## 🔄 Normalización de Coordenadas

El protocolo iMouse convierte las coordenadas de píxeles a un rango 0-32767:

```
X_normalizado = (X_pixels / 365) * 32767
Y_normalizado = (Y_pixels / 667) * 32767
```

### Ejemplos:

| Posición | Píxeles (x,y) | Normalizado (x,y) | Bytes X | Bytes Y |
|----------|---------------|-------------------|---------|---------|
| Esquina TL | (0, 0) | (0, 0) | [0, 0] | [0, 0] |
| Centro | (182, 333) | (16345, 16367) | [233, 63] | [239, 63] |
| Click actual | (300, 300) | (26931, 14732) | [51, 105] | [156, 57] |
| Esquina BR | (365, 667) | (32767, 32767) | [255, 127] | [255, 127] |

---

## ⚙️ Cambiar Resolución (Landscape/Horizontal)

Si usas el iPhone en horizontal (667x365):

```bash
python generate_click_json.py -x 300 -y 300 -w 667 --height 365 -o click.json
```

O para iPad u otras resoluciones:

```bash
# iPad (1024x768)
python generate_click_json.py -x 500 -y 400 -w 1024 --height 768 -o click.json
```

---

## 💡 Verificar Coordenadas

Para ver las coordenadas normalizadas sin ejecutar:

```bash
python generate_click_json.py -x 300 -y 300 -o test.json
cat test.json
```

Busca el paquete "Mover a (300, 300)" y verás los bytes normalizados.

---

## 📊 Archivo Actual

El archivo `click_300_300.json` está generado con la resolución correcta (365x667):

```bash
python replay_imouse.py click_300_300.json
```

Esto hará:
1. Reset a (0, 0)
2. Mover a (300, 300) - normalizado para iPhone 365x667
3. Click izquierdo DOWN
4. Click izquierdo UP

---

## 🔍 Resoluciones Comunes de iPhone

| Dispositivo | Portrait | Landscape |
|-------------|----------|-----------|
| iPhone 6/7/8/SE | 375 x 667 | 667 x 375 |
| iPhone 6+/7+/8+ | 414 x 736 | 736 x 414 |
| iPhone X/XS/11 Pro | 375 x 812 | 812 x 375 |
| iPhone 12/13/14 | 390 x 844 | 844 x 390 |

Si tu iPhone es diferente, ajusta con `-w` y `--height`.
