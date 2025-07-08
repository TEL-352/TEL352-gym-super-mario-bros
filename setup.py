import argparse
from datetime import datetime


def main_parse_args(args):
    """
    Configuración de hiper-parámetros!
    Parsea los argumentos recibidos desde la línea de comandos
    """
    parser = argparse.ArgumentParser(description="TEL 352 - Agente Inteligente con Búsqueda Tabú")
    
    # --- Parámetros de Ejecución ---
    parser.add_argument("--render", action="store_true", help="Renderiza cada simulación. Ralentiza masivamente el entrenamiento.")
    parser.add_argument("--render_progress", action="store_true", help="Renderiza una simulación cada vez que se encuentra una nueva mejor solución.")
    
    # --- NUEVO ARGUMENTO ---
    parser.add_argument("--load_from", type=str, default=None, help="Ruta al archivo .pkl de una simulación anterior para continuar el entrenamiento (ej. outputs/2023_10_28_10_30_00_simulation_results.pkl).")
    
    # --- Parámetros de Simulación y Entrenamiento ---
    parser.add_argument("--n_frames", type=int, default=10000)
    parser.add_argument("--n_training_steps", type=int, default=100)

    # --- Parámetros para la Búsqueda Tabú ---
    parser.add_argument("--n_tiles", type=int, default=220, help="Número de baldosas en el vector de solución.")
    parser.add_argument("--n_neighbors", type=int, default=30, help="Número de vecinos a generar por iteración.")
    parser.add_argument("--tabu_tenure", type=int, default=15, help="Número de iteraciones que un movimiento permanece tabú.")

    return parser.parse_args(args)