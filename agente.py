import os
from typing import List
import cloudpickle
import datetime
import random
import math # Para la función exponencial

# Suponiendo que estas funciones existen en otros archivos como se indica
from acciones import make_environment_actions
from mario_gym import run_simulation
from pixel2cell import conversion_pixel_baldoza

# --- PARÁMETROS DE RECOCIDO SIMULADO (AJUSTAR SEGÚN NECESIDAD) ---
# Si no usas self.args, puedes definirlos aquí directamente o pasarlos al constructor
DEFAULT_INITIAL_TEMPERATURE = 1000.0  # Temperatura inicial alta para exploración
DEFAULT_COOLING_RATE = 0.99           # Tasa de enfriamiento (ej. 0.99 para enfriamiento geométrico)
DEFAULT_MIN_TEMPERATURE = 0.1         # Temperatura mínima para criterio de término
DEFAULT_MAX_ITERATIONS = 5000         # Máximo de iteraciones si no hay args.n_training_steps

# --- PARÁMETROS DE LA FUNCIÓN DE COSTO (AJUSTAR PESOS PARA CADA OBJETIVO) ---
WEIGHT_X_POS = 1.0     # Recompensar avance horizontal
WEIGHT_SCORE = 0.1     # Recompensar puntaje
WEIGHT_COINS = 1.0     # Recompensar monedas (asumiendo que valen más que el score base por punto)
WEIGHT_TIME = 0.5      # Recompensar tiempo restante
PENALTY_NO_FLAG = 1000000 # Gran penalización por no llegar a la bandera
PENALTY_DEAD = 10000000 # Penalización masiva por morir
PENALTY_ERROR = 5000000 # Penalización por acciones no definidas

# --- PARÁMETROS DE LA REPRESENTACIÓN DE ACCIONES ---
# Mario 1-1 tiene ~3200 pixeles de largo. Si una baldoza es de 16x16 pixeles, son ~200 baldozas.
# Se recomienda un valor ligeramente mayor para cubrir posibles saltos o errores.
MAX_BALDOZA_INDEX = 250 # Número máximo de baldozas para las que se almacenará una acción

class SuperMarioAgenteTEL:
    def __init__(self, args):
        self.args = args

        # Define las acciones válidas para el entorno
        self.actions = self.make_environment_actions()
        self.num_possible_actions = len(self.actions) # Cuántas combinaciones de acciones hay

        # Atributos específicos de Recocido Simulado
        self.initial_temperature = getattr(args, 'initial_temperature', DEFAULT_INITIAL_TEMPERATURE)
        self.cooling_rate = getattr(args, 'cooling_rate', DEFAULT_COOLING_RATE)
        self.min_temperature = getattr(args, 'min_temperature', DEFAULT_MIN_TEMPERATURE)
        self.current_temperature = self.initial_temperature

        # Inicializa best_map_actions_results con un estado por defecto antes de usarlo
        self.best_map_actions_results = {
            "coins": 0,
            "flag_get": False,
            "life": 2,
            "score": 0,
            "stage": 1,
            "status": "initial", # Puedes cambiar a "initial" o "running"
            "time": 400,
            "world": 1,
            "x_pos": 1,
            "y_pos": 79
        }

        # current_map_actions se inicializa al inicio del entrenamiento
        self.current_map_actions = self._initialize_map_actions()

        # Ahora current_results puede usar una copia del diccionario por defecto
        self.current_results = self.best_map_actions_results.copy()
        self.current_cost = float('inf') # Costo inicial alto, se actualizará en train()

        # best_map_actions y best_cost se inicializan con la solución actual al inicio
        self.best_map_actions = list(self.current_map_actions) # Se actualizará durante el entrenamiento
        self.best_cost = float('inf') # El costo de la mejor solución encontrada, se actualizará en train()

        # Histórico de mapeos de acciones y resultados para seguimiento
        self.historic_map_actions = []
        self.historic_results = []
        self.historic_costs = [] # Para llevar un registro de la evolución del costo

        print(f"Agente Recocido Simulado inicializado con T_inicial={self.initial_temperature}, "
              f"cooling_rate={self.cooling_rate}, baldozas_max={MAX_BALDOZA_INDEX}, "
              f"acciones_posibles={self.num_possible_actions}")

    def _initialize_map_actions(self) -> List[int]:
        """
        Inicializa un 'map_actions' para todas las baldozas posibles.
        Una buena estrategia inicial es que Mario siempre intente ir a la derecha.
        Asumimos que el índice 1 corresponde a la acción 'right'.
        Si 'right' no es el índice 1, ajustar.
        """
        initial_action_index_for_right = -1
        # Intentar encontrar el índice de la acción 'right'
        for i, action_list in enumerate(self.actions):
            if action_list == ['right']:
                initial_action_index_for_right = i
                break
        
        # Si no se encuentra 'right', usar una acción por defecto (ej. NOOP o la primera acción)
        if initial_action_index_for_right == -1 and self.num_possible_actions > 0:
            initial_action_index_for_right = 0 # O la acción que represente "NOOP"
            print("Advertencia: No se encontró la acción 'right'. Inicializando con la primera acción disponible.")
        elif self.num_possible_actions == 0:
             raise ValueError("No hay acciones definidas en make_environment_actions().")


        # Inicializar todas las baldozas con la acción de ir a la derecha (o la acción por defecto)
        return [initial_action_index_for_right] * MAX_BALDOZA_INDEX

    def conversion_pixel_baldoza(self, n_pixel: int, mario_status: str) -> int:
        """
        Wrapper para que la clase tenga acceso a la funcón definida en pixel2cell.py
        Modificar directamente el archivo pixel2cell.py
        No modificar este método
        """
        # Asegúrate de que esta función devuelve un índice dentro de [0, MAX_BALDOZA_INDEX-1]
        baldoza_index = conversion_pixel_baldoza(n_pixel, mario_status)
        return min(baldoza_index, MAX_BALDOZA_INDEX - 1) # Asegura que no exceda el límite

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
            "historic_costs": self.historic_costs, # Guardar también el historial de costos
            "best_actions": self.best_map_actions,
            "best_results": self.best_map_actions_results,
            "best_cost": self.best_cost, # Guardar el mejor costo
            "final_temperature": self.current_temperature
        }

        outdir = "outputs/"
        os.makedirs(outdir, exist_ok=True)
        backup_file_name = f"{outdir}/{time_now}_sa_simulation_results.pkl"

        with open(backup_file_name, mode="wb") as file:
            cloudpickle.dump(backup_data, file)
        print(f"Resultados de simulación guardados en: {backup_file_name}")

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

    def make_next_actions(self) -> List[int]:
        """
        Función para generar una solución "vecina" (neighbor)
        a partir del `self.current_map_actions`.

        Esto se hace tomando una copia de la solución actual y
        modificando aleatoriamente la acción para una baldoza al azar.
        """
        neighbor_map_actions = list(self.current_map_actions) # Copia de la solución actual

        # Selecciona un índice de baldoza aleatorio para modificar
        # Asegúrate de que el índice esté dentro del rango de MAX_BALDOZA_INDEX
        baldoza_to_change_idx = random.randint(0, MAX_BALDOZA_INDEX - 1)

        # Selecciona una nueva acción aleatoria para esa baldoza
        new_action_idx = random.randint(0, self.num_possible_actions - 1)

        # Aplica el cambio
        neighbor_map_actions[baldoza_to_change_idx] = new_action_idx

        return neighbor_map_actions

    def make_results(self, map_actions):
        """
        No modificar
        Esta función solo ejecuta el run_simulations para generar los resultados
        a partir del map_actions generado por el agente
        """
        results = self.run_simulation(map_actions)
        return results

    def eval_actions(self, results) -> float:
        """
        Función de evaluación (función de costo) para el Recocido Simulado.
        El objetivo es MINIMIZAR este valor.

        Un costo menor significa una mejor solución.
        Se prioriza llegar a la bandera, luego la x_pos, el tiempo, el puntaje y las monedas.
        Se penaliza morir o errores.
        """
        cost = 0.0

        # Penalizaciones por estados de fallo
        if results["status"] == "dead":
            cost += PENALTY_DEAD
        elif results["status"] == "error":
            cost += PENALTY_ERROR

        # Penalización por no llegar a la bandera
        if not results["flag_get"]:
            cost += PENALTY_NO_FLAG
            # Si no llegó a la bandera, el x_pos es muy importante
            # Cuanto más avance, menor será el costo (x_pos max es ~3200)
            # Normalizar para que x_pos sea un valor que se resta al costo base.
            # Max_x_pos podría ser 3200-3400. Una forma de convertir x_pos a costo es:
            # costo = (MAX_POS_EN_NIVEL - x_pos) * peso_x_pos
            # Si x_pos es 3200, entonces costo es 0. Si x_pos es 0, costo es MAX_POS_EN_NIVEL * peso.
            MAX_X_LEVEL_1 = 3200 # Asumimos la longitud máxima de Mario 1-1 en pixeles
            cost += (MAX_X_LEVEL_1 - results["x_pos"]) * WEIGHT_X_POS
        else:
            # Si llega a la bandera, su x_pos no es tan relevante,
            # lo importante es qué tan rápido (tiempo) y qué tan bien (score, coins) lo hizo.
            cost -= results["x_pos"] * WEIGHT_X_POS * 0.1 # Menor peso para x_pos si ya llegó a la meta


        # Restar los elementos que queremos maximizar (para minimizar el costo total)
        cost -= results["score"] * WEIGHT_SCORE
        cost -= results["coins"] * WEIGHT_COINS
        cost -= results["time"] * WEIGHT_TIME # Recompensa por tiempo restante

        return cost

    def update_best_map_action(self, map_actions, results, cost):
        """
        Actualiza la mejor solución GLOBAL encontrada hasta el momento.
        """
        if cost < self.best_cost:
            self.best_cost = cost
            self.best_map_actions = list(map_actions) # Asegurarse de copiar la lista
            self.best_map_actions_results = results.copy()
            print(f"  Nuevo mejor costo global: {self.best_cost:.2f}, X_pos: {results['x_pos']}, Flag: {results['flag_get']}, Status: {results['status']}")

    def criterio_de_termino(self, iteration: int) -> bool:
        """
        Define el criterio de término para el algoritmo de Recocido Simulado.
        Puede ser por número máximo de iteraciones, temperatura mínima,
        o si no hay mejora significativa después de muchas iteraciones.
        """
        max_iterations = getattr(self.args, 'n_training_steps', DEFAULT_MAX_ITERATIONS)
        
        # Criterio 1: Temperatura muy baja
        if self.current_temperature < self.min_temperature:
            print(f"Criterio de término: Temperatura mínima alcanzada ({self.current_temperature:.2f} < {self.min_temperature:.2f}).")
            return True
        
        # Criterio 2: Número máximo de iteraciones
        if iteration >= max_iterations:
            print(f"Criterio de término: Máximo de iteraciones alcanzado ({iteration} >= {max_iterations}).")
            return True
            
        return False

    def train(self):
        """
        Implementación del ciclo de entrenamiento para el Recocido Simulado.
        """
        print("\nIniciando entrenamiento del agente con Recocido Simulado...")

        # Inicializar la solución actual y su costo
        # La solución inicial es self.current_map_actions
        print("Ejecutando simulación inicial para establecer el estado actual y mejor estado...")
        initial_results = self.make_results(self.current_map_actions) # Usa current_map_actions ya inicializado
        self.current_results = initial_results.copy()
        self.current_cost = self.eval_actions(initial_results)

        # La solución inicial es la mejor encontrada hasta ahora
        self.best_map_actions = list(self.current_map_actions)
        self.best_map_actions_results = self.current_results.copy()
        self.best_cost = self.current_cost
        
        print(f"Costo inicial de la solución: {self.current_cost:.2f}, X_pos: {initial_results['x_pos']}, Flag: {initial_results['flag_get']}, Status: {initial_results['status']}")

        iteration = 0
        while not self.criterio_de_termino(iteration):
            print(f"\nIteración {iteration + 1}, Temperatura: {self.current_temperature:.2f}")

            # Generar una nueva solución vecina
            new_map_actions = self.make_next_actions()
            new_results = self.make_results(new_map_actions)
            new_cost = self.eval_actions(new_results)

            # Calcular la diferencia de costo
            delta_cost = new_cost - self.current_cost

            # Decidir si aceptar la nueva solución
            # Si la nueva solución es mejor, siempre la aceptamos
            if delta_cost < 0:
                print(f"  Mejora encontrada. Aceptando nueva solución (costo: {new_cost:.2f} < {self.current_cost:.2f}).")
                self.current_map_actions = list(new_map_actions)
                self.current_results = new_results.copy()
                self.current_cost = new_cost
            else:
                # Si la nueva solución es peor, la aceptamos con cierta probabilidad
                acceptance_probability = math.exp(-delta_cost / self.current_temperature)
                if random.random() < acceptance_probability:
                    print(f"  Peor solución aceptada (costo: {new_cost:.2f} > {self.current_cost:.2f}) con probabilidad: {acceptance_probability:.4f}.")
                    self.current_map_actions = list(new_map_actions)
                    self.current_results = new_results.copy()
                    self.current_cost = new_cost
                else:
                    print(f"  Peor solución rechazada (costo: {new_cost:.2f} > {self.current_cost:.2f}).")
            
            # Actualizar la mejor solución global encontrada hasta ahora
            self.update_best_map_action(self.current_map_actions, self.current_results, self.current_cost)

            # Almacenar en el histórico
            self.historic_map_actions.append(list(self.current_map_actions)) # Almacenar una copia
            self.historic_results.append(self.current_results.copy())
            self.historic_costs.append(self.current_cost)

            # Enfriar la temperatura
            self.current_temperature *= self.cooling_rate
            
            iteration += 1

        print("\nEntrenamiento con Recocido Simulado finalizado.")
        print(f"Mejor costo global encontrado: {self.best_cost:.2f}")
        print(f"Resultados de la mejor solución: {self.best_map_actions_results}")

        self.save_simulation_results()
