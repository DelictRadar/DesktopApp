# DesktopApp
## Guía de instalación
---
### Requisitos del sistema
Se listarán los requerimientos del sistema que la aplicación soporta y permiten que esta funcione correctamente.
1. Windows 10/11
2. Tarjeta gráfica NVIDIA

### Dependencias
Descargue cuando en la sección **Procedimiento** se le pida que lo haga.
1. [Aplicación](https://github.com/DelictRadar/DesktopApp/archive/refs/heads/main.zip)
2. [Anaconda](https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Windows-x86_64.exe)
3. [ONNX](https://)

### Procedimiento
1. Primero, se deberá descargar e instalar la dependencia **Anaconda**, con el objetivo que mientras se instale avancemos con los siguientes pasos.
> Ejecute el instalador y solo avance en la instalación sin modificar las opciones que el instalador le recomienda.
3. Luego deberá clonar o descargar el repositorio, en esta guía se tomará el camino de la descarga. Para ello, se descargará la primera dependencia llamada **Aplicación**.
4. Una vez decargada, al archivo resultante será `DesktopApp-main.zip`, del cual se extraerá su contenido en una ubicación de su preferencia.
> Recomendamos que la ubicación donde se extraiga la carpeta sea de fácil acceso como el escritorio o la carpeta de documentos.
> Después de haber extraído, la estructura de la carpeta será la siguiente:
```
DesktopApp\
|_ assets\
|_ bin\
  |_ execute.bat
  |_ install.bat
|_ .gitignore
|_ main.py
```
5. Lo siguiente que se realizará es descargar la tercera dependencia **ONNX** la cual descargará un archivo con extensión .onnx, este archivo deberá colocarse en la carpeta `assets`.
6. Cuando ya se haya instalado **Anaconda**, deberá digirse al directorio `bin` y ejecutar el archivo `install.bat`.

## Guía de usuario
---
