# Archivo: agente.py
import os
import random
import numpy as np
import cloudpickle
import datetime
from typing import List, Tuple

from acciones import make_environment_actions
from mario_gym import run_simulation
from pixel2cell import conversion_pixel_baldoza


class SuperMarioAgenteTEL:
    # Clase interna para representar a un individuo de la población
    class Individuo:
        def __init__(self, acciones, tasas_mutacion):
            self.acciones = acciones  # Vector de solución (los genes)
            self.tasas_mutacion = tasas_mutacion  # Vector de parámetros de estrategia
            self.fitness = -float('inf')  # Aptitud, se inicia en un valor muy bajo
            self.results = {}  # Resultados de la simulación, se llenará al evaluar

        def __repr__(self):
            return f"Individuo(fitness={self.fitness:.2f})"

    def __init__(self, args):
        # --- Atributos del Proyecto Base ---
        self.args = args
        self.actions = self.make_environment_actions()
        self.best_map_actions = []  # Mejor solución encontrada
        self.best_map_actions_results = {} # Resultados de la mejor solución
        self.best_fitness = -float('inf') # Fitness de la mejor solución

        # Históricos para guardar datos
        self.historic_map_actions = []
        self.historic_results = []
        self.historic_fitness = [] # Para la curva de mejora

        # --- Atributos de Estrategias Evolutivas ---
        self.poblacion = [] # Lista de objetos de la clase Individuo

    # --- Funciones Wrapper (No Modificar) ---
    def conversion_pixel_baldoza(self, n_pixel: int, mario_status: str) -> int:
        return conversion_pixel_baldoza(n_pixel, mario_status)

    def make_environment_actions(self) -> List[List[str]]:
        return make_environment_actions()

    def run_simulation(self, map_actions):
        return run_simulation(
            self.args, map_actions, self.make_environment_actions(), self.conversion_pixel_baldoza
        )

    def make_results(self, map_actions):
        return self.run_simulation(map_actions)

    # --- Implementación de Estrategias Evolutivas ---

    def eval_actions(self, results: dict) -> float:
        """
        Función de fitness. Evalúa y retorna un puntaje numérico para una solución.
        Mientras más alto el puntaje, mejor es la solución.
        """
        # Componente 1: Avance en el nivel (el más importante)
        fitness_avance = results.get("x_pos", 0)

        # Componente 2: Penalización fuerte si Mario muere
        penalizacion_muerte = 0
        if results.get("status") == "dead":
            # Penalización grande, pero se reduce un poco si avanzó más
            # para diferenciar entre morir al principio y morir más adelante.
            penalizacion_muerte = -5000 + fitness_avance

        # Componente 3: Bonificación masiva por completar el nivel
        bonificacion_meta = 500000 if results.get("flag_get", False) else 0

        # Componente 4: Bonificación por tiempo (desempate si llega a la meta)
        bonificacion_tiempo = 0
        if bonificacion_meta > 0:
            bonificacion_tiempo = results.get("time", 0) * 0.1

        # Componente 5: Bonificación pequeña por monedas (desempate menor)
        bonificacion_monedas = results.get("coins", 0)
        
        # --- NUEVA LÓGICA: PENALIZACIÓN POR ESTANCAMIENTO ---
        penalizacion_estancamiento = 0
        # Si el tiempo casi se agota (ej. quedan menos de 10 ticks) Y no se llegó a la meta,
        # es un claro indicador de que Mario se quedó atascado.
        if results.get("time", 400) == 0 and not results.get("flag_get", False):
            # Aplicamos una penalización severa, pero que sigue valorando el avance.
            # Así, quedarse atascado en la baldosa 2500 es malo,
            # pero mejor que morir en la baldosa 300.
            penalizacion_estancamiento = -2000 + fitness_avance
        # --- FIN DE LA NUEVA LÓGICA ---

        fitness_total = (
            fitness_avance
            + penalizacion_muerte
            + bonificacion_meta
            + bonificacion_tiempo
            + bonificacion_monedas
            + penalizacion_estancamiento
        )
        return float(fitness_total)

    def update_best_map_action(self, individuo: Individuo, results: dict):
        """
        Actualiza la mejor solución global si el individuo actual es mejor.
        """
        if individuo.fitness > self.best_fitness:
            print(f"¡Nueva mejor solución encontrada! Fitness: {individuo.fitness:.2f} (Anterior: {self.best_fitness:.2f})")
            self.best_fitness = individuo.fitness
            self.best_map_actions = individuo.acciones
            self.best_map_actions_results = results

    def _inicializar_poblacion(self):
        """
        Crea la población inicial de `mu` individuos con soluciones aleatorias.
        """
        self.poblacion = []
        num_acciones_posibles = len(self.actions)
        for _ in range(self.args.mu):
            # Acciones aleatorias (índices de la lista self.actions)
            acciones = [random.randint(0, num_acciones_posibles - 1) for _ in range(self.args.longitud_genoma)]
            # Tasas de mutación iniciales (bajas y uniformes)
            tasas_mutacion = [0.05] * self.args.longitud_genoma
            self.poblacion.append(self.Individuo(acciones, tasas_mutacion))

    def _recombinacion(self, padre1: Individuo, padre2: Individuo) -> Tuple[List[int], List[float]]:
        """
        Crea un nuevo genoma (acciones y tasas) a partir de dos padres.
        """
        # Recombinación discreta para las acciones (genes)
        x_hijo = [
            random.choice([p1, p2]) for p1, p2 in zip(padre1.acciones, padre2.acciones)
        ]
        # Recombinación intermedia para las tasas de mutación (parámetros de estrategia)
        p_hijo = [
            (p1 + p2) / 2.0 for p1, p2 in zip(padre1.tasas_mutacion, padre2.tasas_mutacion)
        ]
        return x_hijo, p_hijo

    def _mutacion(self, acciones: List[int], tasas: List[float]) -> Tuple[List[int], List[float]]:
        """
        Aplica mutación a un genoma (autoadaptación).
        """
        # 1. Mutar las tasas de mutación
        tau = self.args.tasa_aprendizaje_mutacion
        tasas_mutadas = [
            t * np.exp(tau * np.random.normal(0, 1)) for t in tasas
        ]
        # Nos aseguramos que las tasas no se salgan de un rango razonable
        tasas_mutadas = [max(0.01, min(0.5, t)) for t in tasas_mutadas]

        # 2. Mutar las acciones basadas en las nuevas tasas
        acciones_mutadas = list(acciones)
        num_acciones_posibles = len(self.actions)
        for i in range(len(acciones_mutadas)):
            if random.random() < tasas_mutadas[i]:
                # Reemplazar por una acción aleatoria DIFERENTE a la actual
                accion_actual = acciones_mutadas[i]
                nueva_accion = random.randint(0, num_acciones_posibles - 1)
                while nueva_accion == accion_actual:
                    nueva_accion = random.randint(0, num_acciones_posibles - 1)
                acciones_mutadas[i] = nueva_accion

        return acciones_mutadas, tasas_mutadas
    
    # --- NUEVA FUNCIÓN DE MUTACIÓN DIRIGIDA ---
    def _mutacion_dirigida(self, individuo_base: Individuo, baldosa_muerte: int) -> Individuo:
        """
        Crea un nuevo individuo mutando las acciones del individuo base
        alrededor de la baldosa donde murió.
        """
        acciones_mutadas = list(individuo_base.acciones)
        num_acciones_posibles = len(self.actions)
        
        # Definimos la ventana de mutación: 5 baldosas antes y 5 después
        inicio_ventana = max(0, baldosa_muerte - 5)
        fin_ventana = min(len(acciones_mutadas), baldosa_muerte + 6) # +6 para incluir la baldosa 5 después
        
        print(f"Aplicando mutación dirigida en ventana: [{inicio_ventana}-{fin_ventana-1}]")

        for i in range(inicio_ventana, fin_ventana):
            # Reemplazamos la acción por una nueva acción aleatoria
            accion_actual = acciones_mutadas[i]
            nueva_accion = random.randint(0, num_acciones_posibles - 1)
            # Opcional: nos aseguramos que la nueva acción sea diferente
            while nueva_accion == accion_actual:
                nueva_accion = random.randint(0, num_acciones_posibles - 1)
            acciones_mutadas[i] = nueva_accion
            
        tasas_por_defecto = [0.05] * len(acciones_mutadas)
        return self.Individuo(acciones_mutadas, tasas_por_defecto)
    
    def criterio_de_termino(self):
        print(self.best_map_actions_results["flag_get"])
        if self.best_map_actions_results["flag_get"] == True:
            print("stop")
            return True
        else:
            return False

    def train(self):
        """
        Ciclo de entrenamiento principal de la Estrategia Evolutiva (μ, λ).
        """
        print("--- Iniciando entrenamiento con Estrategias Evolutivas ---")
        self._inicializar_poblacion()
        
        modo_mutacion = "estandar"

        # Bucle principal (por cada generación)
        for g in range(self.args.n_training_steps):
            print(f"\n--- Generación {g + 1}/{self.args.n_training_steps} ---")
            
            individuo_base = self.poblacion[0]
            
            # Simulamos al mejor individuo para saber su resultado final
            resultados_base = self.make_results(individuo_base.acciones)
            individuo_base.fitness = self.eval_actions(resultados_base) # Actualizamos su fitness por si acaso
            individuo_base.results = resultados_base
            
            # Decidimos qué estrategia usar para la siguiente generación
            if resultados_base.get("status") == "dead":
                print(f"Mejor agente murió en x_pos={resultados_base.get('x_pos')}. Usando MUTACIÓN DIRIGIDA.")
                modo_mutacion = "dirigida"
            else:
                print(f"Mejor agente no murió (status={resultados_base.get('status')}). Usando ES ESTÁNDAR.")
                modo_mutacion = "estandar"
            
            # Generar λ hijos
            poblacion_hijos = []
            if modo_mutacion == "dirigida":
                # Obtenemos la baldosa donde ocurrió la muerte
                baldosa_muerte = self.conversion_pixel_baldoza(
                    resultados_base.get("x_pos"), resultados_base.get("status")
                )
                # Generamos todos los hijos a partir del individuo que murió
                for _ in range(self.args.lambda_):
                    hijo = self._mutacion_dirigida(individuo_base, baldosa_muerte)
                    poblacion_hijos.append(hijo)
            else: # modo_mutacion == "estandar"
                for _ in range(self.args.lambda_):
                    padre1, padre2 = random.sample(self.poblacion, 2)
                    x_hijo, p_hijo = self._recombinacion(padre1, padre2)
                    x_mutado, p_mutado = self._mutacion(x_hijo, p_hijo)
                    poblacion_hijos.append(self.Individuo(x_mutado, p_mutado))

            # Evaluar a los λ hijos
            print(f"Evaluando {len(poblacion_hijos)} descendientes...")
            for hijo in poblacion_hijos:
                results = self.make_results(hijo.acciones)
                hijo.fitness = self.eval_actions(results)
                hijo.results = results  # Guardamos los resultados de la simulación
                self.update_best_map_action(hijo, results)
            
            poblacion_combinada = self.poblacion + poblacion_hijos
            poblacion_combinada.sort(key=lambda ind: ind.fitness, reverse=True)
            self.poblacion = poblacion_combinada[:self.args.mu]
            
            # --- Recolección de Datos Históricos ---
            mejor_individuo_gen = self.poblacion[0]
            best_fitness_gen = self.poblacion[0].fitness
            avg_fitness_gen = sum(ind.fitness for ind in self.poblacion) / len(self.poblacion)
            best_x_pos_gen = mejor_individuo_gen.results.get('x_pos', 0)
            
            print(f"Mejor Fitness de la Generación: {best_fitness_gen:.2f}")
            print(f"Fitness Promedio de la Generación: {avg_fitness_gen:.2f}")
            print(f"Mejor Avance (x_pos) de la Generación: {best_x_pos_gen}")
    
            self.historic_fitness.append({
                "generacion": g + 1,
                "best_fitness": best_fitness_gen,
                "avg_fitness": avg_fitness_gen,
                "best_x_pos": best_x_pos_gen
            })
            self.historic_map_actions.append(self.poblacion[0].acciones)
            # Para el histórico de resultados, volvemos a simular el mejor para tener datos consistentes
            self.historic_results.append(self.make_results(self.poblacion[0].acciones))

            if self.criterio_de_termino():
                break
            
        print("\n--- Entrenamiento Finalizado ---")
        self.save_simulation_results()

    def save_simulation_results(self):
        """
        Guarda los resultados de la simulación.
        """
        time_now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        backup_data = {
            "historic_actions": self.historic_map_actions,
            "historic_results": self.historic_results,
            "historic_fitness": self.historic_fitness, # Guardamos la curva de mejora
            "best_actions": self.best_map_actions,
            "best_results": self.best_map_actions_results,
            "args": self.args # Guardamos los hiperparámetros usados
        }
        backup_file_name = f"{time_now}_simulation_results.pkl"
        outdir = "outputs/"
        os.makedirs(outdir, exist_ok=True)
        with open(f"{outdir}/{backup_file_name}", mode="wb") as file:
            cloudpickle.dump(backup_data, file)
        print(f"Resultados guardados en: {outdir}{backup_file_name}")