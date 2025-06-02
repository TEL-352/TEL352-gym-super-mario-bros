import sys
import random

import numpy as np

from agente import SuperMarioAgenteTEL
from setup import main_parse_args

random.seed(10)
np.random.seed(0)


def main(args):
    agente_tel = SuperMarioAgenteTEL(args)
    agente_tel.train()
    
    return

if __name__ == "__main__":
    args = main_parse_args(sys.argv[1:])
    main(args)