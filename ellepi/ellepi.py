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
        # to remove everything after -/+
        cleaned_arguments = [a[0] for a in atom[1:]]
        at = Atom(atom[0], cleaned_arguments, args.nvars)
        atoms_head.append(at)
    
    for atom in modeb:
        cleaned_arguments = [a[0] for a in atom[1:]]
        at = Atom(atom[0], cleaned_arguments, args.nvars)
        atoms_body.append(at)
        
    print(atoms_head)
    print(atoms_body)
    
    # setup the genetic options
    genetic_options = GeneticOptions(args)
    # genetic_options.verbosity = args.verbosity
    
    genetic_alg = GeneticAlgorithm(atoms_head, atoms_body, prolog_int, genetic_options)
    
    best_individual = genetic_alg.run_genetic_loop()

    ir = best_individual.get_individual_as_input_program()
    
    print("--- Best individual ---")
    print(best_individual)
    print(ir)
    
    ll_ind_train_and_probs = prolog_int.compute_ll_rules([ir], args.train)
    print(f"LL on training: {ll_ind_train_and_probs}")
    # ll_ind_test = prolog_int.compute_ll_rules([ir], "test")
    # print(f"LL on test: {ll_ind_test}")
    print("Testng results")
    program, ll_test, aucroc, aucpr = prolog_int.compute_test_results(ir, args.train, args.test)
    print(program)
    print(f"LL test: {ll_test}")
    print(f"AUCROC: {aucroc}")
    print(f"AUCPR: {aucpr}")
    
    
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