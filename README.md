# RPi Frame - Digital Photo Frame Setup

Un proyecto para transformar una Raspberry Pi en un marco digital que sincroniza fotos desde Google Drive y las muestra en una presentación de diapositivas.

## 📋 Descripción General

Este proyecto implementa un sistema automatizado de marco de fotos digital para Raspberry Pi que:

- **Sincroniza fotos** desde Google Drive usando rclone
- **Convierte formatos de imagen** (HEIC, NEF a JPG)
- **Muestra presentación de diapositivas** automática con feh
- **Detecta cambios** en los archivos y reinicia la presentación automáticamente
- **Ejecuta tareas programadas** mediante cron para automatización

## 🛠️ Requisitos de Instalación

### Dependencias del Sistema

Antes de ejecutar los scripts, debes instalar las siguientes herramientas en tu Raspberry Pi:

```bash
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-pip \
    feh \
    rclone \
    libheif-examples \
    exiftool \
    procps
```

#### Descripción de dependencias:

- **python3 & python3-pip**: Intérprete de Python 3 y gestor de paquetes
- **feh**: Visor de imágenes optimizado para presentaciones de diapositivas
- **rclone**: Herramienta de sincronización para Google Drive y otros servicios cloud
- **libheif-examples**: Contiene `heif-convert` para convertir imágenes HEIC a JPG
- **exiftool**: Utilidad para extraer información EXIF y miniaturas de archivos NEF (Canon RAW)
- **procps**: Proporciona `pgrep` y `pkill` para gestionar procesos

### Dependencias de Python

Los scripts utilizan solo módulos estándar de Python, por lo que no requieren instalación adicional de paquetes:

- `subprocess` - Ejecutar comandos del sistema
- `os` - Operaciones del sistema de archivos
- `shutil` - Operaciones de archivos (copiar, etc.)
- `hashlib` - Calcular hashes MD5 para detectar cambios

## 📁 Estructura del Proyecto

```
rpi-frame/
├── gdrive-sync.py          Script para sincronizar Google Drive y convertir imágenes
├── slideshow.py            Script para mostrar presentación de diapositivas con feh
├── conky.frame            Configuración de Conky para mostrar info del sistema
├── crontab.cfg            Configuración de tareas programadas
├── .gitignore             Archivos a ignorar en Git
└── README.md              Este archivo
```

## 🚀 Cómo Funciona

### gdrive-sync.py
- Sincroniza fotos desde Google Drive (`gdrive-frame:PictureFrame`)
- Convierte archivos HEIC (iPhone) a JPG usando `heif-convert`
- Convierte archivos NEF (Canon RAW) a JPG extrayendo la miniatura con `exiftool`
- Copia otros formatos de imagen directamente
- Elimina imágenes con sufijo `-depth.jpg` (profundidad de fotos con IA)
- Elimina archivos en `/tmp/frame` que ya no existen en la fuente

### slideshow.py
- Monitorea cambios en `/tmp/frame` usando hash MD5
- Inicia automáticamente una presentación de diapositivas con `feh`
- Reinicia feh cuando detecta nuevas imágenes
- Mantiene la presentación en pantalla completa

### conky.frame
- Muestra información del sistema (hora, IPs de red)
- Archivo de configuración para Conky

## ⚙️ Configuración Inicial

### 1. Configurar rclone para Google Drive

```bash
rclone config
```

Crea una configuración llamada `gdrive-frame` con tu cuenta de Google Drive.

### 2. Crear directorios necesarios

```bash
mkdir -p /home/pi/frame
mkdir -p /tmp/frame
```

### 3. Copiar scripts al servidor

```bash
cp gdrive-sync.py /home/pi/frame/
cp slideshow.py /home/pi/frame/
chmod +x /home/pi/frame/gdrive-sync.py
chmod +x /home/pi/frame/slideshow.py
```

### 4. Configurar tareas cron

```bash
crontab -e
```

Añade las siguientes líneas (según `crontab.cfg`):

```cron
# Sincronizar Google Drive cada hora
0 * * * * /usr/bin/python3 /home/pi/frame/gdrive-sync.py > /home/pi/frame/gdrive.log 2>&1

# Actualizar presentación cada 5 minutos
*/5 * * * * /usr/bin/python3 /home/pi/frame/slideshow.py > /home/pi/frame/slideshow.log 2>&1
```

## 🎬 Ejecución Manual

### Ejecutar sincronización de Google Drive

```bash
python3 gdrive-sync.py
```

Esto:
1. Sincroniza fotos desde Google Drive
2. Convierte formatos incompatibles (HEIC, NEF)
3. Limpia archivos innecesarios
4. Genera logs en `/home/pi/frame/gdrive.log`

### Ejecutar presentación de diapositivas

```bash
python3 slideshow.py
```

Esto:
1. Verifica si hay cambios en `/tmp/frame`
2. Inicia o reinicia feh si es necesario
3. Genera logs en `/home/pi/frame/slideshow.log`

## 📝 Logs

Los scripts generan archivos de log útiles para debugging:

- `/home/pi/frame/gdrive.log` - Log de sincronización de Google Drive
- `/home/pi/frame/slideshow.log` - Log de la presentación de diapositivas
- `/home/pi/frame/rclone.log` - Log detallado de rclone

Ver logs en tiempo real:

```bash
tail -f /home/pi/frame/gdrive.log
tail -f /home/pi/frame/slideshow.log
```

## 🔧 Rutas y Configuración Personalizada

Si usas rutas diferentes a las predeterminadas, edita estas variables en los scripts:

**gdrive-sync.py:**
```python
SRC_DIR = "/home/pi/Pictures"      # Directorio de sincronización
DST_DIR = "/tmp/frame"             # Directorio de destino
```

**slideshow.py:**
```python
FRAME_DIR = "/tmp/frame"           # Directorio de imágenes a mostrar
STATE_FILE = "/tmp/.feh_frame_state.txt"  # Archivo de estado
```

## 🐛 Troubleshooting

### feh no inicia
- Verifica que DISPLAY esté configurado: `echo $DISPLAY`
- En Raspberry Pi sin interfaz gráfica, puede necesitarse configuración adicional de X11

### rclone falla
- Verifica la configuración: `rclone config show`
- Comprueba credenciales de Google Drive
- Revisa `/home/pi/frame/rclone.log` para más detalles

### No se detectan cambios en slideshow.py
- Verifica que `/tmp/frame` existe y contiene imágenes
- Comprueba permisos de lectura en el directorio
- Revisa `/home/pi/frame/slideshow.log`

### Conversión HEIC/NEF falla
- Verifica instalación: `heif-convert --version` y `exiftool -ver`
- Comprueba que las imágenes son válidas
- Revisa permisos de escritura en `/tmp/frame`

## 📦 Dependencias Resumidas

| Herramienta | Uso | Comando instalación |
|-----------|-----|----------------------|
| Python 3 | Lenguaje de scripting | `apt-get install python3` |
| feh | Visor/presentación de imágenes | `apt-get install feh` |
| rclone | Sincronización Google Drive | `apt-get install rclone` |
| heif-convert | Conversión HEIC→JPG | `apt-get install libheif-examples` |
| exiftool | Extracción de miniaturas NEF | `apt-get install exiftool` |
| procps | Gestión de procesos (pgrep) | `apt-get install procps` |

## 🤝 Notas

- Todos los scripts están optimizados para ejecutarse en Raspberry Pi
- Los logs incluyen timestamps y niveles de detalle para debugging
- El sistema es tolerante a fallos y continúa funcionando incluso si algunas conversiones fallan
- Se recomienda mantener `/tmp/frame` en un sistema de archivos rápido

## 📄 Licencia

Este proyecto no especifica una licencia. Para más información, contacta al propietario del repositorio.
