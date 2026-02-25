import subprocess
import re

RUTA_BASE = "/storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images"

def ejecutar_comando(comando):
    resultado = subprocess.run(comando, capture_output=True, text=True)
    return resultado.stdout.strip()

# Obtener lista completa de archivos
print("Obteniendo archivos del dispositivo...\n")
salida = ejecutar_comando([
    "adb", "shell", "ls", RUTA_BASE.replace(" ", "\\ ")
])

archivos = salida.split("\n")

desde = input("Nombre inicial (ej: IMG-20260221-WA0011.jpg): ")
hasta = input("Nombre final   (ej: IMG-20260221-WA0033.jpg): ")

patron = re.compile(r"(IMG|null)-(\d{8})-WA(\d+)\.jpg", re.IGNORECASE)

match_desde = patron.match(desde)
match_hasta = patron.match(hasta)

if not match_desde or not match_hasta:
    print("❌ Formato incorrecto.")
    exit()

_, fecha_desde, num_desde = match_desde.groups()
_, fecha_hasta, num_hasta = match_hasta.groups()

if fecha_desde != fecha_hasta:
    print("❌ Las fechas no coinciden.")
    exit()

num_desde = int(num_desde)
num_hasta = int(num_hasta)

archivos_a_eliminar = []

for archivo in archivos:
    match = patron.match(archivo)
    if match:
        _, fecha, numero = match.groups()
        numero = int(numero)

        if fecha == fecha_desde and num_desde <= numero <= num_hasta:
            archivos_a_eliminar.append(archivo)

archivos_a_eliminar.sort()

print("\nArchivos que coinciden:\n")

for a in archivos_a_eliminar:
    print(a)

print(f"\nTotal encontrados: {len(archivos_a_eliminar)}")

confirmacion = input("\n¿Eliminar estos archivos? (s/n): ")

if confirmacion.lower() == "s":
    ruta_escapada = RUTA_BASE.replace(" ", "\\ ")
    
    for archivo in archivos_a_eliminar:
        comando = [
            "adb", "shell", "rm",
            f"{ruta_escapada}/{archivo}"
        ]
        subprocess.run(comando)
    
    print("✅ Eliminación completada.")
else:
    print("❌ Operación cancelada.")