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
    
        
    def _query_prolog(self, query : str, expected : bool, return_var : str):
        """
        Wrapper for query once.
        """
        res = janus.query_once(query)
        if res["truth"] != expected:
            print(f"Error in running query {query}")
            sys.exit()
        
        if return_var != "":
            return res[return_var]
        
        return ""
    

    def get_modes(self) -> 'tuple[list[list[str]], list[list[str]]]':
        """
        Gets the modeh, modeb, and targe from file.
        """
        modeh = self._query_prolog("get_mode(h,L)", True, "L")
        modeb = self._query_prolog("get_mode(b,L)", True, "L")

        return modeh, modeb
        

    def _query_for_ll(self, in_p : str, folds : 'list[str]') -> 'list[float]':
        """
        Query prolog for LL.
        """
        # janus.consult("bg", self.lines_bg + f"\n{in_p}\n")
    
        # res = janus.query_once("retractall(in(_)).")
        self._query_prolog("retractall(in(_)).", True, "")
        
        # add a fail so there is no variables bindings
        self._query_prolog(f"assert({in_p[:-1]}), fail.", False, "")

        if folds[0] == "train":
            train_set = "train"
        else:
            train_set = ','.join(folds)

        ll = self._query_prolog(f"get_lls(LL, [{train_set}]).", True, "LL")
        
        return ll
        

    def compute_ll_rules(self, r_list : 'list[str]', folds : 'list[str]') -> 'list[float]':
        """
        Computes the LL of the rules.
        """
        # alternative with multiple in/1
        # return self._query_for_ll('\n'.join(r_list), train_or_test)
        ll_list : 'list[float]' = []
        for r in r_list:
            res = self._query_for_ll(r, folds)
            ll_list.append(res[0])
        
        return ll_list
    
    def compute_test_results(self, in_p : str, folds : 'list[str]'):
        """
        Computes test results.
        """
        self._query_prolog("retractall(in(_)).", True, "")
        
        # janus.consult("bg", self.lines_bg + f"\n{in_p}\n")
        self._query_prolog(f"assert({in_p[:-1]}), fail.", False, "")
        
        if folds[0] == "test":
            test_set = "test"
        else:
            test_set = ','.join(folds)

        res = janus.query_once(f"get_test_results(P,[{test_set}],LL,AUCROC,AUCPR).")
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
  % in(P),test(P,Fold,LL,_,_,_,_).
  induce_par(Fold,P),test(P,Fold,LL,_,_,_,_).
  

get_lls(LLList,Fold):-
  % findall(LL,(in(P),test(P,Fold,LL,_,_,_,_)),LLList).
  findall(LL,get_ll(LL,Fold),LLList).
"""

GET_TEST_RESULTS_CODE = """
get_test_results(PS,Folds,LL,AUCROC,AUCPR):-
    induce_par(Folds,P),test(P,[test],LL,AUCROC,_,AUCPR,_),
    term_string(P,PS).
"""