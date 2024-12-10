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
        "--backend",
        help="Backend for parameter learning",
        choices=["SLIPCOVER", "LIFTCOVER"],
        default="SLIPCOVER"
    )

    command_parser.add_argument(
        "--seed",
        help="Seed for the random generator",
        default=42
    )
    command_parser.add_argument(
        "--train",
        help="Ids for the training set",
        nargs="+",
        default=["train"]
    )
    command_parser.add_argument(
        "--test",
        help="Ids for the training set",
        nargs="+",
        default=["test"]
    )

    # arguments for the genetic algorithm
    command_parser.add_argument(
        "-nv",
        "--nvars",
        help="Number of variables to consider in clauses.",
        type=int,
        default=2
    )
    command_parser.add_argument(
        "-p",
        "--popsize",
        help="Population size.",
        type=int,
        default=50
    )
    command_parser.add_argument(
        "-ec",
        "--evolutionary-cycles",
        help="Number of evolutionary cycles.",
        type=int,
        default=100
    )
    command_parser.add_argument(
        "-rpi",
        help="Initial number of rules per individual.",
        type=int,
        default=6
    )
    command_parser.add_argument(
        "-rtg",
        help="Initial number of rules to generate for population initialization.",
        type=int,
        default=50
    )
    command_parser.add_argument(
        "-par",
        help="Mutation: probability to add a rule.",
        type=float,
        default=0.2
    )
    command_parser.add_argument(
        "-pdr",
        help="Mutation: probability to drop each rule.",
        type=float,
        default=0.05
    )
    command_parser.add_argument(
        "-pm",
        help="Mutation: probability to modify a rule.",
        type=float,
        default=0.25
    )
    command_parser.add_argument(
        "-pcatom",
        help="Mutation: probability to change an atom of a rule.",
        type=float,
        default=0.33
    )
    command_parser.add_argument(
        "-pcinst",
        help="Mutation: probability to change the instantiation of an atom of a rule.",
        type=float,
        default=0.33
    )
    command_parser.add_argument(
        "-ctype",
        help="Crossover type.",
        type=str,
        default="random",
        choices=["random","tournament","fittest","rank"]
    )
    command_parser.add_argument(
        "-psf",
        help="Crossover: probability to select the fittest for the tournament.",
        type=float,
        default=0.8
    )
    command_parser.add_argument(
        "-age",
        help="Probability to drop the oldest element.",
        type=float,
        default=-1.0
    )
    command_parser.add_argument(
        "-r",
        help="Regularization.",
        type=float,
        default=0
    )
    
    return command_parser.parse_args()
