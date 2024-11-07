from .argparser import parse_args

def main():
    """
    Main method.
    """
    args = parse_args()
    print(args)
    

if __name__ == "__main__":
    main()