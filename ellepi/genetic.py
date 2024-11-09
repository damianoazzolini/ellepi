import random

class GeneticOptions:
    """
    Wrapper for all the options of the genetic algorithm.
    """
    def __init__(self) -> None:
        self.population_size : int = 50
        self.mutation_probability : float = 0.05
        self.number_of_evolutionary_cycles : int = 1000
        self.initial_number_of_rules_per_individual : int = 6
        self.sampling_rules_method : str = "weighted" # or random
        self.verbosity : int = 0


class Rule:
    """
    Wrapper for rules.
    """
    def __init__(self,
            rule_as_string : str
        ) -> None:
        self.rule_as_string = rule_as_string
        self.weight = 0
    
    def evaluate_and_assign_weight(self):
        """
        Computes the weight of a single rule (NLL).
        Higher is better.
        """
        self.weight = -1
    
    def __str__(self) -> str:
        return f"{self.rule_as_string} - weight: {self.weight}"
    def __repr__(self) -> str:
        return self.__str__()

class Individual:
    """
    Individual for the genetic algorithm.
    """
    def __init__(self,
            rules : 'list[Rule]'
        ) -> None:
        self.rules = rules
        self.score : float = 0
    
    def compute_score(self):
        """
        Evaluates the score of the current individual.
        """
        # call LIFTCOVER to perform parameter learning on the current
        # program
        self.score = -1
    
    
    def __str__(self) -> str:
        return f"{self.rules} with score: {self.score}"
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
            options : GeneticOptions
        ) -> None:
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
        
        # evaluates rules for weighted sampling
        if self.options.sampling_rules_method == "weighted":
            for r in available_rules:
                r.evaluate_and_assign_weight()
            # sort rules: higher NLL is better
            # available_rules.sort(key=lambda x : x.weight) # not needed
            if self.options.verbosity >= 3:
                print(*available_rules)
        
        attempts = 0
        while len(population) < self.options.population_size:
            # perform weighted sampling for individuals
            if self.options.sampling_rules_method == "weighted":
                weights = [w.weight for w in available_rules]
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
            
        # sort the population in terms of score
        population.sort()
        
        if self.options.verbosity >= 3:
            print(*population)

    
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