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
        self.lines_bg = lines_bg + GET_MODE_CODE + GET_LL_CODE + GET_TEST_RESULTS_CODE
        
        janus.consult("bg", self.lines_bg)

    def get_modes(self) -> 'tuple[list[list[str]], list[list[str]]]':
        """
        Gets the modeh, modeb, and targe from file.
        """

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

    def _query_for_ll(self, in_p : str, train_or_test : str) -> 'list[float]':
        """
        Query prolog for LL.
        """
        # janus.consult("bg", self.lines_bg + f"\n{in_p}\n")
        
        # print(in_p)
        
        # sys.exit()
        
        res = janus.query_once("retractall(in(_)).")
        
        # add a fail so there is no variables bindings
        res = janus.query_once(f"assert({in_p[:-1]}), fail.")
        if res["truth"]:
            print(f"Error in asserting rule {in_p}")
            sys.exit()
        
        res = janus.query_once(f"get_lls(LL, {train_or_test}).")
        if res["truth"]:
            ll = res["LL"]
        else:
            print(f"Error in computing LL for rule {in_p}")
            sys.exit()
        
        return ll
        

    def compute_ll_rules(self, r_list : 'list[str]', train_or_test : str) -> 'list[float]':
        """
        Computes the LL of the rules.
        """
        # alternative with multiple in/1
        # return self._query_for_ll('\n'.join(r_list), train_or_test)
        ll_list : 'list[float]' = []
        for r in r_list:
            res = self._query_for_ll(r, train_or_test)
            ll_list.append(res[0])
        
        return ll_list
    
    def compute_test_results(self, in_p : str):
        """
        Computes test results.
        """
        res = janus.query_once("retractall(in(_)).")
        
        # janus.consult("bg", self.lines_bg + f"\n{in_p}\n")
        res = janus.query_once(f"assert({in_p[:-1]}), fail.")
        if res["truth"]:
            print(f"Error in asserting rule {in_p}")
            sys.exit()
        
        
        res = janus.query_once("get_test_results(P,LL,AUCROC,AUCPR).")
        if res["truth"]:
            p = res["P"]
            ll = res["LL"]
            aucroc = res["AUCROC"]
            aucpr = res["AUCPR"]
        else:
            print(f"Error in computing LL for rule {in_p}")
            sys.exit()
        
        return p, ll, aucroc, aucpr
        


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

get_ll(LL,Fold):-
  % in(P),test(P,[Fold],LL,_,_,_,_).
  induce_par([Fold],P),test(P,[Fold],LL,_,_,_,_).
  

get_lls(LLList,Fold):-
  % findall(LL,(in(P),test(P,[Fold],LL,_,_,_,_)),LLList).
  findall(LL,get_ll(LL,Fold),LLList).
"""

GET_TEST_RESULTS_CODE = """
get_test_results(PS,LL,AUCROC,AUCPR):-
    induce_par([train],P),test(P,[test],LL,AUCROC,_,AUCPR,_),
    term_string(P,PS).
"""