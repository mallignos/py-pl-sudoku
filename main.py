from plcom import SicstusCommunicator
from typing import Union,Literal
#import json


################################################################################
### Static Old Sudoku Thingies
################################################################################

Sudoku_char_t = Union[int,Literal['_']]
Sudoku_t = list[list[Sudoku_char_t]]

def pretty_print_sudoku(board : Sudoku_t) -> None:
    header    = "┏━━━━━━━┯━━━━━━━┯━━━━━━━┓"
    breakline = "┠───────┼───────┼───────┨"
    footer    = "┗━━━━━━━┷━━━━━━━┷━━━━━━━┛"

    print(header)
    print("┃ %s %s %s │ %s %s %s │ %s %s %s ┃" % tuple(map(str,board[0])))
    print("┃ %s %s %s │ %s %s %s │ %s %s %s ┃" % tuple(map(str,board[1])))
    print("┃ %s %s %s │ %s %s %s │ %s %s %s ┃" % tuple(map(str,board[2])))
    print(breakline)
    print("┃ %s %s %s │ %s %s %s │ %s %s %s ┃" % tuple(map(str,board[3])))
    print("┃ %s %s %s │ %s %s %s │ %s %s %s ┃" % tuple(map(str,board[4])))
    print("┃ %s %s %s │ %s %s %s │ %s %s %s ┃" % tuple(map(str,board[5])))
    print(breakline)
    print("┃ %s %s %s │ %s %s %s │ %s %s %s ┃" % tuple(map(str,board[6])))
    print("┃ %s %s %s │ %s %s %s │ %s %s %s ┃" % tuple(map(str,board[7])))
    print("┃ %s %s %s │ %s %s %s │ %s %s %s ┃" % tuple(map(str,board[8])))
    print(footer)


sudoku_board_1 : Sudoku_t = [
    ['_',6,'_','_',1,5,7,'_',8],
    [5,'_','_',7,'_',3,'_',4,'_'],
    ['_',7,3,'_','_','_',6,'_','_'],

    ['_',9,'_',1,5,7,'_',8,'_'],
    ['_','_',2,'_',9,6,'_','_','_'],
    ['_','_','_',2,8,'_','_',1,'_'],

    [1,3,'_','_','_',2,'_','_',4],
    ['_','_','_','_','_',1,5,'_',7],
    [7,'_',8,'_','_','_','_',6,'_']
]

sudoku_board_2 : Sudoku_t = [
    ['_','_','_','_',5,'_','_','_',9],
    [4,'_','_','_','_',6,'_','_',1],
    ['_','_',1,'_','_',3,'_',5,'_'],

    ['_','_','_','_','_',8,4,'_','_'],
    ['_','_',7,'_','_','_','_','_','_'],
    ['_',2,'_',1,9,'_','_',8,'_'],

    ['_','_',9,'_','_','_','_',3,'_'],
    [6,'_','_','_',3,4,'_','_','_'],
    [3,'_','_','_','_','_',7,'_','_']
]

###############################################################################
### New Helper function
###############################################################################

def stringify_board(board : Sudoku_t) -> str:
    out : list[str] = []
    for row in board:
        out.append('[' + ','.join(map(str,row)) + ']')
    return '[' + ','.join(out) + ']'

###############################################################################
### Sicstus Code Thingies
###############################################################################

def main() -> None:
    print_debug=False
    sc = SicstusCommunicator(consultFile="sudoku",debug=print_debug)

    #sc.once("consult(sudoku).")
    sc.once("use_module(library(codesio)).")
    sc.once("assert((decode_string(Input,O) :- name(Input,A),append(A,\".\",S),read_from_codes(S,O))).")

    sc.state( stringify_board(sudoku_board_1) )

    #print(sc.state())

    stop = False
    #for board in sc.call("P=" + stringify_board(sudoku_board_1) + ",sudoku(P,3),Result=P."):
    for board in sc.call("decode_string(StateIn,P),sudoku(P,3),Result=P."):

        pretty_print_sudoku(board)
        
        while True:
            inp = str(input(" ? fler svar? (ja/NEJ) "))
            if inp.lower() in [';','ja','j']:
                break
            elif inp.lower() in ['','n','nej']:
                stop = True
                break
        if stop is True:
            break


if __name__ == '__main__':
    main()