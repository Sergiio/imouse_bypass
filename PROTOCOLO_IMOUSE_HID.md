# Protocolo iMouse HID - Análisis Completo

## Resumen
iMousePro utiliza comunicación HID para enviar comandos de mouse desde el PC al dispositivo móvil. Se identificaron dos protocolos principales y dos modos de movimiento.

---

## 1. MOVIMIENTO ABSOLUTO (Comando 0xa0)

### Cuándo se usa
- Cuando `*(int*)(param_3 + 0x223) == 1` (modo absoluto activado)
- Movimiento directo sin suavizado
- También usado por `HT_LeftDown` en modo absoluto

### Estructura del paquete HID (9 bytes)
```
Offset  Tamaño  Descripción                     Valor
------  ------  ------------------------------- -------------------------
0x00    1       Siempre 0x00 (memset)          0x00
0x01    1       Comando                         0xa0 (movimiento absoluto)
0x02    1       Button State                    0=ninguno, 1=izq, 2=der
0x03    2       Coordenada X normalizada        (X / screen_width) * 32767
0x05    2       Coordenada Y normalizada        (Y / screen_height) * 32767
0x07    2       Padding                         0x0000
```

### Código decompilado relevante
```c
memset(&local_90, 0, 0x40);
local_8f = 0xa0;                                          // Comando
local_8e = local_129;                                     // Device ID
local_8d = (short)(((float)param_1 / (float)iVar9) * 32767.0);  // X normalizado
local_8b = (undefined1)iVar6;                             // Y normalizado (byte bajo)
uStack_8a = (undefined1)((uint)iVar6 >> 8);               // Y normalizado (byte alto)
local_89 = 0;                                             // Padding

hid_write_timeout((short*)*local_120, &local_90, 9, 500);
WaitForSingleObject(*(HANDLE*)((int)puVar5 + 0x20d), 100);
```

### Normalización de coordenadas
- Rango de entrada: 0 - screen_width/height (píxeles)
- Rango de salida: 0 - 32767 (0x7FFF)
- Fórmula: `normalized = (coord / screen_dimension) * 32767`

---

## 2. MOVIMIENTO RELATIVO/INCREMENTAL (Comando 0xa1)

### Cuándo se usa
- Modo predeterminado cuando `*(int*)(param_3 + 0x223) != 1`
- Proporciona suavizado y simulación de movimiento humano
- Utiliza perfiles de aceleración

### Estructura del paquete HID (9 bytes)
```
Offset  Tamaño  Descripción                     Valor
------  ------  ------------------------------- -------------------------
0x00    1       Padding                         0x00
0x01    1       Comando                         0xa1 (movimiento relativo)
0x02    1       Button State                    0=ninguno, 1=izq, 2=der
0x03    1       Delta X (byte bajo)             delta_x & 0xFF
0x04    1       Delta X (byte medio)            (delta_x >> 8) & 0xFF
0x05    1       Delta X (byte alto)             (delta_x >> 16) & 0xFF
0x06    1       Delta Y (byte bajo)             delta_y & 0xFF
0x07    1       Delta Y (byte medio)            (delta_y >> 8) & 0xFF
0x08    1       Padding                         0x00
```

### Perfiles de aceleración
El algoritmo lee dos perfiles desde `param_3[0x71]`:

**Perfil 1 (pdVar1[0-3]):**
```
pdVar1[0]: velocidad_x_base     (uint)
pdVar1[1]: velocidad_y_base     (float)
pdVar1[2]: aceleración_x        (double)
pdVar1[3]: aceleración_y        (double)
```

**Perfil 2 (pdVar1[1][0-3]):**
```
pdVar1[0]: velocidad_x_alternativa  (uint)
pdVar1[1]: velocidad_y_alternativa  (float)
pdVar1[2]: aceleración_x_alt        (double)
pdVar1[3]: aceleración_y_alt        (double)
```

### Algoritmo de suavizado
```
1. Calcular distancia total: max(|delta_x|, |delta_y|)
2. Calcular incrementos por paso:
   step_x = delta_x / distancia_total
   step_y = delta_y / distancia_total
3. Para cada paso:
   - Actualizar posición acumulada
   - Aplicar aceleración según perfil
   - Enviar comando 0xa1 con delta actual
   - Esperar 100ms (WaitForSingleObject)
```

### Ajuste de signos
```c
if (dVar15 < 0.0) {  // Si movimiento es hacia la izquierda
    dVar19 = -dVar19;    // Invertir aceleración X
    uStack_128 = -uStack_128;  // Invertir velocidad X
}
if (dVar17 < 0.0) {  // Si movimiento es hacia abajo
    dStack_e0 = -dStack_e0;    // Invertir aceleración Y
    fStack_11c = -fStack_11c;  // Invertir velocidad Y
}
```

---

## 3. PROTOCOLO ALTERNATIVO (Header: 'W' 0xAB)

### Cuándo se usa
- Cuando `pvVar2 = *(void**)((int)param_3 + 0x21f) != NULL`
- Probablemente para dispositivos con firmware diferente o versión específica

### Estructura del paquete (11 bytes)
```
Offset  Tamaño  Descripción                     Valor
------  ------  ------------------------------- -------------------------
0x00    1       Header magic byte 1             'W' (0x57)
0x01    1       Header magic byte 2             0xAB (-0x55)
0x02    1       Flags/Reserved                  0x00
0x03    1       Tipo de comando                 0x04 o 0x05
0x04    1       Subtipo                         0x07 o 0x05
0x05    1       Longitud de datos               1 o 2
0x06    1       Device ID                       device_id
0x07    3       Datos (delta X/Y)               variable
0x0A    1       Checksum                        suma de bytes 0-11
```

### Dos variantes detectadas

**Variante A: Sin movimiento (solo device ID)**
```c
if ((*(int*)((int)pvVar2 + 0xc) < 0x37) && (delta == 0)) {
    acStack_b8[3] = 0x04;  // Tipo
    acStack_b8[4] = 0x07;  // Subtipo
    acStack_b8[5] = 2;     // Longitud
    uStack_b1 = 0;         // Sin delta
    // Calcular checksum
}
```

**Variante B: Con movimiento**
```c
else {
    acStack_b8[3] = 0x05;  // Tipo
    acStack_b8[4] = 0x05;  // Subtipo
    acStack_b8[5] = 1;     // Longitud
    uStack_b1 = (uint3)delta;  // Delta en 3 bytes
    uStack_ae = (ulonglong)(byte)(device_id + delta + 0xd);  // Checksum simple
}
```

### Cálculo de Checksum
```c
checksum = 0;
for (i = 0; i < 12; i++) {
    checksum += packet[i];
}
packet[10] = checksum;
```

### Función de envío
```c
FUN_10001920(pvVar2, acStack_b8, size, 500);
WaitForSingleObject(*(HANDLE*)((int)param_3 + 0x20d), 100);
```

---

## 4. EVENTOS DE BOTONES

### HT_LeftDown (Presionar botón izquierdo)

**Actualiza el estado:**
```c
*(undefined4 *)((int)param_1 + 0x1dd) = 1;  // Button state = 1 (izquierdo)
```

**Modo absoluto (repositiona + presiona):**
```c
memset(&local_60, 0, 0x40);
local_5f = 0xa0;              // Comando absoluto
uStack_5e = 1;                // Button state = izquierdo
uStack_5d = x_normalized;     // Coordenada X
uStack_5b = y_normalized_low; // Coordenada Y (bytes)
uStack_5a = y_normalized_high;
hid_write_timeout((short*)*param_1, &local_60, 9, 500);
```

**Modo relativo (solo presiona):**
```c
memset(&local_60, 0, 0x40);
local_5f = 0xa1;              // Comando relativo
uStack_5e = 1;                // Button state = izquierdo
uStack_5d = 0;                // Sin movimiento
uStack_5b = 0;
hid_write_timeout((short*)*param_1, &local_60, 9, 500);
```

**Protocolo alternativo:**
```
Firmware < 0x37:  'W' 0xAB 0x00 0x04 0x07 0x02 0x01 [checksum]
Firmware >= 0x37: 'W' 0xAB 0x00 0x05 0x05 0x01 0x01 [0x0e checksum]
                                                   ^^
                                        Button: 0x01 = izquierdo
```

### HT_RightDown (Presionar botón derecho)

**Actualiza el estado:**
```c
*(undefined4 *)((int)param_1 + 0x1dd) = 2;  // Button state = 2 (derecho)
```

**Modo HID directo:**
```c
memset(&local_5c, 0, 0x40);
local_5b = 0xa1;              // Comando relativo
local_5a = 2;                 // Button state = derecho (offset 2)
hid_write_timeout((short*)*param_1, &local_5c, 9, 500);
```

**Protocolo alternativo:**
```
Firmware < 0x37:  'W' 0xAB 0x00 0x04 0x07 0x02 0x02 [checksum]
Firmware >= 0x37: 'W' 0xAB 0x00 0x05 0x05 0x01 0x02 [0x0f checksum]
                                                   ^^
                                        Button: 0x02 = derecho
```

### HT_LeftUp / HT_RightUp (Soltar botones)

Probablemente similar pero con button state = 0:
```c
*(undefined4 *)((int)param_1 + 0x1dd) = 0;  // Button state = 0 (ninguno)
memset(&buffer, 0, 0x40);
buffer[1] = 0xa1;             // Comando relativo
buffer[2] = 0;                // Button state = ninguno
hid_write_timeout(...);
```

---

## 5. FLUJO COMPLETO: MOVIMIENTO + CLICK

### Secuencia de operaciones
```
1. HT_MoveToAA(x, y, device_context)
   ├─ Si modo absoluto:
   │  └─ Enviar comando 0xa0 con coordenadas normalizadas
   │
   └─ Si modo incremental:
      ├─ Calcular delta desde posición actual
      ├─ Dividir en pasos con suavizado
      ├─ Para cada paso:
      │  ├─ Calcular delta con aceleración
      │  ├─ Enviar comando 0xa1 (o protocolo alternativo)
      │  └─ Esperar 100ms
      └─ Actualizar posición actual

2. HT_LeftClick(device_context)
   ├─ HT_LeftDown(device_context)
   ├─ Sleep(rand() % 31 + 50)  // 50-80ms aleatorio
   └─ HT_LeftUp(device_context)
```

### Tiempos importantes
- **Movimiento absoluto**: Sin delay entre comando y click
- **Movimiento incremental**: 100ms entre cada paso
- **Click down->up**: 50-80ms (aleatorio para simular humano)
- **Timeout HID write**: 500ms
- **Wait handle**: 100ms

### Variables de contexto importantes
```
param_3[0x73]:     screen_width
param_3[0x74]:     screen_height
param_3 + 0x1dd:   device_id
param_3 + 0x1e1:   current_x_position
param_3 + 0x1e5:   current_y_position
param_3 + 0x223:   movement_mode (0=incremental, 1=absolute)
param_3 + 0x21f:   alternative_protocol_handle
param_3[0x71]:     acceleration_profiles_pointer
param_3 + 0x20d:   sync_event_handle
```

---

## 5. COMANDOS CONFIRMADOS

**IMPORTANTE:** Los comandos 0xa0 y 0xa1 se usan TANTO para movimiento como para eventos de botón.
El byte en offset 2 (antes llamado "device_id") es en realidad el **button state**.

```
0xa0  = MOUSE_ABSOLUTE           // Movimiento absoluto + estado de botón
0xa1  = MOUSE_RELATIVE           // Movimiento relativo + estado de botón

Button states (offset 2):
  0 = Sin botón presionado (solo movimiento)
  1 = Botón izquierdo presionado
  2 = Botón derecho presionado
```

### Ejemplos de paquetes confirmados:

**Movimiento sin botón:**
```
00 a1 00 64 00 00 00 00 00    // Move relativo +100,0 sin botón
```

**Click izquierdo (down):**
```
00 a1 01 00 00 00 00 00 00    // Botón izquierdo presionado, sin movimiento
```

**Click derecho (down):**
```
00 a1 02 00 00 00 00 00 00    // Botón derecho presionado, sin movimiento
```

**Movimiento con botón presionado (arrastrar):**
```
00 a1 01 64 00 00 32 00 00    // Arrastrar con izquierdo: +100,+50
```

---

## 6. PRÓXIMOS PASOS PARA REVERSE ENGINEERING

1. **Analizar HT_LeftDown y HT_LeftUp** para confirmar comandos de clicks
2. **Buscar HT_RightClick** para clicks derechos
3. **Analizar FUN_10002350** - parece ser wrapper de envío HID
4. **Analizar FUN_10001920** - función de protocolo alternativo
5. **Buscar tabla de perfiles de aceleración** en memoria
6. **Verificar si hay scroll/wheel commands**

---

## 7. CAPTURA CON WIRESHARK/USBPCAP

Para confirmar este análisis, capturar tráfico HID USB mientras:
1. Se mueve el mouse en modo absoluto
2. Se mueve el mouse en modo incremental
3. Se hace click izquierdo
4. Se hace click derecho
5. Se hace scroll (si existe)

Filtro Wireshark: `usb.device_address == X && usb.endpoint_address.direction == OUT`
