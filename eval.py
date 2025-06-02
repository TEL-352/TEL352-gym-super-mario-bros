import sys

import cloudpickle
from eval_setup import eval_parse_args


def main(args):
    with open("eval_function.pkl", "rb") as f:
        eval_function = cloudpickle.loads(f.read())["f"]
        eval_function(args.date, args.render)


if __name__ == "__main__":
    args = eval_parse_args(sys.argv[1:])
    main(args)