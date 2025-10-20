# 🔬 Análisis de Ghidra - MouseKeyItem.dll

## 📋 Resumen Ejecutivo

Este documento detalla los hallazgos del análisis de ingeniería inversa del archivo `MouseKeyItem.dll` usando Ghidra. Se han identificado las funciones críticas que controlan cómo iMouse envía comandos de teclado al iPhone.

---

## 🔑 Descubrimiento Principal

**⚠️ El marcador de protocolo correcto es `0xa2`, NO `0xa1`**

Esto fue confirmado en el código fuente decompilado de la función `FUN_100024b0`:
```c
local_57 = 0xa2;  // MARKER
```

---

## 📦 Funciones Analizadas

### 1. `CusKeyInput_DownUP` - Función Principal de Teclado

**Propósito**: Procesa cadenas de texto y las convierte en comandos USB

**Flujo de ejecución**:
```
Entrada: Texto string → Procesamiento carácter por carácter → Envío USB
```

**Código relevante**:
```c
void CusKeyInput_DownUP(undefined4 *param_1, char *param_2, int param_3)
{
    // 1. Convierte cada carácter a scancode
    FUN_1000b760(local_30, (char *)piVar4);

    // 2. Construye el byte de modificadores
    local_40 = local_40 | local_24;  // Modifiers (Shift, Ctrl, Alt, etc.)

    // 3. Construye el byte de scancode
    local_44 = local_44 | (int)local_30[0] << (iVar7);  // Scancodes

    // 4. Envía el paquete USB
    FUN_100024b0(local_38, uVar5, uVar9, local_38, (char)uVar10);
}
```

**Observaciones**:
- Procesa texto carácter por carácter
- Usa tabla de lookup (FUN_1000b760) para convertir char → scancode
- Combina modificadores en un solo byte con operaciones OR
- Llama a FUN_100024b0 para envío final

---

### 2. `FUN_100024b0` - Función de Envío USB

**Propósito**: Construye y envía el paquete de 9 bytes al dispositivo USB

**Código completo**:
```c
void __fastcall FUN_100024b0(undefined4 *param_1, uint param_2,
                              undefined4 param_3, undefined4 param_4,
                              undefined1 param_5)
{
    char acStack_80[48];
    undefined4 local_50;
    undefined local_4c;
    undefined local_48;
    undefined local_47;
    undefined local_46;
    undefined local_40;
    undefined4 local_3c;
    undefined4 local_38;
    undefined4 *local_34;
    int local_30;
    undefined4 local_2c;
    undefined4 local_28;

    local_34 = param_1;
    local_30 = *(int *)((int)param_1 + 0x21f);

    // RUTA 1: Protocolo Alternativo (WiFi/WebSocket directo)
    if (local_30 != 0) {
        local_2c = 0;
        local_28 = 0;
        acStack_80[0] = 'W';       // 0x57
        acStack_80[1] = -0x55;     // 0xAB
        acStack_80[2] = -1;        // 0xFF
        acStack_80[3] = '\x02';    // 0x02
        acStack_80[4] = local_88;
        acStack_80[5] = local_84;
        acStack_80[6] = param_5;
        acStack_80[7] = '\0';

        FUN_1000b8c0(&local_2c, acStack_80);
        FUN_1000ba60(*(undefined4 *)(local_30 + 0xc), &local_2c);

        if (local_2c != 0) {
            (**(code **)(*local_2c + 8))(local_2c, 1);
        }
        if (local_28 != 0) {
            (**(code **)(*local_28 + 8))(local_28, 1);
        }
        return;
    }

    // RUTA 2: Protocolo USB Normal (RUTA PRINCIPAL)
    if (*(char *)((int)param_1 + 0x223) != '\0') {
        memset(&local_58, 0, 0x40);

        local_56 = local_88;   // Modifier + Scancode data
        local_52 = local_84;   // Extra data
        local_57 = 0xa2;       // ⚠️ MARCADOR DE PROTOCOLO
        local_50 = param_5;    // Type/flag byte

        // Envía 9 bytes via USB con timeout de 500ms
        hid_write_timeout((short *)*param_1, &local_58, 9, 500);
    }
    return;
}
```

**Hallazgos importantes**:

1. **Dos rutas de comunicación**:
   - **Ruta 1** (WiFi/WebSocket): Cuando `param_1[0x21f] != 0`
     - Usa header especial: `0x57 0xAB 0xFF 0x02` ("W" + marca)
     - Envía por red directamente al iPhone
   - **Ruta 2** (USB): Cuando `param_1[0x223] != 0`
     - Construye paquete de 9 bytes
     - **Marcador confirmado: `0xa2`**
     - Envía vía `hid_write_timeout()`

2. **Estructura del paquete USB** (9 bytes):
   ```
   Byte 0:    Report ID (implícito, añadido por hid_write_timeout)
   Byte 1:    0xa2           (marcador de protocolo)
   Byte 2:    local_88       (modifier + scancode data, byte alto)
   Byte 3-6:  Padding/data
   Byte 7:    local_84       (extra data)
   Byte 8:    param_5        (type/flag)
   ```

3. **Timeout**: 500ms para envío USB

---

### 3. `FUN_1000b760` - Tabla de Lookup de Caracteres

**Propósito**: Convierte caracteres/strings a scancodes HID + modificadores

**Código**:
```c
undefined4 * __fastcall FUN_1000b760(undefined4 *param_1, char *param_2)
{
    undefined4 *puVar1;
    int iVar2;
    char **ppcVar3;
    int iVar4;
    char **ppcVar5;
    int iVar6;

    iVar6 = 0;
    iVar4 = 0;
    puVar1 = param_1;

    // Búsqueda en tabla de lookup
    ppcVar5 = &PTR_DAT_1001901c;
    do {
        iVar4 = _stricmp(*ppcVar5, param_2);  // Comparación case-insensitive

        if (iVar4 == 0) {  // ¡Match encontrado!
            // Copia datos del scancode + modifier
            *param_1 = *(undefined4 *)(&DAT_10019018 + iVar4);
            param_1[1] = *(undefined4 *)(&DAT_10019018 + iVar4 + 4);
            param_1[2] = *(undefined4 *)(&DAT_10019018 + iVar4 + 8);
            param_1[3] = *(undefined4 *)(&DAT_10019018 + iVar4 + 0xc);

            // Suma datos adicionales
            *param_1 = *param_1 + iVar6;

            return puVar1;
        }

        ppcVar5 = ppcVar5 + 4;  // Siguiente entrada (stride de 4 words)
        iVar6 = iVar6 + 1;

    } while ((int)ppcVar5 < 0x10019a7c);  // Fin de tabla

    // No encontrado
    *param_1 = 0xffffffff;
    param_1[1] = 0;
    param_1[2] = 0;
    param_1[3] = 0;

    return puVar1;
}
```

**Hallazgos importantes**:

1. **Tabla de lookup**:
   - Ubicación: `0x1001901c` a `0x10019a7c`
   - Tamaño: ~2656 bytes
   - Estructura: Arrays de punteros a strings + datos asociados
   - Stride: 4 words (16 bytes) por entrada

2. **Búsqueda case-insensitive**: Usa `_stricmp()` para comparación

3. **Retorna 4 valores** (4 × 4 bytes = 16 bytes):
   - `param_1[0]`: Scancode base + contador
   - `param_1[1]`: Datos adicionales
   - `param_1[2]`: Más datos
   - `param_1[3]`: Flags/opciones

4. **Manejo de no-encontrado**: Retorna `0xffffffff` en param_1[0]

---

## 🧩 Flujo Completo de Ejecución

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Usuario escribe texto: "Hola"                                │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. CusKeyInput_DownUP() procesa cada carácter                   │
│    - Carácter 'H' → FUN_1000b760("H")                           │
│    - Retorna: scancode=0x0b, modifier=0x02 (Shift)              │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Construcción del paquete                                     │
│    - Combina modificadores con OR                               │
│    - Combina scancodes con bit shift                            │
│    - Llama a FUN_100024b0()                                     │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. FUN_100024b0() decide ruta:                                  │
│    ┌─────────────────────┬──────────────────────────────┐       │
│    │ WiFi/WebSocket?     │ USB Normal?                  │       │
│    │ (0x21f != 0)        │ (0x223 != 0)                 │       │
│    └─────────┬───────────┴──────────┬───────────────────┘       │
│              │                      │                           │
│              ▼                      ▼                           │
│    Header: W 0xAB 0xFF 0x02    Packet: [9 bytes]               │
│    Envío: red WiFi             Byte 1: 0xa2 (marcador)         │
│                                Envío: hid_write_timeout()       │
└─────────────────────────────────────┬───────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Dispositivo USB Virtual (0x720a:0x3dab)                      │
│    - Recibe los 9 bytes                                         │
│    - iMouseSrv.exe lee el paquete                               │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. iMouseSrv.exe procesa y reenvía                              │
│    - Decodifica: 0xa2 = comando de teclado                      │
│    - Lee: modifier=0x02, scancode=0x0b                          │
│    - Traduce a formato iOS                                      │
│    - Envía por AirPlay/WiFi al iPhone                           │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. iPhone ejecuta                                               │
│    - Recibe comando por WebSocket                               │
│    - Simula pulsación: Shift + H = 'H'                          │
│    - Resultado: Aparece 'H' en la app activa                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Formato Confirmado del Paquete

### Versión USB (9 bytes)
```
┌────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ 00 │ a2 │ MM │ 00 │ KK │ 00 │ 00 │ DD │ FF │
└────┴────┴────┴────┴────┴────┴────┴────┴────┘
  │    │    │    │    │              │    │
  │    │    │    │    │              │    └─ Byte 8: Flags/Type (param_5)
  │    │    │    │    │              └─ Byte 7: Extra data (local_84)
  │    │    │    │    └─ Byte 4: Scancode (variable)
  │    │    │    └─ Byte 3: Reserved (0x00)
  │    │    └─ Byte 2: Modifier (local_88 high byte)
  │    └─ Byte 1: Protocol Marker (CONFIRMADO: 0xa2)
  └─ Byte 0: Report ID (0x00)
```

### Versión WiFi/WebSocket (8 bytes)
```
┌────┬────┬────┬────┬────┬────┬────┬────┐
│ 57 │ AB │ FF │ 02 │ MM │ DD │ FF │ 00 │
└────┴────┴────┴────┴────┴────┴────┴────┘
  │    │    │    │    │    │    │
  │    │    │    │    │    │    └─ Null terminator
  │    │    │    │    │    └─ Flags
  │    │    │    │    └─ Extra data (local_84)
  │    │    │    └─ Version/Type (0x02)
  │    │    └─ Magic (0xFF)
  │    └─ Magic (0xAB)
  └─ Header 'W' (0x57)
```

---

## 🔍 Próximos Pasos de Investigación

### 1. Extraer Tabla de Lookup Completa
**Ubicación**: `0x1001901c` - `0x10019a7c`

Para obtener el mapeo completo de caracteres a scancodes:
```
1. En Ghidra, navegar a dirección 0x1001901c
2. Seleccionar rango hasta 0x10019a7c
3. Exportar datos
4. Analizar estructura:
   - Cada entrada: [string_ptr][data1][data2][data3]
   - Stride: 16 bytes (4 words)
```

### 2. Investigar Protocolo de Mouse
**Funciones a analizar**:
- `opMouseMove`
- `opMouseXY`
- `opMouseClick`
- `cmd_MouseMove`

**Hipótesis**: ¿Usa otro marcador? (0xa1, 0xa3?)

### 3. Capturar Respuestas del Dispositivo
**Método**:
- El dispositivo tiene INPUT report de 17 bytes
- Capturar con `hid_read()` o callback
- Analizar formato de respuestas

**Posibles datos**:
- Estado de conexión iPhone
- Confirmaciones de comando
- Batería del iPhone
- Errores

### 4. Analizar Protocolo WiFi/WebSocket
**Investigar**:
- ¿Cómo se establece la conexión?
- ¿Formato exacto de mensajes WebSocket?
- ¿Autenticación/encriptación?
- ¿Puerto usado?

---

## 📝 Conclusiones

1. **Marcador confirmado**: `0xa2` es el byte de protocolo para comandos de teclado USB
2. **Dual-path**: iMouse puede enviar por USB o directamente por WiFi
3. **Lookup table**: Conversión char→scancode está en tabla estática en memoria
4. **Timeout robusto**: 500ms para comandos USB
5. **Protocol alternativo**: Header `W 0xAB 0xFF 0x02` para ruta WiFi

---

## 🛠️ Aplicaciones Prácticas

Con este conocimiento podemos:

✅ **Crear emuladores** que generen paquetes correctos con marcador 0xa2
✅ **Bypass del software** enviando paquetes directos al dispositivo USB
✅ **Automatización** creando scripts que escriban en iPhone remotamente
✅ **Debugging** entendiendo por qué ciertos comandos fallan
✅ **Extensiones** añadiendo nuevos comandos o funcionalidad

---

**Fecha de análisis**: 2025-10-19
**Herramienta**: Ghidra 10.x
**Archivo analizado**: MouseKeyItem.dll
**Arquitectura**: x86 (32-bit) Windows DLL
