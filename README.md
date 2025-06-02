# Proyecto de TEL352 - Seminario de Telemática II 

Repositorio base para el proyecto de la asignatura TEL352

**_RECUERDE ACTUALIZAR ESTE README CON LAS INSTRUCCIONES PARA EJECUTAR SU AGENTE_**

**_SI CREA NUEVOS ARCHIVOS, DEBE DESCRIBIRLOS BREVEMENTE EN LA ESTRUCTURA DEL REPOSITORIO_**

- **_Tienen total libertad para modificar las firmas de las funciones (inputs-outputs)_**
- **_Tienen total libertad para construir sus funciones o implementar sus heurísticas en archivos separados (por comodidad y orden), en caso de hacer eso se les pide construir el wrapper pertinente dentro de la clase definida en agente.py para mantener el flujo de la simulación (wrapper = crear un método nuevo en la clase que llame a la función que hicieron en un archivo separado)_**

## Configuración de entorno:

- Instalar Python 3.8
    - Se recomienda configurar un entorno de Python utilizando [Miniconda3](https://www.anaconda.com/docs/getting-started/miniconda/install), esto permitirá tener un entorno de desarrollo aislado y reproducible
        - Luego de instalar miniconda3 se puede crear el entorno virtual requerido con el siguiente comando: `conda create -n tel352 python=3.8`
        - Por último, activar el entorno virtual con el siguiente comando: `conda activate tel352`
- Instalar las librerias necesarias para el proyecto a partir del archivo requirements.txt
    - En la terminal, acceder al directorio del repositorio y ejecutar el siguiente comando: `pip install -r requirements.txt`

## Estructura del repositorio:

El repositorio consta de los siguientes archivos

- `acciones.py`: Contiene las combinaciones de acciones que considerará su algoritmo para generar la solución final (contiene todas las posibles combinaciones de acciones válidas para realizar en cualquier etapa de la simulación)
- `main.py`: Contiene la lógica 
- `setup.py`: Contiene la configuración de hiper-parámetros necesarios para la ejecución del programa, como el número de steps a realizar en cada etapa, entre otros (modificar a conveniencia)
- `todo`...

---

**_(EDITAR SI CREA ARCHIVOS)_** Archivos creados para la solución implementada:

- `archivo1`: descripción archivo1 

## Ejecución del programa:

El programa se debe ejecutar por medio del archivo `main.py`, para lo cual se puede utilizar el siguiente comando como base:
- `python main.py --n_frames 10000 --n_training_steps 100`
    - A la derecha de `main.py` van todos los argumentos o parámetros definidos en el archivo `setup.py`

**_(EDITAR LÍNEA DE COMANDO CON LOS PARÁMETROS AGREGADOS EN `setup.py` Y LOS VALORES UTILIZADOS POR SU AGENTE)_**

Línea de comando para ejecutar el programa:

- `python main.py --n_frames 10000 --n_training_steps 100`
