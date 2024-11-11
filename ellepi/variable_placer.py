import itertools as it

class Atom:
    """
    Class representing an atom
    """
    def __init__(self,
            name : str,
            modes : 'list[str]',
            nvars : int
        ) -> None:
        self.name = name
        self.modes = modes
        self.arity = len(modes)
        self.number_of_variables = nvars
        self.possible_instantiations : 'list[str]' = []
        
        self._place_variables()
    
    def __str__(self) -> str:
        d = self.name + "(" + ','.join(self.modes) + ") " + str(self.number_of_variables)
        return d + ": " + ' '.join(self.possible_instantiations)
    def __repr__(self) -> str:
        return self.__str__()
        
        
    def _place_variables(self):
        '''
        The number of possible placements is nvar^{arity}.
        If one of the arguments is ground, we can find its grounding and the
        total number of placements is: {nvar}^{arity - ngroundpos} x \prod_i ngroundings_i
        Example:
        variables | arity | total placements
        3 | 2 | 9
        3 | 3 | 27 
        '''
        def _flatten_tuple(data):
            # to flatten (('A0', 'A0'), 'a') -> ('A0', 'A0', 'a')
            # not tested
            flattened : 'list[str]' = []
            for item in data:
                # If the item is a tuple, recursively flatten it
                if isinstance(item, tuple):
                    flattened.extend(_flatten_tuple(item))
                else:
                    flattened.append(item)
            return tuple(flattened)

        ############################## BODY
        # assume no groundings
        possible_vars = ['A'+f"{i}" for i in range(self.number_of_variables)] + ["_"]
        if "#" not in self.modes:
            for t in it.product(possible_vars, repeat=self.arity):
                inst = self.name
                if self.arity > 0:
                    inst += "(" + ','.join(t) + ")"
                self.possible_instantiations.append(inst)
        else:
            pass
            # TODO: find instantiations
            # TODO: i also need to consider the position of the groudnings
            # groundings = find_instantiations() # TODO: call prolog to find them
            # for t in it.product(possible_vars, groundings):
            #     pass
            
