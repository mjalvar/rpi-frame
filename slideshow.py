import os
import subprocess
import hashlib

FRAME_DIR = "/tmp/frame"
STATE_FILE = "/tmp/.feh_frame_state.txt"

FEH_COMMAND = ['feh', '--fullscreen', '--zoom', 'fill', '--slideshow-delay', '10', '--hide-pointer', '--randomize', FRAME_DIR]
FEH_ENV = {
    "DISPLAY": ":0",
    "HOME": os.environ.get("HOME", "/tmp")
}

def calculate_directory_hash(directory):
    """Crea un hash basado en los nombres y tamaños de archivos."""
    hash_md5 = hashlib.md5()
    for root, _, files in sorted(os.walk(directory)):
        for fname in sorted(files):
            path = os.path.join(root, fname)
            if os.path.isfile(path):
                stat = os.stat(path)
                hash_md5.update(fname.encode())
                hash_md5.update(str(stat.st_mtime).encode())
                hash_md5.update(str(stat.st_size).encode())
    return hash_md5.hexdigest()

def read_previous_hash():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return f.read().strip()
    return ""

def write_current_hash(h):
    with open(STATE_FILE, 'w') as f:
        f.write(h)

def is_feh_running():
    try:
        subprocess.check_output(['pgrep', '-f', 'feh'])
        return True
    except subprocess.CalledProcessError:
        return False

def start_feh():
    print("Iniciando feh...")
    subprocess.Popen(FEH_COMMAND, env=FEH_ENV)

def restart_feh():
    print("Reiniciando feh...")
    subprocess.call(['pkill', '-f', 'feh'])
    start_feh()

def main():
    current_hash = calculate_directory_hash(FRAME_DIR)
    previous_hash = read_previous_hash()

    if current_hash != previous_hash:
        print("Cambio detectado en los archivos.")
        if is_feh_running():
            restart_feh()
        else:
            start_feh()
        write_current_hash(current_hash)
    else:
        print("No hay cambios en /tmp/frame. No se reinicia feh.")

if __name__ == "__main__":
    main()
