from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
from flask import Flask, jsonify
from flask_cors import CORS
import time
import threading

from stockfish import Stockfish
import Board as bo

pieces = {
    "P" : "pawn", "R" : "rook", "N" : "knight", "B" : "bishop", "Q" : "queen", "K": "king",
    "p" : "pawn", "r" : "rook", "n" : "knight", "b" : "bishop", "q" : "queen", "k": "king"
}
def filterMoveList(l:list, piece:str, fr0m:str, to:str):
    t = []
    for i in range(len(l)):
        if piece != None and l[i].name != piece[0]:
            t.append(i)
        elif fr0m != None and bo.notation[l[i].fr0m] != fr0m:
            t.append(i)
        elif to != None and bo.notation[l[i].t0] != to:
            t.append(i)

    for i in range(len(t)-1, -1, -1):
        l.pop(t[i])
    return l

def convertString(s:str):
    new = ""
    number = 0
    j = 0
    while s[j] != " ":
        if s[j] == "/":
            j+=1
            continue;
        if number != 0:
            new += "_"
            number -= 1
            if number == 0:
                j += 1
            continue
        if s[j].isdigit():
            number = int(s[j])
        else:
            new += s[j]
            j+=1
    #print("newString: ")
    #print(new)
    return new


class Game:
    def __init__(self, color: str, difficulty: int):
        self.stBoard = None
        self.myBoard = None
        self.startGame(color, difficulty)
    

    def startGame(self, color: str, difficulty: int):
        self.myBoard = bo.Board()
        self.stBoard = Stockfish(path="stockfish", depth=10, parameters=
                      {"Threads": 2, "Minimum Thinking Time": 30, "Skill Level": difficulty})
        #print(self.stBoard.get_parameters())
        if color == "black":
            best = self.stBoard.get_best_move()
            self.myBoard.placeFEN(self.stBoard.get_fen_position())
            piece = pieces[self.myBoard.board[bo.rNotation[best[:2]][0]][bo.rNotation[best[:2]][1]].name]
            self.stBoard.make_moves_from_current_position([best])
            print(self.stBoard.get_board_visual())
            print(piece + " from " + best[:2] + " to " + best[-2:])
            return
        print(self.stBoard.get_board_visual())
        

    def makeMove(self, piece, fr0m, to):
        if piece == None and fr0m == None and to != None:
            piece = "Pawn"
        #print(piece, fr0m, to)
        self.myBoard.placeFEN(self.stBoard.get_fen_position())
        self.myBoard.possibleMoves()
        list = filterMoveList(self.myBoard.psm, piece, fr0m, to)
        if len(list) == 1:
            self.stBoard.make_moves_from_current_position([bo.notation[list[0].fr0m] + bo.notation[list[0].t0]]) 
        else: 
            print("This Move is not possible or not complete")
            return
        #print(self.myBoard.printMoveList(self.myBoard.psm))
        print(self.stBoard.get_board_visual())
        update_string(convertString(self.stBoard.get_fen_position()))

        #Engine Move:
        best = self.stBoard.get_best_move()
        #print(best)
        capture = str(self.stBoard.will_move_be_a_capture(best))
        self.myBoard.placeFEN(self.stBoard.get_fen_position())
        piece = pieces[self.myBoard.board[bo.rNotation[best[:2]][0]][bo.rNotation[best[:2]][1]].name]
        self.stBoard.make_moves_from_current_position([best])
        print(self.stBoard.get_board_visual())
        update_string(convertString(self.stBoard.get_fen_position()))
        if capture == "Capture.NO_CAPTURE":
            print(piece + " from " + best[:2] + " to " + best[-2:])
        else:
            print(piece + " from " + best[:2] + " takes on " + best[-2:])

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

current_string = convertString("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

@app.route('/api/get-string', methods=['GET'])
def get_string():
    return jsonify(message=current_string)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('update', {'message': current_string})

def update_string(new_string):
    global current_string
    current_string = new_string
    socketio.emit('update', {'message': current_string})

def runGame():
    time.sleep(10)
    g = Game("white", 12)
    time.sleep(5)
    g.makeMove("Pawn", "d2", "d4")
    time.sleep(5)
    g.makeMove("N", "g1", "f3")
    time.sleep(5)
    g.makeMove("B", "c1", "f4")

    

if __name__ == '__main__':
    gameThread = threading.Thread(target=runGame)
    gameThread.start()
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)
