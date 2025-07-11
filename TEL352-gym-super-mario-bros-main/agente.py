import os
from typing import List

from deap import base, creator, tools
import random
import numpy as np


import cloudpickle
import datetime

from acciones import make_environment_actions
from mario_gym import run_simulation
from pixel2cell import conversion_pixel_baldoza


class SuperMarioAgenteTEL:
    def __init__(self, args):
        # Recibe los argumentos enviados por la línea de comando
        self.args = args

        # Define las acciones váldias para el entorno según lo definido en acciones.py
        self.actions = self.make_environment_actions()

        # Almacena el mapeo de acciones a realizar por cada baldoza
        # Se debe actualizar con el mejor mapeo de acciones encontrado en cada iteración
        # puede no ser un diccionario, ajustar a conveniencia (ver REPRESENTACION.md)
        self.best_map_actions = {}
        self.best_map_actions_results = {
            "coins": 0,
            "flag_get": False,
            "life": 2,
            "score": 0,
            "stage": 1,
            "status": "dead",
            "time": 400,
            "world": 1,
            "x_pos": 1,
            "y_pos": 79
        }

        # Almacena el histórico del mapeo de acciones y de sus resultados
        # Se debe actualizar en cada ejecución para ir llevando un registro histórico
        # y facilitar la comparación de desempeño entre cada step
        self.historic_map_actions = []
        self.historic_results = []

        # Sientanse en libertad de agregar todos los atributos
        # que necesiten para su agente

    def conversion_pixel_baldoza(self, n_pixel: int, mario_status: str) -> int:
        """
        Wrapper para que la clase tenga acceso a la funcón definida en pixel2cell.py
        Modificar directamente el archivo pixel2cell.py
        No modificar este método
        """
        return conversion_pixel_baldoza(n_pixel, mario_status)

    def make_environment_actions(self) -> List[List[str]]:
        """
        Wrapper para que la clase tenga acceso a la funcón definida en acciones.py
        Modificar directamente el archivo acciones.py
        No modificar este método
        """
        return make_environment_actions()

    def save_simulation_results(self):
        """
        Función para guardar una copia de las acciones y resultados históricos
        y también el mejor map_actions generado por su agente para luego ser evaluado
        """
        time_now = datetime.datetime.now()
        time_now = time_now.strftime("%Y_%m_%d_%H_%M_%S")

        backup_data = {
            "historic_actions": self.historic_map_actions,
            "historic_results": self.historic_results,
            "best_actions": self.best_map_actions,
            "best_results": self.best_map_actions_results,
        }

        backup_file_name = f"{time_now}_simulation_results.pkl"
        outdir = "outputs/"
        os.makedirs(outdir, exist_ok=True)

        with open(f"{outdir}/{backup_file_name}", mode="wb") as file:
            cloudpickle.dump(backup_data, file)

    def run_simulation(self, map_actions):
        """
        Wrapper para que la clase tenga acceso a la funcón definida en mario_gym.py
        No modificar ni la función original ni este método

        Ejecuta una simulación utilizando
        el mapeo de acciones generado por su agente
        El único objetivo de esta función es ejecutar
        las acciones generadas por su agente en el nivel 1 de Mario
        """
        
        return run_simulation(
            self.args,
            map_actions,
            self.make_environment_actions(),
            self.conversion_pixel_baldoza,
        )


    def make_next_actions(self):
        """
        Convierte el mejor individuo actual en un map_actions usable
        """
        map_actions = {}
        for baldoza, action_idx in enumerate(self.best_individuo):
            map_actions[baldoza] = action_idx
        return map_actions
    
    

    def make_results(self, map_actions):
        """
        No modificar
        Esta función solo ejecuta el run_simulations para generar los resultados
        a partir del map_actions generado por el agente
        En esta función se explican los contenidos de los resultados
        puede ser útil al momento de decidir un criterio de evaluación para su agente

        map_actions:
            Estructura que tiene como índice el número de la baldoza
            y como valor para esa baldoza retorna el índice de la acción a realizar
            El número de la baldoza se obtiene según su implementación de pixel2cell.py
            El índice de la acción se obtiene según su implementación de acciones.py
        """
        results = self.run_simulation(map_actions)

        """
        results es un diccionario con las siguientes llaves:
          "coins":
              int con el número de monedas recolectadas
          "flag_get":
              bool que indica si se llegó a la bandera (True) o no (False)
          "life":
              int con la cantidad de vidas restantes
              Inicialmente es 2, puede aumentar cada vez que
              Mario consigue un champiñon verde o recolecta 100 monedas
              En teoría nunca disminuirá, para eso esta el "status" con valor "dead"
          "score":
              int con el puntaje actual de Mario
          "world":
              int con el número del mundo que se está jugando
          "stage":
              int con el número del nivel que se está jugando
          "status":
              "small" cuando Mario es pequeño (estado inicial),
              "big" cuando consume un champiñon,
              "dead" cuando Mario pierde ante alguno de los obstáculos del nivel
              "error" cuando el agente no tiene una acción definida para una determinada baldoza
          "time":
              int con el tiempo restante para completar el nivel, si llega a 0 Mario pierde
              Inicialmente tiene valor 400 y va disminuyendo hasta llegar a 0 a medida que avanza el juego
          "x_pos":
              int con la posición de Mario en el eje X del nivel
          "y_pos":
              int con la posición de Mario en el eje Y del nivel
        """

        return results

    

    def update_best_map_action(self, map_actions, results):
        results_eval = self.eval_actions(results)
        best_eval = self.eval_actions(self.best_map_actions_results)

        if results_eval > best_eval:
            self.best_map_actions = map_actions
            self.best_map_actions_results = results
    
    def eval_actions(self, results):
        x = results["x_pos"]
        score = results["score"]

        if results["status"] == "error":
            return -1000
        if results["status"] == "stuck":
            return x - 100 + score // 10
        if results["status"] == "dead":
            return x - 200 + score // 10
        if results["flag_get"]:
            return 10000
        return x + score // 10

    def criterio_de_termino(self):
        """
        En esta función debe definir su criterio de término.

        Sientase en libertad de agregar todos los parámetros y las salidas que necesite 
        """

        return True
    
    

    def train(self):
        # --- Parámetros Evolutivos ---
        TAM_POBLACION = 30
        N_GENERACIONES = self.args.n_training_steps
        N_BALDOZAS = 50  # Ajuste si hay más
        N_ACCIONES = len(self.actions)

        # --- Definir estructura DEAP ---
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        toolbox = base.Toolbox()
        toolbox.register("attr_action", random.randrange, N_ACCIONES)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_action, n=N_BALDOZAS)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        
        def evaluar(individuo):
            map_actions = {i: act for i, act in enumerate(individuo)}
            resultados = self.run_simulation(map_actions)
            return (self.eval_actions(resultados),)

        toolbox.register("evaluate", evaluar)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutUniformInt, low=0, up=N_ACCIONES - 1, indpb=0.1)
        toolbox.register("select", tools.selTournament, tournsize=3)

        # --- Entrenamiento Evolutivo ---
        #poblacion = toolbox.population(n=TAM_POBLACION)
        poblacion = []
        for _ in range(TAM_POBLACION):
            individuo = [3] * 10 + [random.randint(0, N_ACCIONES - 1) for _ in range(N_BALDOZAS - 10)]
            poblacion.append(creator.Individual(individuo))
        mejores_individuos = []
        try:
            for gen in range(N_GENERACIONES):
                self.args.render = (gen == N_GENERACIONES - 1)
                # Evaluar fitness
                fitnesses = list(map(toolbox.evaluate, poblacion))
                for ind, fit in zip(poblacion, fitnesses):
                    ind.fitness.values = fit

                # Guardar mejor
                top = tools.selBest(poblacion, k=1)[0]
                self.best_individuo = list(top)



                self.best_individuo = list(top)
                mapa = {i: act for i, act in enumerate(top)}
                resultados = self.make_results(mapa)

                self.historic_map_actions.append(mapa)
                self.historic_results.append(resultados)
                self.update_best_map_action(mapa, resultados)

                # Reproducir nueva generación
                offspring = toolbox.select(poblacion, len(poblacion))
                offspring = list(map(toolbox.clone, offspring))

                for child1, child2 in zip(offspring[::2], offspring[1::2]):
                    if random.random() < 0.9:
                        toolbox.mate(child1, child2)
                        del child1.fitness.values
                        del child2.fitness.values

                for mutant in offspring:
                    if random.random() < 0.2:
                        toolbox.mutate(mutant)
                        del mutant.fitness.values

                poblacion[:] = offspring

                print(f"[Gen {gen+1}] Fitness: {top.fitness.values[0]} | x_pos: {resultados['x_pos']} | status: {resultados['status']}")
        except KeyboardInterrupt:
            print("Entrenamiento interrumpido por el usuario. Se guardará lo aprendido.")
            self.save_simulation_results()

        self.save_simulation_results()

    
