# Archivo: setup.py
import argparse
from datetime import datetime


def main_parse_args(args):
    """
    Configuración de hiper-parámetros!
    Parsea los argumentos recibidos desde la línea de comandos
    """
    parser = argparse.ArgumentParser(description="TEL 352 - Agente Inteligente con Estrategias Evolutivas")

    # --- Parámetros Generales ---
    # Flag para renderizar la ventana de Mario durante la ejecución
    parser.add_argument("--render", action="store_true")

    # La simulación (intento de completar el nivel) terminará una vez alcanzado los n_frames establecidos
    parser.add_argument("--n_frames", type=int, default=10000)

    # Número de generaciones para el entrenamiento del algoritmo
    parser.add_argument("--n_training_steps", type=int, default=100, help="Número de generaciones de la Estrategia Evolutiva.")

    # --- Parámetros de Estrategias Evolutivas (ES) ---
    parser.add_argument("--mu", type=int, default=15, help="Tamaño de la población de padres (μ).")
    parser.add_argument("--lambda_", type=int, default=15, help="Número de descendientes a generar (λ).")
    parser.add_argument("--longitud_genoma", type=int, default=200, help="Número de baldosas a considerar en la solución (largo del cromosoma).")
    parser.add_argument("--tasa_aprendizaje_mutacion", type=float, default=0.1, help="Tasa de aprendizaje para la autoadaptación de las tasas de mutación.")


    return parser.parse_args(args)