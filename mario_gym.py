from nes_py.wrappers import JoypadSpace
import gym_super_mario_bros

from agente import SuperMarioAgenteTEL


def run_simulation(args, map_actions, env_actions, pixel2baldoza):
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
            "status": "small",
            "time": 400,
            "world": 1,
            "x_pos": 40,
            "y_pos": 79
        }

        results = {
            "info": info,
        }

        for step in range(args.n_frames):
            if done:
                state = env.reset()

            n_lives = info["life"]
            action_idx = 0
            n_baldoza = pixel2baldoza(info["x_pos"], info["status"])
            try:
                action_idx = map_actions[n_baldoza]
            except Exception as e:
                results["info"]["status"] = "error"
                break

            state, reward, done, info = env.step(action_idx)

            if info["life"] < n_lives:
                results["info"]["status"] = "dead"
                break

            results["info"] = info

            if done or info["flag_get"]:
                break

            if args.render:
                env.render()


        env.close()

        return results["info"]