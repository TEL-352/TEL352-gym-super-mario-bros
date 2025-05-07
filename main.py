from nes_py.wrappers import JoypadSpace
import gym_super_mario_bros

from agente import SuperMarioAgenteTEL

agente_tel = SuperMarioAgenteTEL()

env = gym_super_mario_bros.make('SuperMarioBros-v0')
env = JoypadSpace(env, agente_tel.get_actions())

done = True
for step in range(agente_tel.get_n_steps()):
    if done:
        state = env.reset()
    
    if step == 0:
        state, reward, done, info = env.step(0)

    else:
        state, reward, done, info = env.step(agente_tel.get_next_action(state, reward, info))

    if agente_tel.get_render():
        env.render()
    # break

env.close()
