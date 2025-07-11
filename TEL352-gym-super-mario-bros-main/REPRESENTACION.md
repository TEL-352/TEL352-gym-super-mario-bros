Para la representación de la solución se optó por acotar el espacio de búsqueda por baldozas. En el universo de *Super Mario Bros*, cada baldoza tiene un tamaño de 16x16 pixeles, mientras que la posición de Mario viene dada por coordenadas X e Y, ambas en pixeles. La coordenada X comienza desde el pixel 1 (punto en el extremo izquierdo del nivel) y va aumentando a medida que Mario llega al final del nivel (punto en el extremo derecho del mapa)

Información que puede ser relevante para su implementación:

- En el nivel 1, Mario comienza en el pixel horizontal número 40, el pixel que se encuentra más hacia la izquierda es el número 1, mientras que el pixel que se encuentra más hacia la derecha (en el final del nivel) tiene un número desconocido (se estima que un nivel de Mario puede tener hasta 2560 pixeles de largo). Solo sabemos que los números de pixeles aumentan a medida que Mario avanza hacia la derecha.

- La posición de Mario en pixeles indica que el "dibujo" o "sprite" de Mario se comienza a dibujar a partir de ese pixel, por ejemplo, si la posición recibida indica que Mario está en el pixel 40, significa que Mario comenzará a dibujarse desde el pixel 40 en adelante. Mario tiene un ancho de 16 pixeles cuando es grande (y 12 pixeles cuando es pequeño), por lo que en este caso sabremos que Mario grande estará ubicado entre el pixel 40 y el 56 (40 + 16), y que su centro estará en el pixel número 48 (40 + 16/2), mientras que Mario pequeño estará entre el pixel 40 y el 52 (40 + 12)

- En el archivo `pixel2cell.py` debe definir su conversión de pixel a baldoza. La conversión por default retorna 1 por lo que deberás modificarla según tu interpretación y según la implementación que quieran realizar para que el agente no se quede repitiendo siempre la misma acción

# Representación basada en posiciones (cuadro/baldosa + acción)

Supongamos que su lista de acciones válidas es la siguiente:

```python
actions = [
    ["NOOP"],
    ["left", "B"],
    ["right", "B"],
    ["right", "A"],
    ["right", "A", "B"],
    ["A", "B"],
]
```

El framework de Super Mario recibirá esta lista de acciones posibles al inicio de la ejecución, y en cada evaluación decidirá que acción utilizar en base al índice que le entreguemos.

Por ejemplo, si queremos que Mario __*corra*__ hacia la __*derecha*__ en un determinado momento, deberemos decirle que presione la combinación de botones almacenada en el __índice 2__ de la lista que le entregamos, equivalente a `["right", "B"]`. 

## Estructura:

Algunas maneras para llevar esta representación al espacio de solución son las siguientes:

```python
# Diccionario donde la llave es el número de la baldoza y
# el valor es la combinación de botones a presionar
# mientras Mario se encuentre en esa baldoza

acciones_por_posicion = {
    1: 1,   # Acción a realizar en la baldoza 1, se traduce internamente a actions[2]
    2: 4,   # Acción a realizar en la baldoza 2, se traduce internamente a actions[5]
    3: 1,   # Acción a realizar en la baldoza 3, se traduce internamente a actions[2]
    ...,
    n: idx, # Acción a realizar en la baldoza n, se traduce internamente a actions[idx]
}
```


```python
# Lista donde el índice corresponde al número de la baldoza y el valor almacenado en ese índice es la combinación de botones a presionar mientras Mario se encuentre en esa baldoza
acciones_por_posicion = [
    0,      # Acción a realizar en la baldoza 0, se traduce internamente a actions[0]
    2,      # Acción a realizar en la baldoza 1, se traduce internamente a actions[2]
    5,      # Acción a realizar en la baldoza 2, se traduce internamente a actions[5]
    ...,
    idx,    # Acción a realizar en la baldoza n, se traduce internamente a actions[idx]
]
```

Son libres de utilizar la estructura que más les acomode, solo mantengan en mente que al momento de ejecutar su solución el framework usará el número de la baldoza para obtener la combinación de acciones, por lo que debe ir vinculado de alguna manera con el índice de la estructura que utilicen.

Mientras su estructura reciba como __entrada el número de la baldoza__ y genere como __salida el índice de la acción__ a realizar (en base a su definición en `actions.py`), la ejecución debería funcionar.
