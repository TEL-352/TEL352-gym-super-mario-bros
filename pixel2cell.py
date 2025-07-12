import math

def conversion_pixel_baldoza(n_pixel: int, mario_status: str) -> int:
    """
    Esta función se llama automáticamente en el archivo mario_gym.py

    Traducción de pixeles a baldozas para la representación.
    Esta función debe retornar el número de la baldoza en la que se encuentra
    Mario a partir de su posición horizontal en pixeles.

    n_pixel:
        Posición horizontal desde la que se comienza a dibujar a Mario.
        Es creciente hacia la derecha.
    
    mario_status:
        String indicando el estado de Mario.
        "small", "big" o "fire".
        Cuando Mario es "small", su tamaño horizontal es de 12 pixeles.
        Cuando Mario es "big" o "fire", su tamaño horizontal es de 16 pixeles.
    
    El retorno debe ser un número entero que representa el índice de la baldosa.
    """

    baldoza_size = 16
    mario_width = 12 if mario_status == "big" else 16

    # Calculamos la posición del centro del sprite de Mario
    posicion_centro_mario = n_pixel + (mario_width / 2)

    # Convertimos la posición del centro a un número de baldosa
    numero_baldosa = int(posicion_centro_mario // baldoza_size)

    return max(0, numero_baldosa) # Aseguramos que no retorne un número negativo
