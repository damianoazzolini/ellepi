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
        self.lines_bg = lines_bg + GET_MODE_CODE + GET_LL_CODE

    def get_modes(self) -> 'tuple[list[list[str]], list[list[str]]]':
        """
        Gets the modeh, modeb, and targe from file.
        """
        
        # TODO: move consult in the constructor, so I consult the file
        # once and then use assert and retract to set the input program
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

    def _query_for_ll(self, in_p : str) -> 'list[float]':
        janus.consult("bg", self.lines_bg + f"\n{in_p}\n")
        
        res = janus.query_once("get_lls(LL).")
        if res["truth"]:
            ll = res["LL"]
        else:
            print(f"Error in computing LL for rule {r}")
            sys.exit()
        
        return ll
        

    def compute_ll_rules(self, r_list : 'list[str]') -> 'list[float]':
        """
        Computes the LL of the rule.
        """
        
        in_p = ""
        for r in r_list:
            r = r.split(":-") # to add the probability
            r = r[0] + ":0.5 :- " + r[1]
            
            in_p += f"in([({r})]).\n"
        
        return self._query_for_ll(in_p)

    def compute_ll_programs(self, r_list : 'list[list[str]]') -> 'list[float]':
        """
        Compute the LL of the programs.
        """
        # TODO: compute the LL for each program with a Prolog call
        print(r_list)
        in_programs = ""
        for individual in r_list:
            current_in = "in(["
            for rule in individual:
                r = rule.split(":-") # to add the probability
                r = r[0] + ":0.5 :- " + r[1]
                current_in += f"({r}),"
            current_in = current_in[:-1] 
            current_in += "]).\n"
            in_programs += current_in
        
        return self._query_for_ll(in_programs)


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

GET_LL_CODE = """
:- style_check(-discontiguous).
:- style_check(-singleton).

get_ll(LL):-
  in(P),test(P,[train],LL,_,_,_,_).

get_lls(LLList):-
  findall(LL,(in(P),test(P,[train],LL,_,_,_,_)),LLList).
"""