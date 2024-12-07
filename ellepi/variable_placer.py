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
        if '#' in self.modes:
            print("# in mode bias not supported")

        possible_vars: 'list[str]' = ['A'+f"{i}" for i in range(self.number_of_variables)] + ["_"]
        ground_modes: 'list[int]' = [idx for idx in range(0, len(self.modes)) if self.modes[idx] not in ['+', '-', '#']]
        for t in it.product(possible_vars, repeat=(self.arity - len(ground_modes))):
            inst: str = self.name
            if self.arity > 0:
                lv : 'list[str]' = ['']*self.arity
                # use the same ground modes
                for nm in ground_modes:
                    lv[nm] = self.modes[nm]

                idx_var = 0
                for i in range(0, self.arity):
                    if lv[i] == '':
                        lv[i] = t[idx_var]
                        idx_var += 1
                
                inst += "(" + ','.join(lv) + ")"
            self.possible_instantiations.append(inst)