#!/bin/bash
echo "🔍 Verificando servicios iMouse..."
echo "=================================="
echo ""

# Verificar procesos iMouse
if tasklist.exe | grep -i "imouse" > /dev/null 2>&1; then
    echo "✅ Servicios iMouse encontrados:"
    tasklist.exe | grep -i "imouse"
else
    echo "❌ No se encontraron servicios iMouse corriendo"
    echo ""
    echo "💡 Para iniciarlos:"
    echo "   Opción 1: cd /mnt/c/imousePro && ./iMouseSrv.exe &"
    echo "   Opción 2: Desde Windows: C:\\imousePro\\iMouseSrv.exe"
    echo ""
fi

echo ""
echo "🔍 Verificando mDNS (necesario para AirPlay)..."
if tasklist.exe | grep -i "mdns" > /dev/null 2>&1; then
    echo "✅ Servicio mDNS encontrado:"
    tasklist.exe | grep -i "mdns"
else
    echo "⚠️  Servicio mDNS no encontrado"
fi

echo ""
echo "🔍 Dispositivo USB virtual..."
if lsusb.exe 2>/dev/null | grep -i "720a" > /dev/null 2>&1; then
    echo "✅ Dispositivo USB 0x720a:0x3dab detectado"
else
    echo "ℹ️  Verificando con otro método..."
fi

echo ""
echo "=================================="
echo "📱 Para conectar el iPhone:"
echo "   1. iPhone → Control Center → Screen Mirroring"
echo "   2. Seleccionar el PC de la lista"
echo "   3. Esperar conexión por AirPlay"
echo "=================================="
