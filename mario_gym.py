from nes_py.wrappers import JoypadSpace
import gym_super_mario_bros
import pdb


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
            "status": "dead",
            "time": 400,
            "world": 1,
            "x_pos": 1,
            "y_pos": 79
        }

        results = {
            "info": info,
        }

        x_pos = 0
        count = 0

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
            #print(info)
            
            if info["life"] < n_lives:
                results["info"]["status"] = "dead"
                break
            
            if info["x_pos"] == x_pos:
                if count >= 100:
                    results["info"]["status"] = "dead end"
                    break
                else:
                    count += 1
            else:
                count = 0
                x_pos = info["x_pos"]
            results["info"] = info

            if done or info["flag_get"]:
                break
            
            if args.render:
                env.render()


        env.close()

        return results["info"]