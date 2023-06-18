# DesktopApp

## Guía de instalación

---

### Requisitos del sistema

Se listarán los requerimientos del sistema que la aplicación soporta y permiten que esta funcione correctamente.

1. Windows 10/11
2. Tarjeta gráfica NVIDIA, a partir de las serie 10

### Dependencias

Descargue cuando en la sección **Procedimiento** se le pida que lo haga.

1. [Aplicación](https://github.com/DelictRadar/DesktopApp/archive/refs/heads/main.zip)
2. [Anaconda](https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Windows-x86_64.exe)
3. [ONNX](https://upcedupe-my.sharepoint.com/:u:/g/personal/u201815174_upc_edu_pe/ER-xoGecjfdLjAkxjWcqz98BlIvP55DuaqWUxO6eS8mYPg?e=uN3feI)

### Procedimiento

1. Primero, se deberá descargar e instalar la dependencia **Anaconda**, con el objetivo que mientras se instale avancemos con los siguientes pasos.

> Ejecute el instalador y solo avance en la instalación sin modificar las opciones que el instalador le recomienda.

2. Luego deberá clonar o descargar el repositorio, en esta guía se tomará el camino de la descarga. Para ello, se descargará la primera dependencia llamada **Aplicación**.

3. Una vez decargada, al archivo resultante será `DesktopApp-main.zip`, del cual se extraerá su contenido en una ubicación de su preferencia.

> Recomendamos que la ubicación donde se extraiga la carpeta sea de fácil acceso como el escritorio o la carpeta de documentos.
> Después de haber extraído, la estructura de la carpeta será la siguiente:

```
DesktopApp\
|_ assets\
  |_ installation\
  |_ sounds\
|_ bin\
  |_ execute.bat
  |_ install.bat
|_ .gitignore
|_ main.py
```

4. Lo siguiente que se realizará es descargar la tercera dependencia **ONNX** la cual descargará un archivo con extensión `.onnx`, este archivo deberá colocarse en la carpeta `assets\`.
5. Cuando ya se haya instalado **Anaconda**, deberá digirse al directorio `bin\` y ejecutar el archivo `install.bat`.
6. Finalmente, la estructura de la carpeta resultante después de toda la instalación será la siguiente:

```
DesktopApp\
|_ assets\
  |_ installation\
  |_ sounds\
  |_ model_x.xx_x.xx.onnx
|_ bin\
  |_ execute.bat
  |_ install.bat
|_ videos\
|_ .gitignore
|_ main.py
```

## Guía de usuario
---
### Funcionalidad básica del programa

1. Lo primero que se realizará es la ejecución del programa, para esto se deberá ejecutar el archivo de lotes que se encuentra en la ruta `bin\execute.bat`.
2. El programa cargará y se abrirá junto con una ventana de comando, la cual se mantendrá abierta hasta que usted cierre la aplicación.
> No se preocupe por la consola, puede ignorarla.
3. El programa abrirá solo si detecta una cámara, si no existe ninguna, este le avisará en la consola que no detectó ningún dispotivo y procederá a cerrarse la aplicación.
> Una vez solucione el problema, agregando una cámara a la computadora, cierre la consola y vuelva a realizar los pasos desde el punto 1.
4. Cuando el programa haya abierto, lo que le aparecerá será lo siguiente:
![DesktopApplication](https://cdn.discordapp.com/attachments/879826886019129425/1114757281192624149/image.png)
  - Como se puede observar, en la parte de arriba aparece una barra desplegable que lista las cámaras que se han encontrado. Aquí se puede elegir la cámara con la que se quiere trabajar.
  - Más abajo y ocupando la mayoría de la pantalla, podrá encontrar el video en tiempo real que está captando de la cámara elegida.
  > Por defecto, la cámara seleccionada será la primera que aparezca en la lista.
5. Cuando se detecte un arma, la pantalla se modificará de la siguiente manera:
![DesktopApplication_Detected](https://cdn.discordapp.com/attachments/879826886019129425/1114758826793639936/image.png)
  - Ahora la imágen en tiempo real tiene un contorno rojo, y mientras el arma sea detectada, muestra la detección dentro de un recuadro junto a la etiqueta y la precisión con la que el modelo la detectó.
  - A la derecha de la muestra en tiempo real, se agregará una imágen del preciso momento en el que se detectó un arma, para que cuando sea alertado el operario y el arma que se detectó ya no aparezca en escena, este pueda saber donde se encontró el arma que activó la alarma.
  - Asimismo, se observa el botón `Cancelar Alerta`, el cual básicamente se encarga de apagar la alerta auditiva, la cual comenzará a sonar en el momento en el que se detecte un arma.

Adcionalmente, el programa grabará el momento en el que se detectó el arma durante unos 10 segundos, lo guardará en la ruta `videos\` en formato `mp4` y con la fecha y hora de la detección como nombre.
