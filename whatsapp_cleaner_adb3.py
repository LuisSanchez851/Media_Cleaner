import subprocess
import re
import argparse
import sys

RUTA_BASE = "/storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images"


def ejecutar(comando):
    return subprocess.run(comando, capture_output=True, text=True)


def listar_archivos(ruta_escapada):
    resultado = ejecutar(["adb", "shell", "ls", ruta_escapada])
    if resultado.returncode != 0:
        print("❌ Error listando archivos.")
        sys.exit(1)
    return resultado.stdout.strip().split("\n")


def obtener_tamano(ruta_escapada, archivo):
    resultado = ejecutar(["adb", "shell", "stat", "-c%s", f"{ruta_escapada}/{archivo}"])
    try:
        return int(resultado.stdout.strip())
    except:
        return 0


def formatear_espacio(bytes_total):
    mb = bytes_total / (1024 * 1024)
    gb = mb / 1024
    if gb >= 1:
        return f"{gb:.2f} GB"
    return f"{mb:.2f} MB"


def filtrar_archivos(archivos, desde, hasta):
    patron = re.compile(r"(IMG|null)-(\d{8})-WA(\d+)\.jpg", re.IGNORECASE)

    match_desde = patron.match(desde)
    match_hasta = patron.match(hasta)

    if not match_desde or not match_hasta:
        print("❌ Formato de nombre incorrecto.")
        sys.exit(1)

    _, fecha_desde, num_desde = match_desde.groups()
    _, fecha_hasta, num_hasta = match_hasta.groups()

    if fecha_desde != fecha_hasta:
        print("❌ Las fechas no coinciden.")
        sys.exit(1)

    num_desde = int(num_desde)
    num_hasta = int(num_hasta)

    resultado = []

    for archivo in archivos:
        match = patron.match(archivo)
        if match:
            _, fecha, numero = match.groups()
            numero = int(numero)
            if fecha == fecha_desde and num_desde <= numero <= num_hasta:
                resultado.append(archivo)

    return sorted(resultado)


def eliminar_archivos(ruta_escapada, archivos, dry_run=False):
    eliminados = 0

    for archivo in archivos:
        if dry_run:
            print(f"[SIMULACIÓN] Eliminaría: {archivo}")
            continue

        resultado = ejecutar(["adb", "shell", "rm", f"{ruta_escapada}/{archivo}"])
        if resultado.returncode == 0:
            eliminados += 1

    return eliminados


def main():
    parser = argparse.ArgumentParser(description="WhatsApp ADB Cleaner")
    parser.add_argument("desde", help="Archivo inicial")
    parser.add_argument("hasta", help="Archivo final")
    parser.add_argument("--dry-run", action="store_true", help="Modo simulación (no elimina archivos)")

    args = parser.parse_args()

    ruta_escapada = RUTA_BASE.replace(" ", "\\ ")

    print("🔍 Listando archivos en el dispositivo...")
    archivos = listar_archivos(ruta_escapada)

    archivos_filtrados = filtrar_archivos(archivos, args.desde, args.hasta)

    if not archivos_filtrados:
        print("⚠ No se encontraron archivos en ese rango.")
        sys.exit(0)

    espacio_total = sum(obtener_tamano(ruta_escapada, a) for a in archivos_filtrados)

    print("\n📂 Archivos detectados:")
    for a in archivos_filtrados:
        print("  -", a)

    print(f"\n🧮 Total archivos: {len(archivos_filtrados)}")
    print(f"💾 Espacio a liberar: {formatear_espacio(espacio_total)}")

    if args.dry_run:
        print("\n🟡 Modo simulación activado. No se eliminará nada.")
        eliminar_archivos(ruta_escapada, archivos_filtrados, dry_run=True)
        sys.exit(0)

    confirm = input("\n¿Confirmar eliminación? (s/n): ")

    if confirm.lower() != "s":
        print("❌ Operación cancelada.")
        sys.exit(0)

    eliminados = eliminar_archivos(ruta_escapada, archivos_filtrados)

    print(f"\n✅ Eliminados correctamente: {eliminados}")
    print(f"❌ Fallaron: {len(archivos_filtrados) - eliminados}")


if __name__ == "__main__":
    main()