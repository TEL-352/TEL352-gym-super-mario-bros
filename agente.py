from typing import List

class SuperMarioAgenteTEL:
    def __init__(self):
        self.actions = self.make_list_of_actions()

        # boolean para indicar si se quiere renderizar el juego o no
        # es util tenerlo en False durante el entrenamiento para acelerar la ejecución
        self.render = True

        # número de steps o iteraciones para la simulación
        self.n_steps = 5000

    def get_actions(self) -> List[List[str]]:
        # Auxiliar para darle a conocer al entorno las acciones disponibles
        # no modificar
        return self.actions
    
    def get_render(self) -> bool:
        # Auxiliar para darle a conocer al entorno si queremos que renderice el juego
        # no modificar
        return self.render
    
    def get_n_steps(self) -> int:
        # Auxiliar para darle a conocer al entorno la cantidad de steps o iteraciones que haremos
        # no modificar
        return self.n_steps

    def make_list_of_actions(self) -> List[List[str]]:
        # Esta función debe retornar una lista que contenga
        # todas las combinaciones de acciones
        # que su agente inteligente podrá utilizar durante la ejecución.
        #
        # El formato final de actions corresponde a una lista de listas
        # en donde cada sublista contendrá posibles acciones
        # a realizar durante cada frame
        #
        # por ejemplo, la siguiente lista indica que las opciones disponibles
        # en cada frame son "right" o "left": 
        # actions = [["right"], ["left"]]
        #
        # Acciones disponibles por cada frame:
        #
        # "NOOP": no presiona ningún botón
        #
        # "right": presiona el botón para hacer avanzar a Mario hacia la derecha
        #
        # "left": presiona el botón para hacer avanzar a Mario hacia la izquierda
        #
        # "down": presiona el botón para hacer avanzar a Mario hacia abajo
        #           (útil para entrar en una tubería o para bajar cuando Mario escala)
        #
        # "up": presiona el botón para hacer avanzar a Mario hacia arriba
        #           (útil para subir cuando Mario escala)
        #
        # "A": presiona el botón para hacer saltar a Mario
        #           Si se presiona durante varios frames consecutivos,
        #           Mario saltará más alto hasta alcanzar la máxima altura
        #
        # "B": presiona el botón para hacer correr a Mario
        #           Se debe presionar consecutivamente durante varios frames para notar la diferencia
        #
        # Es posible presionar más de un botón por frame, por ejemplo, la lista
        # actions = [["right", "B", "A"]]
        # indica que el agente deberá presionar simultáneamente los botones "right", "B" y "A"
        #
        # A partir de aqui construya su lista de acciones permitidas

        # placeholder, reemplazar por lista propia
        actions = [["right", "B"], ["right", "A"], ["right", "A"], ["A", "B"]]

        return actions 

    def get_next_action(self, state, reward, info) -> int:
        # En esta función defina como su agente procesará el state observado
        # para generar la acción que deberá ejecutar en el siguiente frame
        #
        # Para ello cuenta con el state y el reward generados
        # a partir de la última acción ejecutada
        #
        # state: arreglo numpy con los valores rgb que permiten dibujar el último frame observado
        #
        # reward: float,
        #           Es mayor a 0.0 cuando Mario realiza avances hacia el final del nivel
        #           Es 0.0 cuando Mario no se mueve o se queda atascado en alguna parte
        #           Es menor a 0.0 cuando Mario retrocede o realiza "avance negativo"
        #
        # info: diccionario, contiene información adicional generada a partir del frame anterior
        #       que podría ser relevante para su agente:
        #           "coins": int con el número de monedas recolectadas
        #           "flag_get": bool que indica si se llegó a la bandera o no
        #           "life": int con la cantidad de vidas restantes
        #           "score": int con el puntaje actual de Mario
        #           "world": int con el número del mundo que se está jugando
        #           "stage": int con el número del nivel que se está jugando
        #           "status": "small" cuando Mario es pequeño (estado inicial), "big" cuando consume un champiñon
        #           "time": int con el tiempo restante para completar el nivel, si llega a 0 Mario pierde
        #           "x_pos": int con la posición de Mario en el eje X del nivel
        #           "y_pos": int con la posición de Mario en el eje Y del nivel}
        #
        #
        # El retorno de esta función corresponde al índice de la acción que se ejecutará
        # a partir de la lista construida en la función make_list_of_actions
        #
        # placeholder, reemplazar con lógica de su agente inteligente
        import random

        next_action = random.choice(range(len(self.actions)))

        return next_action
