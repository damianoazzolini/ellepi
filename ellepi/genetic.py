import random
import sys

from .variable_placer import Atom
from .prolog_interface import PrologInterface

class GeneticOptions:
    """
    Wrapper for all the options of the genetic algorithm.
    """
    def __init__(self) -> None:
        self.rules_to_generate : int = 10 # rules to generate for the available population
        self.max_initial_rule_length : int = 3
        self.population_size : int = 10
        self.mutation_probability : float = 0.05
        self.number_of_evolutionary_cycles : int = 1000
        self.initial_number_of_rules_per_individual : int = 6
        self.sampling_rules_method : str = "weighted" # or random
        self.verbosity : int = 0


class Rule:
    """
    A rule is represented by two list of lists, one for the head and one
    for the body.
    Each element of the two list has the same structure: a list (not tuple
    since tuples are immutable) containing the index of the head atom
    and the index for its instantiation.
    """
    def __init__(self,
            head_candidates : 'list[Atom]',
            body_candidates : 'list[Atom]',
            n_body_atoms : int
        ) -> None:
        self.head_candidates = head_candidates
        self.body_candidates = body_candidates
        self.head : 'list[int]' = []
        self.body : 'list[list[int]]' = []
        self.weight : float = 0
        
        # generate a random rule
        selected_atom = random.randint(0, len(head_candidates) - 1)
        selected_instantiation = random.randint(0, len(head_candidates[selected_atom].possible_instantiations) - 1)
        self.head = [selected_atom, selected_instantiation]

        for _ in range(n_body_atoms):
            selected_atom = random.randint(0, len(body_candidates) - 1)
            selected_instantiation = random.randint(0, len(body_candidates[selected_atom].possible_instantiations) - 1)
            self.body.append([selected_atom,selected_instantiation])
            
        self.body.sort(key=lambda x : x[0]) # keep them sorted, for fast comparison
    
    def _get_body_atoms(self) -> 'str':
        body_atoms : 'list[str]' = []
        for b in self.body:
            a = b[0]
            i = b[1]
            body_atom = self.body_candidates[a].possible_instantiations[i]
            body_atoms.append(body_atom)
        
        return ','.join(body_atoms)

    def _get_head_atom(self) -> 'str':
        a = self.head[0]
        i = self.head[1]
        head_atom = self.head_candidates[a].possible_instantiations[i]
        
        return head_atom

    def get_rule_as_str_with_weight(self) -> str:
        return f"{self._get_head_atom()} :- {self._get_body_atoms()} : {self.weight}"
    def __str__(self) -> str:
        return f"{self._get_head_atom()} :- {self._get_body_atoms()}"
    def __repr__(self) -> str:
        return self.__str__()
    def __eq__(self, other: object) -> bool:
        same_head = (self.head == other.head)
        same_body = (sorted(self.body) == sorted(other.body))
        return same_head and same_body
    def __gt__(self, other) -> bool:
        ha = (self.head[0] > other.head[0])
        hi = (self.head[1] > other.head[1])
        ba = False
        for a, b in zip(self.body,other.body):
            ba = ba and (a[0] > b[0])
        return ha or hi or ba

class Individual:
    """
    Individual for the genetic algorithm.
    An individual is represented by a set of rules.
    """
    def __init__(self,
            rules : 'list[Rule]'
        ) -> None:
        self.rules = rules
        self.score : float = 0
        self.compute_score()
    
    def compute_score(self):
        """
        Evaluates the score of the current individual.
        """
        # call LIFTCOVER to perform parameter learning on the current
        # program
        self.score = -1
    
    
    def __str__(self) -> str:
        s = "\n".join([str(r) for r in self.rules])
        return f"Individual with score: {self.score}\n" + s + "\n---\n"
    def __repr__(self) -> str:
        return self.__str__()
    def __eq__(self, other: object) -> bool:
        return sorted(self.rules) == sorted(other.rules)
    def __gt__(self, other) -> bool:
        return self.score > other.score


class GeneticAlgorithm:
    """
    Class defining the genetic algorithm.
    """
    def __init__(self,
            head_candidates : 'list[Atom]',
            body_candidates : 'list[Atom]',
            prolog_int : PrologInterface,
            options : GeneticOptions
        ) -> None:
        self.head_candidates = head_candidates
        self.body_candidates = body_candidates
        self.prolog_int = prolog_int
        self.options = options
        self.population : 'list[Individual]' = []
        
        self._init_population()
    
    
    def _init_population(self):
        """
        Initializes the population.
        """
        population : 'list[Individual]' = []
        available_rules : 'list[Rule]' = []
        max_attempts : int = 10_000
        
        # generate the available rules
        for _ in range(self.options.rules_to_generate):
            rl = random.randint(1, self.options.max_initial_rule_length) # random body length
            r = Rule(self.head_candidates, self.body_candidates, rl)
            available_rules.append(r)
        
        available_rules.sort()
        if self.options.sampling_rules_method == "weighted":
            # much faster than doing one by one
            ll_rules = self.prolog_int.compute_ll_rules([str(r) for r in available_rules])
            
            for ll, idx in zip(ll_rules,range(len(available_rules))):
                available_rules[idx].weight = ll
        
        if self.options.verbosity >= 2:
            print("Initial available rules")
            for r in available_rules:
                print(r.get_rule_as_str_with_weight())
                
            # print(*available_rules, sep="\n")
        
        attempts = 0
        while len(population) < self.options.population_size:
            # perform weighted sampling for individuals
            if self.options.sampling_rules_method == "weighted":
                weights = [-w.weight for w in available_rules] # - since LL is negative
                current_rules = random.choices(
                    population=available_rules,
                    weights=weights,
                    k=self.options.initial_number_of_rules_per_individual
                )
                new_individual = Individual(current_rules)
            else:
                new_individual = Individual(
                    random.sample(
                        available_rules,
                        self.options.initial_number_of_rules_per_individual
                    )
                )
            
            if new_individual not in population:
                new_individual.compute_score()
                population.append(new_individual)
            
            attempts += 1
            if attempts >= max_attempts:
                print("Exited sampling population loop due to exceeding number of attempts")
                print(f"max: {max_attempts}, length population: {len(population)}")
        
        # TODO: compute the score, something like this
        # ll_rules = self.prolog_int.compute_ll_rules([str(r) for r in available_rules])
        pop_as_list : 'list[list[str]]' = []
        for e in population:
            rules_p : 'list[str]' = []
            for r in e.rules:
                rules_p.append(str(r))
            pop_as_list.append(rules_p)

        ll_rules = self.prolog_int.compute_ll_programs(pop_as_list)
        
        print(ll_rules)
        
        for ll, idx in zip(ll_rules,range(len(population))):
            population[idx].score = ll
        
        # sort the population in terms of score
        population.sort(reverse=True)
        
        if self.options.verbosity >= 3:
            print(*population)
        
        sys.exit()

    
    def run_genetic_loop(self):
        """
        Runs the genetic loop.
        """
        
        for it in range(self.options.number_of_evolutionary_cycles):
            # select
            
            # mutate
            
            # evaluate
            
            # replace
            
            pass