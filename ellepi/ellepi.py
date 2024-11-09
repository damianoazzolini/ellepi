import random

from .argparser import parse_args

def main():
    """
    Main method.
    """
    args = parse_args()
    print(args)
    
    random.seed(args.seed)
    

if __name__ == "__main__":
    main()