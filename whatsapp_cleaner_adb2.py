import subprocess
import re

RUTA_BASE = "/storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images"

def ejecutar_comando_lista(comando):
    resultado = subprocess.run(comando, capture_output=True, text=True)
    return resultado.stdout.strip()

def obtener_tamano_archivo(ruta_escapada, archivo):
    comando = [
        "adb", "shell", "stat", "-c%s",
        f"{ruta_escapada}/{archivo}"
    ]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    try:
        return int(resultado.stdout.strip())
    except:
        return 0

print("Obteniendo archivos del dispositivo...\n")

ruta_escapada = RUTA_BASE.replace(" ", "\\ ")

salida = ejecutar_comando_lista([
    "adb", "shell", "ls", ruta_escapada
])

archivos = salida.split("\n")

desde = input("Nombre inicial (ej: IMG-20250219-WA0065.jpg): ")
hasta = input("Nombre final   (ej: IMG-20250219-WA0070.jpg): ")

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

if not archivos_a_eliminar:
    print("⚠ No se encontraron archivos en ese rango.")
    exit()

# 🔥 Calcular espacio total
espacio_total = 0
for archivo in archivos_a_eliminar:
    espacio_total += obtener_tamano_archivo(ruta_escapada, archivo)

mb = espacio_total / (1024 * 1024)
gb = mb / 1024

print("\nArchivos que coinciden:\n")
for a in archivos_a_eliminar:
    print(a)

print(f"\nTotal archivos: {len(archivos_a_eliminar)}")

if gb >= 1:
    print(f"Espacio aproximado a liberar: {gb:.2f} GB")
else:
    print(f"Espacio aproximado a liberar: {mb:.2f} MB")

confirmacion = input("\n¿Eliminar estos archivos? (s/n): ")

if confirmacion.lower() == "s":
    eliminados = 0
    for archivo in archivos_a_eliminar:
        comando = [
            "adb", "shell", "rm",
            f"{ruta_escapada}/{archivo}"
        ]
        resultado = subprocess.run(comando)
        if resultado.returncode == 0:
            eliminados += 1

    print(f"\n✅ Archivos eliminados correctamente: {eliminados}")
    print(f"❌ Fallaron: {len(archivos_a_eliminar) - eliminados}")
else:
    print("❌ Operación cancelada.")