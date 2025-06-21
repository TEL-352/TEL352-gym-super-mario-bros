import os
import sys

import cloudpickle
from eval_setup import eval_parse_args
from nes_py.wrappers import JoypadSpace
import gym_super_mario_bros


from acciones import make_environment_actions
from pixel2cell import conversion_pixel_baldoza

def eval_function(date: str, render: bool):
    with open(f"outputs/{date}_simulation_results.pkl", "rb") as f:
        simulation_data = cloudpickle.loads(f.read())
        best_map_actions = simulation_data["best_actions"]
        print(simulation_data)
    
    env_actions = make_environment_actions()
    pixel2baldoza = conversion_pixel_baldoza
    results = run_simulation(render, best_map_actions, env_actions, pixel2baldoza)
    print(results)


def run_simulation(render, map_actions, env_actions, pixel2baldoza):
    """
    Función para ejecutar una simulación utilizando
    el mapeo de acciones generado por su agente
    No modificar, esta función solo tiene el objetivo de ejecutar
    las acciones generadas por su agente en el nivel 1 de Mario
    """
    env = gym_super_mario_bros.make('SuperMarioBros-v0')
    env = JoypadSpace(env, env_actions)

    done = True
    info = {
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

    results = {
        "info": info,
    }

    while True:
        if done:
            state = env.reset()

        n_lives = info["life"]
        action_idx = 0
        n_baldoza = pixel2baldoza(info["x_pos"], info["status"])
        try:
            action_idx = map_actions[n_baldoza]
        except Exception as e:
            print(f"Error, no hay acciones definidas para la baldoza {n_baldoza}")
            results["info"]["status"] = "error"
            break

        sim_results = ""
        with open("eval_function.pkl", "rb") as f:
            sim_results = cloudpickle.loads(f.read())["f"](*env.step(action_idx), n_lives)

        # print(sim_results)
        if sim_results == "dead":
            results["info"]["status"] = "dead"
            print("Oh no!, Mario ha perdido antes de llegar a la meta")
            break

        results["info"] = info

        if sim_results == "win":
            print("Muy Bien! Mario ha conseguido llegar a la meta y completar el nivel!")
            break

        if render:
            env.render()

        done = False

    env.close()

    return results["info"]



if __name__ == "__main__":
    args = eval_parse_args(sys.argv[1:])
    eval_function(args.date, args.render)
