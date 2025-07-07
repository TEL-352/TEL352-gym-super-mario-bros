# Proyecto de TEL352 - Seminario de Telemática II 

Repositorio base para el proyecto de la asignatura TEL352
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
- `agente.py`: Contiene el código principal para su agente inteligente. Este se compone de una clase con todos los métodos necesarios para implementar su heurística.
- `eval_setup.py`: Configuración para evaluar la solución de su agente. No se debe modificar.
- `eval.py`: Código para evaluar la solución de su agente. No se debe modificar.
- `main.py`: Contiene la lógica mínima necesaria para entrenar a su agente. No debería ser necesario modificarlo.
- `mario_gym.py`: Contiene el código necesario para que su agente pueda interactuar con el framework de Super Mario GYM. No se debe modificar.
- `pixel2cell.py`: Contiene la conversión que debe implementar para traducir la posición en pixeles de Mario a baldozas. Leer `REPRESENTACION.md` para más información.
- `requirements.txt`: Contiene las librerías que debe instalar en su entorno de python 3.8 para poder ejecutar el framework.
- `setup.py`: Contiene la configuración de hiper-parámetros necesarios para la ejecución del programa, como el número de steps a realizar en cada etapa, entre otros (modificar a conveniencia)

---


## Ejecución del programa:

El programa se debe ejecutar por medio del archivo `main.py`, para lo cual se puede utilizar el siguiente comando como base:
- `python main.py --n_frames 10000 --n_training_steps 300 --ls_iteration 15 --perturbation_size 10`
    - A la derecha de `main.py` van todos los argumentos o parámetros definidos en el archivo `setup.py`


Línea de comando para ejecutar el programa:

- `python main.py --n_frames 10000 --n_training_steps 300 --ls_iteration 15 --perturbation_size 10`

## Evaluación del agente:

Una vez finalizada la ejecución de su agente, debería aparecer un nuevo directorio en su repositorio con el nombre `outputs`. Este directorio contiene los resultados de la simulación (acciones y resultados históricos junto a la mejor solución encontrada).

Para evaluar su agente se debe ejecutar el archivo `eval.py`. Este archivo puede recibir como argumentos el flag `--render` para renderizar el juego ejecutando sus acciones y `--date YYYY_MM_DD_HH_mm_ss` para elegir la fecha que de la solución que se quiere evaluar. Por ejemplo, si al ejecutar el archivo `main.py` se genera dentro de `outputs` el archivo `2025_06_01_10_15_17_simulation_results.pkl`, podemos evaluar esta solución ejecutando la siguiente línea de comando:

- `python eval.py --render --date 2025_07_04_20_57_11`