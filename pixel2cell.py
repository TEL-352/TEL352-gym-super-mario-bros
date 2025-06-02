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

    baldoza_size = 16
    mario_size = 16

    if mario_status == "small":
        mario_size = 12

    # Modificar retorno
    # El retorno debe ser un número entero!
    return 1