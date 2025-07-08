import os
import random
import datetime
import time
from typing import List
from collections import deque

import cloudpickle

from acciones import make_environment_actions
from mario_gym import run_simulation
from pixel2cell import conversion_pixel_baldoza


class SuperMarioAgenteTEL:
    def __init__(self, args):
        self.args = args
        self.actions = self.make_environment_actions()
        self.num_actions = len(self.actions)
        self.num_tiles = self.args.n_tiles

        if self.args.load_from and os.path.exists(self.args.load_from):
            print(f"--- Cargando estado desde: {self.args.load_from} ---")
            with open(self.args.load_from, "rb") as f:
                simulation_data = cloudpickle.load(f)
            self.best_map_actions = simulation_data["best_actions"]
            self.best_map_actions_results = simulation_data["best_results"]
            self.current_map_actions = self.best_map_actions.copy()
            print("¡Estado cargado exitosamente! La búsqueda comenzará desde la mejor solución anterior.")
        else:
            if self.args.load_from:
                print(f"ADVERTENCIA: No se encontró el archivo {self.args.load_from}. Iniciando desde cero.")
            print("--- Iniciando desde una solución por defecto (correr a la derecha) ---")
            initial_action_index = 2
            self.current_map_actions = [initial_action_index] * self.num_tiles
            self.best_map_actions = self.current_map_actions.copy()
            self.best_map_actions_results = {
                "coins": 0, "flag_get": False, "life": 2, "score": 0, "stage": 1,
                "status": "dead", "time": 400, "world": 1, "x_pos": 40, "y_pos": 79
            }

        self.tabu_list = deque(maxlen=self.args.tabu_tenure)
        self.historic_map_actions = []
        self.historic_results = []
        self.iterations_without_improvement = 0

    def conversion_pixel_baldoza(self, n_pixel: int, mario_status: str) -> int:
        return conversion_pixel_baldoza(n_pixel, mario_status)

    def make_environment_actions(self) -> List[List[str]]:
        return make_environment_actions()

    def save_simulation_results(self, total_time=None):
        time_now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        backup_data = {
            "historic_actions": self.historic_map_actions,
            "historic_results": self.historic_results,
            "best_actions": self.best_map_actions,
            "best_results": self.best_map_actions_results,
        }
        if total_time is not None:
            backup_data["total_training_time_seconds"] = total_time

        outdir = "outputs/"
        os.makedirs(outdir, exist_ok=True)
        with open(f"{outdir}/{time_now}_simulation_results.pkl", mode="wb") as file:
            cloudpickle.dump(backup_data, file)

    def run_simulation(self, map_actions):
        return run_simulation(
            self.args, map_actions, self.make_environment_actions(), self.conversion_pixel_baldoza
        )

    def generate_neighbors(self, base_map_actions, last_results):
        last_x_pos = last_results.get('x_pos', 40)
        status = last_results.get('status', 'small')
        neighbors = []
        
        mario_tile_posicion = self.conversion_pixel_baldoza(last_x_pos, "small") + 5
        
        ventana_atras = 8
        ventana_adelante = 8
        
        baldosa_inicio_ventana = max(0, mario_tile_posicion - ventana_atras)
        baldosa_fin_ventana = min(self.num_tiles - 1, mario_tile_posicion + ventana_adelante)
        
        if baldosa_inicio_ventana > baldosa_fin_ventana:
            baldosa_inicio_ventana = 0
            baldosa_fin_ventana = min(self.num_tiles - 1, ventana_adelante * 2)
        
        jump_action_index = 4

        for _ in range(self.args.n_neighbors):
            neighbor = base_map_actions.copy()
            
            is_dead_by_fall = status == 'dead' and last_results.get('time', 400) > 0

            if is_dead_by_fall and random.random() < 0.5: 
                tile_to_change = random.randint(max(0, mario_tile_posicion - 8), max(0, mario_tile_posicion - 1))
                new_action = jump_action_index
                print(f"DEBUG: Mario muerto en x={last_x_pos} (baldosa ~{mario_tile_posicion}). Forzando salto en ventana anterior ({tile_to_change}).")

            else:
                tile_to_change = random.randint(baldosa_inicio_ventana, baldosa_fin_ventana)
                new_action = random.randint(0, self.num_actions - 1)

            current_action = neighbor[tile_to_change]
            if new_action == current_action:
                new_action = (new_action + 1) % self.num_actions
                
            neighbor[tile_to_change] = new_action
            move = (tile_to_change, new_action)
            neighbors.append((neighbor, move))
            
        return neighbors

    def make_results(self, map_actions):
        return self.run_simulation(map_actions)

    def eval_actions(self, results):
        score = results["x_pos"] * 2
        score += results["score"] * 1.5
        
        if results["status"] == 'big': score += 200
        if results["flag_get"]: score += 5000 + results["time"]
        if results["status"] == "dead" : score -= 200
        if results["status"] == "error": return -1
        return score

    def update_best_map_action(self, map_actions, results) -> bool:
        current_best_score = self.eval_actions(self.best_map_actions_results)
        new_score = self.eval_actions(results)
        
        if new_score > current_best_score:
            print(f"** Nueva mejor solución encontrada! Score: {new_score:.1f}, Pos: {results['x_pos']}, Status: {results['status']} **")
            self.best_map_actions = map_actions.copy()
            self.best_map_actions_results = results
            self.iterations_without_improvement = 0
            return True
        else:
            self.iterations_without_improvement += 1
            return False

    def criterio_de_termino(self):
        if self.best_map_actions_results["flag_get"]:
            print("¡Criterio de término alcanzado: Se ha llegado a la bandera!")
            return True
        return False

    def train(self):
        print("--- Iniciando Búsqueda Tabú ---")
        start_time = time.time()
        
        if self.args.load_from and os.path.exists(self.args.load_from):
            current_results = self.best_map_actions_results
        else:
            current_results = self.make_results(self.current_map_actions)
            self.update_best_map_action(self.current_map_actions, current_results)
        
        if self.criterio_de_termino():
            print("La mejor solución cargada ya completa el nivel. No se necesita más entrenamiento.")
            self.save_simulation_results()
            return

        for i in range(self.args.n_training_steps):
            print(f"\n--- Iteración {i+1}/{self.args.n_training_steps} (Estancado por: {self.iterations_without_improvement} iter.) ---")
            
            if self.iterations_without_improvement > 5:
                print("¡Estancamiento detectado! Aplicando perturbación a la solución actual...")
                
                # Obtenemos la última posición conocida de Mario como referencia
                last_x_pos = current_results.get('x_pos', 40)
                mario_tile_posicion = self.conversion_pixel_baldoza(last_x_pos, "small")

                # ==================== INICIO DE LA LÓGICA MEJORADA ====================
                # Definimos una ventana de perturbación más amplia alrededor de Mario.
                # Por ejemplo, 15 baldosas hacia atrás y 15 hacia adelante.
                # Esto es más grande que la ventana de generación de vecinos para ser una "sacudida" real.
                ventana_perturbacion = 15
                
                inicio_perturbacion = max(0, mario_tile_posicion - ventana_perturbacion)
                fin_perturbacion = min(self.num_tiles - 1, mario_tile_posicion + ventana_perturbacion)

                # Nos aseguramos de que el rango sea válido
                if inicio_perturbacion > fin_perturbacion:
                    fin_perturbacion = inicio_perturbacion + 1
                    
                print(f"DEBUG: Perturbando 5 acciones aleatorias en la ventana de baldosas [{inicio_perturbacion}-{fin_perturbacion}]")

                for _ in range(5): # Hacemos 5 cambios aleatorios
                    tile_to_change = random.randint(inicio_perturbacion, fin_perturbacion)
                    
                    # Para asegurar una perturbación real, asignamos una acción diferente a la actual
                    new_action = random.randint(0, self.num_actions - 1)
                    if self.current_map_actions[tile_to_change] == new_action:
                        new_action = (new_action + 1) % self.num_actions

                    self.current_map_actions[tile_to_change] = new_action
                # ===================== FIN DE LA LÓGICA MEJORADA ======================
                
                self.iterations_without_improvement = 0
                
                # Re-evaluamos la nueva solución perturbada para tener un punto de partida actualizado
                current_results = self.make_results(self.current_map_actions)

            neighbors = self.generate_neighbors(self.current_map_actions, current_results)
            
            best_neighbor_solution = None
            best_neighbor_move = None
            best_neighbor_results = None
            best_neighbor_score = -float('inf')
            global_best_score = self.eval_actions(self.best_map_actions_results)

            print(f"  Lista Tabú actual: {list(self.tabu_list)}")
            print("  Evaluando Vecindario:")
            
            for neighbor_solution, move in neighbors:
                results = self.make_results(neighbor_solution)
                score = self.eval_actions(results)
                is_tabu = move in self.tabu_list
                aspiration_met = is_tabu and score > global_best_score
                
                tabu_status_str = " (Tabú)" if is_tabu and not aspiration_met else ""
                print(f"    - Vecino (Movimiento: {move}): Score={score:.1f}{tabu_status_str}")

                if (not is_tabu and score > best_neighbor_score) or aspiration_met:
                    if aspiration_met: print(f"      -> Criterio de aspiración cumplido para movimiento tabú {move}!")
                    best_neighbor_score = score
                    best_neighbor_solution = neighbor_solution
                    best_neighbor_move = move
                    best_neighbor_results = results

            if best_neighbor_solution is None:
                print("No se encontró un vecino válido. Reiniciando lista tabú para escapar.")
                self.tabu_list.clear()
                continue

            self.current_map_actions = best_neighbor_solution
            current_results = best_neighbor_results
            
            if best_neighbor_move in self.tabu_list: self.tabu_list.remove(best_neighbor_move)
            self.tabu_list.append(best_neighbor_move)

            updated = self.update_best_map_action(self.current_map_actions, current_results)
            
            if updated and self.args.render_progress:
                print("--> Mostrando la nueva mejor solución encontrada...")
                original_render_state, self.args.render = self.args.render, True
                self.run_simulation(self.best_map_actions)
                self.args.render = original_render_state

            self.historic_map_actions.append(self.current_map_actions)
            self.historic_results.append(current_results)
            
            print(f"Mejor vecino elegido: Score={best_neighbor_score:.1f}, Pos={best_neighbor_results['x_pos']}. Mejor global: {global_best_score:.1f}")
            print(f"Movimiento realizado: {best_neighbor_move}. Tamaño lista tabú: {len(self.tabu_list)}")
            porcentaje = (current_results["x_pos"] / 3266) * 100
            print(f"  Porcentaje completado: {porcentaje:.2f}%")


            if self.criterio_de_termino(): break
        
        print("\n--- Entrenamiento Finalizado ---")
        end_time = time.time()
        total_execution_time = end_time - start_time
        print(f"Tiempo total de entrenamiento: {total_execution_time:.2f} segundos.")
        self.save_simulation_results(total_execution_time)