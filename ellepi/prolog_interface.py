import sys

import janus_swi as janus

class PrologInterface:
    """
    Prolog interface through Janus.
    """
    def __init__(
            self,
            bg : str,
            verbosity : int = 0
        ) -> None:
        self.verbosity = verbosity

        # read bg knowledge
        f = open(bg, "r")
        lines_bg = f.read()
        f.close()
        self.lines_bg = lines_bg + GET_MODE_CODE

    def get_modes(self) -> 'tuple[list[list[str]], list[list[str]]]':
        """
        Gets the modeh, modeb, and targe from file.
        """
        
        janus.consult("bg", self.lines_bg)

        res = janus.query_once("get_mode(h,L)")
        if res["truth"]:
            modeh = res["L"]
        else:
            print("Error in querying background file (get_modes_and_target(h,L))")
            sys.exit()
        
        res = janus.query_once("get_mode(b,L)")
        if res["truth"]:
            modeb = res["L"]
        else:
            print("Error in querying background file (get_modes_and_target(b,L))")
            sys.exit()

        return modeh, modeb


GET_MODE_CODE = """
get_arguments(Atom,Arguments):-
    Atom =.. Arguments.

get_mode(HorB,LA):-
    (   HorB = h -> 
    	findall(A,modeh(_,A),LM) ;
    	findall(A,modeb(_,A),LM)
    ),
    maplist(get_arguments,LM,LA).
"""