import subprocess
import os
import shutil

SRC_DIR = "/home/pi/Pictures"
DST_DIR = "/tmp/frame"
RCLONE_CMD = [
    "/usr/bin/rclone",
    "sync",
    "gdrive-frame:PictureFrame",
    SRC_DIR,
    "--log-file=/home/pi/frame/rclone.log",
    "--log-level=INFO",
    "--delete-excluded"
]

def run_rclone():
    print("Ejecutando rclone...")
    result = subprocess.run(RCLONE_CMD, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error en rclone:", result.stderr)
    else:
        print("rclone finalizado correctamente.")

def process_files():
    if not os.path.exists(DST_DIR):
        os.makedirs(DST_DIR)
    for filename in os.listdir(SRC_DIR):
        src_path = os.path.join(SRC_DIR, filename)
        if not os.path.isfile(src_path):
            continue
        name, ext = os.path.splitext(filename)
        ext_lower = ext.lower()

        if ext_lower == ".heic":
            dst_path = os.path.join(DST_DIR, f"{name}.jpg")
            if os.path.exists(dst_path):
                print(f"Archivo convertido ya existe, saltando: {dst_path}")
                continue

            # Verificar si el archivo HEIC ya es JPEG
            file_info = subprocess.run(["file", "--mime-type", "-b", src_path], capture_output=True, text=True)
            if file_info.returncode != 0:
                print(f"Error obteniendo información del archivo {filename}: {file_info.stderr}")
                continue
            if "image/jpeg" in file_info.stdout:
                dst_path = os.path.join(DST_DIR, f"{name}.jpg")
                print(f"El archivo {filename} ya es JPEG, cambiando extensión y copiando a {dst_path}...")
                shutil.copy2(src_path, dst_path)
                continue
            print(f"Convirtiendo {filename} a {dst_path}...")
            result = subprocess.run(["heif-convert", src_path, dst_path], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error convirtiendo {filename}: {result.stderr}")
        elif ext_lower == ".nef":
            dst_path = os.path.join(DST_DIR, f"{name}.jpg")
            if os.path.exists(dst_path):
                print(f"Archivo convertido ya existe, saltando: {dst_path}")
                continue
            print(f"Convirtiendo {filename} a {dst_path}...")
            result = subprocess.run(["bash", "-c", f"exiftool -b -PreviewImage {src_path} > {dst_path}"], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error convirtiendo {filename}: {result.stderr}")
        else:
            dst_path = os.path.join(DST_DIR, filename)
            if os.path.exists(dst_path):
                print(f"Archivo ya existe, saltando copia: {dst_path}")
                continue
            print(f"Copiando {filename} a {dst_path}...")
            shutil.copy2(src_path, dst_path)

def remove_depth_images():
    print("Eliminando archivos *-depth.jpg en", DST_DIR)
    for filename in os.listdir(DST_DIR):
        if filename.endswith("-depth.jpg"):
            path = os.path.join(DST_DIR, filename)
            print(f"Borrando {filename}...")
            os.remove(path)

def remove_missing_images():
    print("Eliminando archivos en", DST_DIR, "que no están en", SRC_DIR)
    src_files = {os.path.splitext(f)[0] for f in os.listdir(SRC_DIR) if os.path.isfile(os.path.join(SRC_DIR, f))}
    for filename in os.listdir(DST_DIR):
        dst_name, _ = os.path.splitext(filename)
        if dst_name not in src_files:
            path = os.path.join(DST_DIR, filename)
            print(f"Borrando {filename}...")
            os.remove(path)

def main():
    run_rclone()
    process_files()
    remove_depth_images()
    remove_missing_images()
    print("Proceso terminado.")

if __name__ == "__main__":
    main()

