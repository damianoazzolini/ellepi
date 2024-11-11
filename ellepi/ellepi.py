import random

from .argparser import parse_args
from .genetic import GeneticOptions, GeneticAlgorithm
from .prolog_interface import PrologInterface
from .variable_placer import Atom

def main():
    """
    Main method.
    """
    args = parse_args()
    print(args)
    
    random.seed(args.seed)
    
    prolog_int = PrologInterface(args.filename, args.verbosity)
    
    # get modes to generate placements
    modeh, modeb = prolog_int.get_modes()
    
    atoms_head : 'list[Atom]' = []
    atoms_body : 'list[Atom]' = []
    
    for atom in modeh:
        at = Atom(atom[0], atom[1:], args.nvars)
        atoms_head.append(at)

    for atom in modeb:
        at = Atom(atom[0], atom[1:], args.nvars)
        atoms_body.append(at)
        
    print(atoms_head)
    print(atoms_body)
    
    # setup the genetic options
    genetic_options = GeneticOptions()
    genetic_options.verbosity = args.verbosity
    
    genetic_alg = GeneticAlgorithm(atoms_head, atoms_body, genetic_options)
    
    
    # get the modes from the file to generate atoms
    
    
# a program is list of clauses. Each clause has a head and a list of body atoms
# each atom (either head or body) is a list containing the index of the considered
# atom and the index of the considered possible instantiation of varaibles
# for it
# example
# possible atoms: [a with arity 1, b with arity 1]: a has index 0 and b has index 1
# two variables allowed
# possible instantiations [a(A0),a(A1),a(_)] and [b(A0),b(A1),b(_)]
# rule: a(A0) :- b(_) is
# head: [0][0]
# body: [1][2]
# it can also be a dict, but i need to distinguish atoms with the same signature but
# different possible modes
    

if __name__ == "__main__":
    main()