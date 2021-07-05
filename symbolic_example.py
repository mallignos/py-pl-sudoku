from sicstus_symbolic import SicstusSymbolic,SPVariable, SPFunctor,SPTerm
from typing import Union
from plcom_example import pretty_print_sudoku,loop_barrier

Sudoku_char_t = Union[int,SPVariable[int]]
Sudoku_t = list[list[Sudoku_char_t]]

def get_sudoku_1(_ : SPVariable[int]) -> Sudoku_t:
    return [
        [_,6,_,_,1,5,7,_,8],
        [5,_,_,7,_,3,_,4,_],
        [_,7,3,_,_,_,6,_,_],

        [_,9,_,1,5,7,_,8,_],
        [_,_,2,_,9,6,_,_,_],
        [_,_,_,2,8,_,_,1,_],

        [1,3,_,_,_,2,_,_,4],
        [_,_,_,_,_,1,5,_,7],
        [7,_,8,_,_,_,_,6,_]
    ]


def get_sudoku_2(_ : SPVariable[int]) -> Sudoku_t:
    return [
        [_,_,_,_,5,_,_,_,9],
        [4,_,_,_,_,6,_,_,1],
        [_,_,1,_,_,3,_,5,_],

        [_,_,_,_,_,8,4,_,_],
        [_,_,7,_,_,_,_,_,_],
        [_,2,_,1,9,_,_,8,_],

        [_,_,9,_,_,_,_,3,_],
        [6,_,_,_,3,4,_,_,_],
        [3,_,_,_,_,_,7,_,_]
    ]



def main2():
    print_debug=False
    scs = SicstusSymbolic(consultFile="sudoku",debug=print_debug)

    #sc.once("use_module(library(codesio)).")
    scs.use_module('library(codesio)')

    sudoku = scs.newFunctor("sudoku",2,bound=True)
    Board : SPVariable[Sudoku_t] = scs.newVariable("Board")
    _ : SPVariable[int] = scs.newVariable('_')
    #Board.load(get_sudoku_1(_))
    sudokuStorage = scs.newFunctor("sudokuStorage",2)
    sudokuStorage.addRule(("sudoku1",get_sudoku_1(_)))
    sudokuStorage.addRule(("sudoku2",get_sudoku_2(_)))

#    read_from_codes = Functor("read_from_codes",2,bound=True)
#    append = Functor("append",3,bound=True)
#    name = Functor("name",2,bound=True)


#    decode_string = Functor("decode_string",2)
#    decode_string.addRule((I,O), [name(I,A),append(A,".",S),read_from_codes(S,O)])
    


    #print("Success?")
    stop = False
    #Board.eq = (get_sudoku_1(_))
    for __ in scs.query([sudokuStorage('sudoku1',Board) ,sudoku(Board,3)]):
        #print("Tomat",Board.value)
        pretty_print_sudoku(Board.value)
        
        if loop_barrier():
            break

if __name__ == '__main__':
    main2()