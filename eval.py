import os
import sys

import cloudpickle
from eval_setup import eval_parse_args
from nes_py.wrappers import JoypadSpace
import gym_super_mario_bros

from acciones import make_environment_actions
from pixel2cell import conversion_pixel_baldoza

def eval_function(date: str, render: bool):
    if not os.path.exists("outputs"):
        print("Error: El directorio 'outputs' no existe. Ejecuta el entrenamiento primero (main.py).")
        return
        
    filepath = f"outputs/{date}_simulation_results.pkl"
    if not os.path.exists(filepath):
        print(f"Error: No se encontró el archivo de resultados en '{filepath}'.")
        return

    try:
        with open(filepath, "rb") as f:
            simulation_data = cloudpickle.load(f)
        best_map_actions = simulation_data["best_actions"]
        print("--- Cargando la mejor solución encontrada ---")

        training_time = simulation_data.get("total_training_time_seconds")
        if training_time is not None:
            minutes = int(training_time // 60)
            seconds = training_time % 60
            print(f"El entrenamiento de esta solución tardó: {minutes} minutos y {seconds:.2f} segundos.")
        
        print(f"Resultados de la mejor solución guardada: {simulation_data['best_results']}")

    except Exception as e:
        print(f"Error al cargar o leer el archivo pkl: {e}")
        return
    
    env_actions = make_environment_actions()
    pixel2baldoza = conversion_pixel_baldoza
    
    print("\n--- Ejecutando simulación de la mejor solución (mostrando acciones) ---")
    results = run_simulation(render, best_map_actions, env_actions, pixel2baldoza)
    print("\n--- Resultados finales de la simulación ---")
    print(results)


def run_simulation(render, map_actions, env_actions, pixel2baldoza):
    env = gym_super_mario_bros.make('SuperMarioBros-v0')
    env = JoypadSpace(env, env_actions)

    state = env.reset()
    info = env.unwrapped._get_info()

    last_x_pos = 0
    stuck_count = 0
    last_tile_printed = -1

    while True:
        n_baldoza = pixel2baldoza(info["x_pos"], info["status"])
        
        if n_baldoza != last_tile_printed:
            try:
                action_idx = map_actions[n_baldoza]
                action_name = env_actions[action_idx]
                print(f"Baldosa: {n_baldoza:3d} | Pos(X): {info['x_pos']:4d} | Acción: {action_name}")
                last_tile_printed = n_baldoza
            except IndexError:
                pass

        try:
            action_idx = map_actions[n_baldoza]
        except IndexError:
            info["status"] = "error"
            break

        state, reward, done, info = env.step(action_idx)
        
        if info["life"] < 2: 
            info["status"] = "dead"
            break

        if info["x_pos"] == last_x_pos:
            stuck_count += 1
            if stuck_count > 200: 
                info["status"] = "stuck"
                break
        else:
            stuck_count = 0
            last_x_pos = info["x_pos"]

        if info["flag_get"]:
            break
        
        if done:
            break

        if render:
            env.render()

    env.close()
    return info


if __name__ == "__main__":
    args = eval_parse_args(sys.argv[1:])
    if not args.date:
        print("Error: Debes especificar la fecha de la simulación a evaluar con el argumento --date.")
    else:
        eval_function(args.date, args.render)