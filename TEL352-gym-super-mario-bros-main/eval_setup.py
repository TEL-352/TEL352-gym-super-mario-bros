import argparse


def eval_parse_args(args):
    """
    Configuración para evaluar resultados del agente!
    Parsea los argumentos recibidos desde la línea de comandos
    """
    parser = argparse.ArgumentParser(description="TEL 352 - Agente Inteligente - Eval")
    
    # Flag para renderizar la ventana de Mario durante la ejecución
    # Puede ser útil no renderizar para acelerar el entrenamiento
    parser.add_argument("--render", action="store_true")
    
    # Fecha de la simulación que desea evaluar
    # debe ir en formato "YYYY_MM_DD_HH_mm_ss" (año_mes_dia_horas_minutos_segundos)
    # por ejemplo: "2025_06_01_10_35_01"
    parser.add_argument("--date", type=str, default="")

    return parser.parse_args(args)