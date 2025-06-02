import argparse
from datetime import datetime


def main_parse_args(args):
    """
    Configuración de hiper-parámetros!
    Parsea los argumentos recibidos desde la línea de comandos
    """
    parser = argparse.ArgumentParser(description="TEL 352 - Agente Inteligente")
    
    # Flag para renderizar la ventana de Mario durante la ejecución
    # Puede ser útil no renderizar para acelerar el entrenamiento
    parser.add_argument("--render", action="store_true")
    
    # Configurar acorde al criterio de término elegido
    # La simulación (intento de completar el nivel) terminará una vez alcanzado los n_frames establecidos
    parser.add_argument("--n_frames", type=int, default=10000)

    # Número de steps o iteraciones para el entrenamiento de su algoritmo
    parser.add_argument("--n_training_steps", type=int, default=100)

    # Puede agregar todos los hiper-parámetros que estime necesario (tamaño de población, número de hormigas, etc)


    return parser.parse_args(args)