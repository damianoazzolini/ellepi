import argparse

def parse_args():
    """
    Arguments parser.
    """
    command_parser = argparse.ArgumentParser(
        description="ELLEPI: EvoLutionary LEarning of ProbabIlistic logic programs",
        # epilog="Example: ",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    command_parser.add_argument(
        "-f",
        "--filename",
        help="Program to analyse",
        type=str,
        required=True
    )
    command_parser.add_argument(
        "-v",
        "--verbosity",
        help="Verbosity level.",
        type=int,
        default=0
    )
    command_parser.add_argument(
        "--train",
        nargs="+",
        help="Folds for the training set",
        required=True
    )
    command_parser.add_argument(
        "--test",
        nargs="+",
        help="Folds for the test set"
    )

    command_parser.add_argument(
        "--seed",
        help="Seed for the random generator",
        default=42
    )

    return command_parser.parse_args()
