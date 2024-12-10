import sys

import janus_swi as janus

class PrologInterface:
    """
    Prolog interface through Janus.
    """
    def __init__(
            self,
            bg : str,
            backend : str,
            verbosity : int = 0
        ) -> None:
        self.verbosity = verbosity
        self.backend = backend

        # read bg knowledge
        f = open(bg, "r")
        lines_bg = f.read()
        f.close()

        predicate_induce = "induce_par" if self.backend == "SLIPCOVER" else "induce_par_lift"
        predicate_test = "test" if self.backend == "SLIPCOVER" else "test_lift"
            
        ll_code = GET_LL_CODE.replace("__PREDICATE_INDUCE__", predicate_induce).replace("__PREDICATE_TEST__", predicate_test)
        test_code = GET_TEST_RESULTS_CODE.replace("__PREDICATE_INDUCE__", predicate_induce).replace("__PREDICATE_TEST__", predicate_test)

        self.lines_bg = lines_bg + GET_MODE_CODE + ll_code + test_code
        
        janus.consult("bg", self.lines_bg)
    
        
    def _query_prolog(self, query : str, expected : bool, return_var : str = ""):
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
        self._query_prolog("retractall(in(_)).", True)
        
        # add a fail so there is no variables bindings
        self._query_prolog(f"assert({in_p[:-1]}), fail.", False)

        if folds[0] == "train":
            train_set = "train"
        else:
            train_set = ','.join(folds)

        ll_and_sum_probs = self._query_prolog(f"get_lls(LLPList, [{train_set}]).", True, "LLPList")
        
        return ll_and_sum_probs
        

    def compute_ll_rules(self, r_list : 'list[str]', folds : 'list[str]') -> 'list[list[float]]':
        """
        Computes the LL of the rules.
        """
        # alternative with multiple in/1
        # return self._query_for_ll('\n'.join(r_list), train_or_test)
        ll_list_sum_probs : 'list[list[float]]' = []
        for r in r_list:
            res = self._query_for_ll(r, folds)
            ll_list_sum_probs.append(res)
        
        return ll_list_sum_probs
    
    def compute_test_results(self, in_p : str, train_folds : 'list[str]', test_folds : 'list[str]'):
        """
        Computes test results.
        """
        self._query_prolog("retractall(in(_)).", True, "")
        
        # janus.consult("bg", self.lines_bg + f"\n{in_p}\n")
        self._query_prolog(f"assert({in_p[:-1]}), fail.", False, "")
        
        if train_folds[0] == "train":
            train_set = "train"
        else:
            train_set = ','.join(train_folds)

        if test_folds[0] == "test":
            test_set = "test"
        else:
            test_set = ','.join(test_folds)

        # print(f"get_test_results(P,[{train_set}],[{test_set}],LL,AUCROC,AUCPR).")
        res = janus.query_once(f"get_test_results(P,[{train_set}],[{test_set}],LL,AUCROC,AUCPR).")
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
get_arguments(Atom,AgumentsString):-
    Atom =.. Arguments,
    maplist(term_string,Arguments,AgumentsString).

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

get_prob((_:P;_:-_),P).

get_ll(LL,SumProbs,Fold):-
  % in(P),test(P,Fold,LL,_,_,_,_).
  % induce_par(Fold,P),
  __PREDICATE_INDUCE__(Fold,P),
  __PREDICATE_TEST__(P,Fold,LL,_,_,_,_),
  maplist(get_prob, P, ProbList),
  sum_list(ProbList, SumProbs).
  

get_lls(LLPListFlat,Fold):-
  % findall(LL,(in(P),test(P,Fold,LL,_,_,_,_)),LLList).
  findall([LL,P],get_ll(LL,P,Fold),LLPList),
  flatten(LLPList,LLPListFlat).
"""

GET_TEST_RESULTS_CODE = """
get_test_results(PS,TrainFolds,TestFolds,LL,AUCROC,AUCPR):-
    % induce_par(TrainFolds,P),
    __PREDICATE_INDUCE__(TrainFolds,P),
    __PREDICATE_TEST__(P,TestFolds,LL,AUCROC,_,AUCPR,_),
    term_string(P,PS).
"""