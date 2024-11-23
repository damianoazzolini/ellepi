import copy
import numpy as np # for argmax
import random
import sys
import time


from argparse import Namespace

from .variable_placer import Atom
from .prolog_interface import PrologInterface

class GeneticOptions:
    """
    Wrapper for all the options of the genetic algorithm.
    """
    def __init__(self, args : Namespace) -> None:
        self.train_set : 'list[str]' = args.train
        self.population_size : int = args.popsize
        self.number_of_evolutionary_cycles : int = args.evolutionary_cycles
        self.initial_number_of_rules_per_individual : int = args.rpi
        self.rules_to_generate : int = args.rtg # rules to generate for the available population
        self.allow_atoms_mutliple_times : bool = False # allow the use of the same atom multiple times in the generation of rules
        # for mutation
        self.prob_add_rule : float = args.par
        self.prob_drop_rule : float = args.pdr
        self.prob_modify : float = args.pm
        self.prob_change_atom : float = args.pcatom
        self.prob_change_instantiation : float = args.pcinst
        # for crossover
        self.crossover_type : str = args.ctype
        self.prob_select_fittest_tournament : float = args.psf
        # for dropping elements
        self.age_regularized_prob : float = args.age
        
        self.tournament_percentage : int = 20
        self.verbosity : int = args.verbosity
        self.max_initial_rule_length : int = 3
        self.sampling_rules_method : str = "weighted" # or random
        self.iterations_print_step : int = 10


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
        
        allow_atoms_twice : bool = False
        
        # generate a random rule
        selected_atom = random.randint(0, len(head_candidates) - 1)
        selected_instantiation = random.randint(0, len(head_candidates[selected_atom].possible_instantiations) - 1)
        self.head = [selected_atom, selected_instantiation]

        if allow_atoms_twice:
            selected_atoms = [random.randint(0, len(body_candidates) - 1) for i in range(n_body_atoms)]
        else:
            selected_atoms = random.sample(list(range(0,len(body_candidates) - 1)), n_body_atoms)
        for sa in selected_atoms:
            selected_instantiation = random.randint(0, len(body_candidates[sa].possible_instantiations) - 1)
            self.body.append([sa,selected_instantiation])
        # for _ in range(n_body_atoms):
        #     selected_atom = random.randint(0, len(body_candidates) - 1)
        #     selected_instantiation = random.randint(0, len(body_candidates[selected_atom].possible_instantiations) - 1)
        #     self.body.append([selected_atom,selected_instantiation])
            
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

    def get_rule_as_input_program(self) -> str:
        """
        Returns a rule as an input program for SLIPCOVER.
        """
        r = str(self).split(":-") # to add the probability
        r = r[0] + ":0.5 :- " + r[1]
        return f"in([({r})])."
    
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
        self.birth_time : float = time.time()
        # self.compute_score()
    
    # def compute_score(self):
    #     """
    #     Evaluates the score of the current individual.
    #     """
    #     # call LIFTCOVER to perform parameter learning on the current
    #     # program
    #     self.score = -1
    
    def get_individual_as_input_program(self) -> str:
        """
        Returns an individual as an input program for SLIPCOVER.
        """
        current_in = "in(["
        for rule in self.rules:
            r = str(rule).split(":-") # to add the probability
            r = r[0] + ":0.5 :- " + r[1]
            current_in += f"({r}),"
        current_in = current_in[:-1]
        current_in += "])."
        return current_in

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
            rr = [r.get_rule_as_input_program() for r in available_rules]
            ll_rules = self.prolog_int.compute_ll_rules(rr, self.options.train_set)
            
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
                current_rules.sort()
                new_individual = Individual(current_rules)
            else:
                new_individual = Individual(
                    random.sample(
                        available_rules,
                        self.options.initial_number_of_rules_per_individual
                    )
                )
            
            if new_individual not in population:
                # new_individual.compute_score()
                population.append(new_individual)
            
            attempts += 1
            if attempts >= max_attempts:
                print("Exited sampling population loop due to exceeding number of attempts")
                print(f"max: {max_attempts}, length population: {len(population)}")
        
        # computation of the LL of the individuals

        l = [ir.get_individual_as_input_program() for ir in population]
        ll_rules = self.prolog_int.compute_ll_rules(l, self.options.train_set)
       
        for ll, idx in zip(ll_rules,range(len(population))):
            population[idx].score = ll
        
        # sort the population in terms of score
        population.sort(reverse=True)
        self.population = population
        
        if self.options.verbosity >= 2:
            for i in self.population:
                print(i)
                print(i.get_individual_as_input_program())
                
            print(*self.population)
    
    def _select_individuals(self) -> 'tuple[Individual,Individual]':
        """
        Selections of the individuals.
        """
        # def get_from_tournament():
        #     prob_selecting_fittest = 0.9
        #     how_many = min(2, int(len(self.population)*self.options.tournament_percentage/100))
        #     random_subset = random.sample(self.population, how_many)
        #     stop = False
        #     best_element = min(random_subset, key=lambda x : x.score)
        #     while len(random_subset) > 0 and not stop:
        #         if random.random() > prob_selecting_fittest:
        #             random_subset.remove(best_element)
        #             best_element = min(random_subset, key=lambda x : x.score)
        #         else:
        #             stop = True
        #     return best_element
        # random selection
        r0 = 0
        r1 = 0
        if self.options.crossover_type == "random":
            r0 = random.randint(0, len(self.population) - 1)
            r1 = random.randint(0, len(self.population) - 1)
        elif self.options.crossover_type == "fittest":
            scores = [x.score for x in self.population]
            r0 = np.argmax(scores)
            scores.pop(r0)
            r1 = np.argmax(scores)
        elif self.options.crossover_type == "tournament":
            # i0 = get_from_tournament()
            print("still to implement tournament crossover type")
            sys.exit()
        elif self.options.crossover_type == "rank":
            tot_rank = len(self.population) * (len(self.population) + 1) / 2
            l : 'list[int]' = []
            while len(l) != 2:
                r = random.random()
                i = 1
                idx_selected = -1
                for i in range(1, len(self.population) + 1):
                    # print(f"i: {i} : {r}")
                    r -= i / tot_rank
                    if r < 0:
                        break
                # print(f"Selected: {self.population_size - i}")

                if len(self.population) - i != idx_selected:
                    l.append(len(self.population) - i)
                    idx_selected = len(self.population) - i
             
            r0 = l[0]
            r1 = l[1]
        
        return Individual(self.population[r0].rules), Individual(self.population[r1].rules)

    def _crossover(self, i0 : Individual, i1 : Individual) -> 'tuple[Individual,Individual]':
        """
        Crossover of the individuals i0 and i1
        """

        idx0 = random.randint(0, len(i0.rules))
        idx1 = random.randint(0, len(i1.rules))
        
        idx0 = min(len(i1.rules), idx0)
        idx1 = min(len(i0.rules), idx1)
        
        new_individual_01 = Individual(i0.rules[:idx0] + i1.rules[idx0:])
        new_individual_10 = Individual(i1.rules[:idx1] + i0.rules[idx1:])
        
        return (new_individual_01, new_individual_10)

    def _mutate(self, i : Individual) -> Individual:
        """
        Applies mutation. Several kinds:
        - add rule
        - remove rule
        0) do nothing
        1) modify rule
            - do nothing
            - change atom
            - change instantiation of such atom
        """
        
        if random.random() < self.options.prob_add_rule:
            rl = random.randint(1, self.options.max_initial_rule_length) # random body length
            new_rule = Rule(self.head_candidates, self.body_candidates, rl)
            i.rules.append(new_rule)
        
        should_drop = [random.random() < self.options.prob_drop_rule for _ in range(len(i.rules))]
        # to_drop = [i for i, j in enumerate(should_drop) if j == True]
        new_rules : 'list[Rule]' = []
        for rule, drop in zip(i.rules, should_drop):
            if not drop:
                new_rules.append(rule)

        for idx_rule, r in enumerate(new_rules):
            if random.random() < self.options.prob_modify:
                new_body : 'list[list[int]]' = []
                for idx, a in enumerate(r.body):
                    mutation_kind = random.choices([0,1,2],[
                        self.options.prob_change_atom,
                        self.options.prob_change_instantiation,
                        1 - (self.options.prob_change_atom + self.options.prob_change_instantiation)])[0]
                    if mutation_kind == 1: # change atom
                        selected_atom = random.randint(0, len(r.body_candidates) - 1)
                        selected_instantiation = random.randint(0, len(r.body_candidates[selected_atom].possible_instantiations) - 1)
                        new_body.append([selected_atom,selected_instantiation])
                    elif mutation_kind == 2: # change instantiation
                        selected_atom = r.body[idx][0]
                        selected_instantiation = random.randint(0, len(r.body_candidates[selected_atom].possible_instantiations) - 1)
                        new_body.append([selected_atom,selected_instantiation])
                    else: # do nothing
                        new_body.append(a)
                new_rules[idx_rule].body = new_body
        
        return Individual(new_rules)
                

    def run_genetic_loop(self) -> Individual:
        """
        Runs the genetic loop.
        """
        
        start_time = time.time()
        
        for it in range(self.options.number_of_evolutionary_cycles + 1):
        # for it in range(10):
            if self.options.verbosity >= 1 and it % self.options.iterations_print_step == 0:
                best_score = self.population[0].score
                print(f"Iteration: {it}. Best individual with score: {best_score}")
            # select two individuals
            i0, i1 = self._select_individuals()
            if self.options.verbosity >= 3:
                print("Selected for crossover")
                print(i0)
                print(i1)
            
            # crossover
            i0, i1 = self._crossover(i0,i1)
            if self.options.verbosity >= 3:
                print("Obtained from crossover")
                print(i0)
                print(i1)
            
            # mutate - crucial the deepcopy, since _mutate modifies the input class
            if self.options.verbosity >= 3:
                print("Mutation step")
            i0 = self._mutate(copy.deepcopy(i0))
            i1 = self._mutate(copy.deepcopy(i1))
            
            # evaluate
            if self.options.verbosity >= 3:
                print("Evaluation step")
            ind_list = [i0,i1]
            l = [ir.get_individual_as_input_program() for ir in ind_list]
            # print(l)
            ll_ind = self.prolog_int.compute_ll_rules(l, self.options.train_set)
       
            for ll, idx in zip(ll_ind, range(len(ind_list))):
                ind_list[idx].score = ll
                
            # replace
            self.population = self.population + ind_list
            self.population.sort(reverse=True)
            
            # drop exceeding elements
            if self.options.verbosity >= 3:
                print("Dropping after insertion")
                for i in range(1, len(ind_list) + 1):
                    print(self.population[len(self.population) - i])
            
            # standard: drop the worst scores
            # age regularized: drop the oldest
            for i in range(len(ind_list)):
                if random.random() < self.options.age_regularized_prob:
                    oldest_index = np.argmin([x.birth_time for x in self.population])
                    self.population.pop(oldest_index)
                else:
                    self.population = self.population[:-1]
        
        if self.options.verbosity >= 2:
            print("Final population")
            for i in self.population:
                print(i)
                print(i.get_individual_as_input_program())
            
        # print(*self.population)
        
        elapsed_time = time.time() - start_time
        if self.options.verbosity >= 1:
            print(f"Terminated evolutionary loop in {elapsed_time} second")

        return self.population[0]