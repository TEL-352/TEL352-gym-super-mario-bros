from typing import List

def make_environment_actions() -> List[List[str]]:
    """
    Esta función retorna todas las combinaciones de acciones válidas que el agente
    puede utilizar durante la ejecución del entorno Super Mario Bros.
    """

    actions = [
        ["NOOP"],              # No hacer nada
        ["left", "B"],         # Ir a la izquierda corriendo
        ["right", "B"],        # Ir a la derecha corriendo
        ["right", "A"],        # Saltar hacia la derecha
        ["right", "A", "B"],   # Saltar y correr hacia la derecha
        ["A", "B"]              # Saltar en el lugar corriendo
    ]

    return actions
