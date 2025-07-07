import os
from typing import List
import random

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
        self.iteration = 0
        self.historic_map_actions = []
        self.historic_results = []
        self.stuck_counter = 0
        self.last_x_pos = 0
        self.num_baldosas = ((5000 - 1) // 16) + 1
        

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
        Función para generar la lista de acciones a utilizar en la iteración actual

        Esta (o estas) acción se debe generar como resultado de la implementación
        de la heurística que se le asignó a cada estudiante

        La (o las) lista de acciones generada debe cumplir con lo siguiente:
            Estructura que tiene como índice el número de la baldoza
            y como valor para esa baldoza almacenar el índice de la acción a realizar
            El número de la baldoza se obtiene según su implementación de pixel2cell.py
            El índice de la acción se obtiene según su implementación de acciones.py
        """

        print(f"\n=== Iteración {self.iteration} ===")
        self.iteration += 1

        if self.iteration == 1:
            print("Generando solución inicial...")
            current_solution = self.generate_initial_solution()
            initial_results = self.make_results(current_solution)
            attempts = 0
            while initial_results["status"] == "error" and attempts < 3:
                print(f"Reintentando solución inicial... (intento {attempts + 1})")
                current_solution = self.generate_initial_solution()
                initial_results = self.make_results(current_solution)
                attempts += 1
            if initial_results["status"] != "error":
                self.best_map_actions = current_solution
                self.best_map_actions_results = initial_results
        else:
            current_solution = self.best_map_actions.copy()

        print("\nSolución actual:", current_solution)

        local_solution, local_results = self.local_search(current_solution)

        if local_results["status"] == "error":
            print("Error detectado, aplicando patrones seguros...")
            local_solution = self.apply_safe_patterns(current_solution)
            local_results = self.make_results(local_solution)

        if local_results["status"] != "error" and self.eval_actions(local_results) > self.eval_actions(self.best_map_actions_results):
            print(f"Nueva mejor solución Score: {self.eval_actions(local_results)}")
            self.best_map_actions = local_solution
            self.best_map_actions_results = local_results

        return self.best_map_actions_to_list()

    def best_map_actions_to_list(self):
        map_actions = []
        for i in range(self.num_baldosas):
            map_actions.append(self.best_map_actions.get(i, 2))
        return map_actions

    def generate_initial_solution(self):
        num_actions = len(self.actions)
        solution = {i: random.randint(0, num_actions - 1) for i in range(self.num_baldosas)}
        return solution

    def local_search(self, solution):
        best_local = solution.copy()
        best_local_results = self.make_results(best_local)
        if best_local_results["status"] == "error":
            return best_local, best_local_results

        last_x_pos = best_local_results["x_pos"]
        stuck_counter = 0

        print(f"Inicio búsqueda local - X inicial: {last_x_pos}")

        for i in range(self.args.ls_iterations):
            print(f"\nIteración LS {i+1}/{self.args.ls_iterations}")
            new_solution = best_local.copy()
            new_results = self.make_results(new_solution)
            current_x = new_results["x_pos"]

            print(f"  Estado: {new_results['status']}, x_pos: {current_x}, stuck_counter: {stuck_counter}")

            if current_x == last_x_pos:
                stuck_counter += 1
            else:
                stuck_counter = 0
            last_x_pos = current_x

            if (new_results["status"] == "dead" or stuck_counter >= 5 or current_x <= best_local_results["x_pos"]):
                print(f"  Problema detectado. Aplicando perturbation en las últimas baldosas donde estuvo Mario.")
                new_solution = self.perturbation(
                    new_solution,
                    x_pos=current_x,
                    status=new_results["status"]
                )
                print(f"  Acciones tras perturbation: {[new_solution.get(j, '-') for j in range(self.num_baldosas-15, self.num_baldosas)]}")
                new_results = self.make_results(new_solution)
                stuck_counter = 0 

            if new_results["status"] != "error" and self.eval_actions(new_results) > self.eval_actions(best_local_results):
                print(f"Mejora encontrada Nuevo x_pos: {new_results['x_pos']}, score: {self.eval_actions(new_results)}")
                best_local = new_solution
                best_local_results = new_results
                last_x_pos = new_results["x_pos"]

        print(f"Fin búsqueda local. Mejor x_pos: {best_local_results['x_pos']}, score: {self.eval_actions(best_local_results)}")
        return best_local, best_local_results
    def apply_safe_patterns(self, solution):
        new_solution = solution.copy()
        for i in range(0, 100, 5):
            pattern = random.choice(self.safe_patterns)
            for j, action in enumerate(pattern):
                if i + j < 100:
                    new_solution[i + j] = action
        return new_solution

    def eval_actions(self, results):
        score = 0
        score += results["x_pos"] * 10
        if results["flag_get"]:
            score += 10000
        if results["status"] == "dead":
            score -= 10000
        score += results["coins"] * 2
        score += results["time"] * 2
        return score

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
        """
        En esta función debe definir su criterio de selección para actualizar
        la mejor solución (o las mejores) soluciones encontradas
        """
        results_eval = self.eval_actions(results)

        if results_eval == 0:
            self.best_map_actions = map_actions
            self.best_map_actions_results = results

    def criterio_de_termino(self):
        """
        En esta función debe definir su criterio de término.

        Sientase en libertad de agregar todos los parámetros y las salidas que necesite 
        """
        if self.best_map_actions_results["flag_get"] and self.best_map_actions_results["status"] != "dead":
            print("¡Nivel completado exitosamente!")
            return True
        return False

    def perturbation(self, solution, x_pos=None, status=None):
        """
        Perturba la solución modificando las últimas perturbation_size baldozas.
        Si se provee x_pos y status, comienza desde esa posición.
        Si no, modifica las últimas baldozas del nivel.
        """
        new_solution = solution.copy()
        num_actions = len(self.actions)
        
        if x_pos is not None and status is not None:
            problem_cell = self.conversion_pixel_baldoza(x_pos, status)
            # Comienza desde donde estuvo Mario por última vez
            start_fix = max(0, problem_cell - self.args.perturbation_size)
        else:
            # Si no hay posición específica, usa las últimas baldozas del nivel
            start_fix = max(0, self.num_baldosas - self.args.perturbation_size)
        
        print(f"Perturbando {self.args.perturbation_size} baldozas desde la posición {start_fix}")
        
        for j in range(self.args.perturbation_size):
            if start_fix + j < self.num_baldosas:
                new_solution[start_fix + j] = random.randint(0, num_actions - 1)
                
        return new_solution
    def train(self):
        print("Iniciando entrenamiento ILS...")

        if not self.best_map_actions:
            print("Generando solución inicial...")
            current_solution = self.generate_initial_solution()
            current_results = self.make_results(current_solution)
            attempts = 0
            while current_results["status"] == "error" and attempts < 3:
                print(f"Reintentando solución inicial... (intento {attempts + 1})")
                current_solution = self.generate_initial_solution()
                current_results = self.make_results(current_solution)
                attempts += 1
            self.best_map_actions = current_solution
            self.best_map_actions_results = current_results

        for i in range(self.args.n_training_steps):
            print(f"\n=== Iteración ILS {i+1}/{self.args.n_training_steps} ===")
            perturbed_solution = self.perturbation(self.best_map_actions)
            local_solution, local_results = self.local_search(perturbed_solution)
            if (local_results["status"] != "error" and
                self.eval_actions(local_results) > self.eval_actions(self.best_map_actions_results)):
                print(f"¡Nueva mejor solución global! Score: {self.eval_actions(local_results)}")
                self.best_map_actions = local_solution
                self.best_map_actions_results = local_results
            if (self.criterio_de_termino()):
                print("Criterio de término alcanzado.")
                print(f"Total de iteraciones: {i + 1}")
                break
            print(f"Posición alcanzada: {local_results['x_pos']}")
            print(f"Score: {self.eval_actions(local_results)}")

        self.save_simulation_results()