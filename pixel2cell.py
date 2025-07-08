# pixel2cell.py
# Necesitamos importar MAX_BALDOZA_INDEX que está en agente.py
# Esto puede causar una dependencia circular si agente.py también importa pixel2cell.py
# Una mejor práctica sería pasar MAX_BALDOZA_INDEX como argumento a la función
# O definir una constante global para el tamaño del mapa en un archivo de constantes.
# Por simplicidad y para que funcione rápidamente, lo importaremos aquí.
# Si tienes problemas de importación circular, podemos refactorizar.
from constants import MAX_BALDOZA_INDEX # Importar la constante

def conversion_pixel_baldoza(n_pixel: int, mario_status: str) -> int:
    """
    Esta función se llama automáticamente en el archivo mario_gym.py

    Traducción de pixeles a baldozas para la representación
    Esta función debe retornar el número de la baldoza en la que se encuentra
    Mario a partir de su posición horizontal en pixeles

    n_pixel:
        Posición horizontal desde la que se comienza a dibujar a Mario
        Es creciente hacia la derecha
    
    mario_status:
        String indicando el estado de Mario
        Inicialmente, Mario es pequeño por lo que su estado es "small"
        Si consume un champiñon rojo aumentará de tamaño y su estado será "big"
        Cuando Mario es "small", su tamaño horizontal es de 12 pixeles
        Cuando Mario es "big", su tamaño horizontal es de 16 pixeles
    
    Esta función debe retornar el número de la baldoza en la que se encuentra
    Mario según su posición en pixeles dentro del mapa
    
    El retorno debe ser un número entero!

    """

    baldoza_size = 16 # Cada baldoza mide 16 pixeles de ancho
    
    # La posición de Mario (n_pixel) dividida por el tamaño de la baldoza nos da el índice
    # Usamos división entera (//) para obtener un número entero de baldoza
    baldoza_idx = n_pixel // baldoza_size

    # Asegurarse de que el índice no exceda los límites de MAX_BALDOZA_INDEX
    # El rango de índices es de 0 a MAX_BALDOZA_INDEX - 1
    baldoza_idx = max(0, min(baldoza_idx, MAX_BALDOZA_INDEX - 1))

    return baldoza_idx
