import Piece as pi
import Move as mo
import copy as co
import random
import time


notation = {
    (0, 0) : "a1", (0,1) : "b1", (0,2) : "c1", (0,3) : "d1", (0,4) : "e1", (0,5) : "f1", (0,6) : "g1", (0,7) : "h1",
    (1,0) : "a2", (1,1) : "b2", (1,2) : "c2", (1,3) : "d2", (1,4) : "e2", (1,5) : "f2", (1,6) : "g2", (1,7) : "h2", 
    (2,0) : "a3", (2,1) : "b3", (2,2) : "c3", (2,3) : "d3", (2,4) : "e3", (2,5) : "f3", (2,6) : "g3", (2,7) : "h3", 
    (3,0) : "a4", (3,1) : "b4", (3,2) : "c4", (3,3) : "d4", (3,4) : "e4", (3,5) : "f4", (3,6) : "g4", (3,7) : "h4", 
    (4,0) : "a5", (4,1) : "b5", (4,2) : "c5", (4,3) : "d5", (4,4) : "e5", (4,5) : "f5", (4,6) : "g5", (4,7) : "h5",
    (5,0) : "a6", (5,1) : "b6", (5,2) : "c6", (5,3) : "d6", (5,4) : "e6", (5,5) : "f6", (5,6) : "g6", (5,7) : "h6",
    (6,0) : "a7", (6,1) : "b7", (6,2) : "c7", (6,3) : "d7", (6,4) : "e7", (6,5) : "f7", (6,6) : "g7", (6,7) : "h7", 
    (7,0) : "a8", (7,1) : "b8", (7,2) : "c8", (7,3) : "d8", (7,4) : "e8", (7,5) : "f8", (7,6) : "g8", (7,7) : "h8",
}
rNotation = {v:k for k, v in notation.items()}

class Board:
    def __init__(self):
        self.board = []
        self.check = False
        self.wK = None
        self.bK = None
        self.RK = True
        self.RQ = True
        self.Rk = True
        self.Rq = True
        self.ac = None #active Color
        self.hmC = 0 #Halfmove clock
        self.fmN = 0 #Fullmove number
        self.psE = (None, None) #En Passant
        self.psm = []
        self.history = []
        self.finished = False
        for i in range(8):
            self.board.append([])
            for j in range(8):
                self.board[i].append(pi.Piece("F", " "))


    def printBoard(self):
        for i in range(7, -1, -1):
            print()
            for j in range(8):
                #print((i,j), end = " ")
                if self.board[i][j].color == "b":
                    print(str(self.board[i][j].name).lower(), end= ' ')
                elif self.board[i][j].name == "F":
                    print("_", end=' ')
                    
                else:
                    print(str(self.board[i][j].name), end=' ')
        print()
        print()

    def printMoveList(self, l: list):
        s = ""
        for x in l:
            s += (str(x) + "\n")
        return s

    def rightMoveNotation(self, l: list):
        m = []
        for x in l:
            if x.name == "P":
                if x.take == True:
                    m.append(notation[x.fr0m][0] + "x" + notation[x.t0])
                else:
                    m.append(notation[x.t0])
                if x.promotion != None:
                    m[-1] += ("=" + x.promotion)
            else:
                if x.take == True:
                    m.append(x.name + "x" + notation[x.t0])
                else:
                    m.append(x.name + notation[x.t0])
            
            if x.check == True:
                m[-1] += "+" 
        t = []
        for i in range(len(m)):
            if m.count(m[i]) > 1:
                u = []
                t.append(u)
                for j in range(len(m)):
                    if m[j] == m[i]:
                        u.append(j)
                if t.count(u) > 1:
                    t.remove(t[-1])

        for y in t:
            for z in y:
                m[z] = m[z][:1] + notation[l[z].fr0m][0] + m[z][1:]
             
        t = []
        for i in range(len(m)):
            if m.count(m[i]) > 1:
                u = []
                t.append(u)
                for j in range(len(m)):
                    if m[j] == m[i]:
                        u.append(j)
                if t.count(u) > 1:
                    t.remove(t[-1])

        for y in t:
            for z in y:
                m[z] = m[z][:2] + notation[l[z].fr0m][1] + m[z][2:]        
        
        """"
        for i in range(len(m)):
            if m.count(m[i]) > 1:
                m[i] = m[i][:1] + notation[l[i].fr0m][1] + m[i][2:]
    
        
        for i in range(len(m)):
            if m.count(m[i]) > 1:
                print(str(m.count(m[i])) + ": " + m[i])
        """        
        return m


    def placePiece(self, n: str, c: str, p: tuple):
        if n == "K":
            if c == "w":
                self.wK = p
            else:
                self.bK = p
        t = pi.Piece(n, c) 
        self.board[p[0]][p[1]] = t  

    def clearPiece(self, p: tuple):
        self.board[p[0]][p[1]].name = "F"
        self.board[p[0]][p[1]].color = " "

    def makeMoveU(self, m: mo.Move):
        self.possibleMoves()
        print(self.possibleMoves)
        if m in self.psm:
            self.makeMove(m)
        else:
            print("Dieser Zug ist nicht in der Lister der möglichen Züge")
    
    def makeMove(self, m: mo.Move):
        if m.t0 == self.psE and m.name == "P":
            if self.ac == "w":
                self.clearPiece((m.t0[0]+1, m.t0[1]))
            else:
                self.clearPiece((m.t0[0]-1, m.t0[1]))

        if m.name == "P" and abs(m.fr0m[0] - m.t0[0]) > 1:
            if self.ac == "w":
                self.psE = (m.fr0m[0], m.fr0m[1] + 1)
        else: 
            self.psE = (None, None)
        if m.promotion != None:
            self.placePiece(m.promotion, self.ac, m.t0)
            self.clearPiece(m.fr0m)
        else:
            self.placePiece(m.name, self.ac, m.t0)
            self.clearPiece(m.fr0m)
        if m.take == True:
            self.hmC = 0
        else:
            self.hmC += 1
        if self.ac == "w":
            self.ac = "b"
        else:
            self.ac = "w"
            self.fmN += 1
        #self.history.append((self.fmN, m))


    def placeDefault(self):
        self.ac = "w"
        self.RK = True
        self.RQ = True
        self.Rk = True
        self.Rq = True
        self.hmC = 0 #Halfmove clock nach Schlagen Bauer
        self.fmN = 0 #Fullmove number
        #white:
        self.board[0][0] = pi.Piece("R", "w")
        self.board[0][1] = pi.Piece("N", "w")
        self.board[0][2] = pi.Piece("B", "w")
        self.board[0][3] = pi.Piece("Q", "w")
        self.board[0][4] = pi.Piece("K", "w")
        self.wK = (0, 4)
        self.board[0][5] = pi.Piece("B", "w")
        self.board[0][6] = pi.Piece("N", "w")
        self.board[0][7] = pi.Piece("R", "w")
        
        for i in range(8):
            self.board[1][i] = pi.Piece("P", "w") 
        
        #black:
        self.board[7][0] = pi.Piece("R", "b")
        self.board[7][1] = pi.Piece("N", "b")
        self.board[7][2] = pi.Piece("B", "b")
        self.board[7][3] = pi.Piece("Q", "b")
        self.board[7][4] = pi.Piece("K", "b")
        self.bK = (7, 4)
        self.board[7][5] = pi.Piece("B", "b")
        self.board[7][6] = pi.Piece("N", "b")
        self.board[7][7] = pi.Piece("R", "b")

        for i in range(8):
            self.board[6][i] = pi.Piece("P", "b") 

    def placeFEN(self, s: str):
        try:
            for i in range(8):
                for j in range(8):
                    self.clearPiece((i,j))
                    
            pieces = s.split("/")
            rest = pieces[-1].split(" ")
            pieces[-1] = rest[0]
            rest.remove(rest[0])
            #place Pieces
            i = 7
            j = 0
            for x in pieces: 
                for k in range(len(x)):
                    if x[k].isupper():
                        self.placePiece(x[k], "w", (i, j))
                    elif x[k].islower():
                        self.placePiece(x[k].upper(), "b", (i, j))
                    else:
                        j += int(x[k]) - 1
                    j += 1
                i -= 1
                j = 0
            
            self.ac = rest.pop(0)
            self.RK == False
            self.RQ == False
            self.Rk == False
            self.Rq == False   
            for x in rest.pop(0):
                if x == "K":
                    self.RK == True
                    break
                if x == "Q":
                    self.RQ == True
                    break
                if x == "k":
                    self.Rk == True
                    break
                if x == "q":
                    self.Rq == True
            
            te = rest.pop(0)
            if te == "-":
                self.psE = (None, None)
            else:
                self.psE = rNotation[te]
            self.hmC = int(rest.pop(0))
            self.fmN = int(rest.pop(0))


        except ValueError or IndexError:
            print("Fehlerhafte Eingabe des DEF-Codes!")
                

    def wpsmP(self, l: list, p: tuple):       
        i = p[0]
        j = p[1]

        if self.psE != (None, None) and i == 4:
            if j+1 <= 7 and (i+1, j+1) == self.psE:
                l.append(mo.Move("P", (i,j), self.psE, True, False, None))
            elif j-1 >= 0 and (i+1, j-1) == self.psE:
                l.append(mo.Move("P", (i,j), self.psE, True, False, None))
        if self.board[i+1][j].name == "F":                                               #Wenn eins
            if i+1 == 7:
                l.append(mo.Move("P", (i,j), (i+1, j), False, False, "R"))
                l.append(mo.Move("P", (i,j), (i+1, j), False, False, "N"))
                l.append(mo.Move("P", (i,j), (i+1, j), False, False, "B"))
                l.append(mo.Move("P", (i,j), (i+1, j), False, False, "Q"))
            else:
                l.append(mo.Move("P", (i,j), (i+1, j), False, False, None))
                #Wenn zwei möglich
                if i == 1 and self.board[i+2][j].name == "F":
                    l.append(mo.Move("P", (i,j), (i+2, j), False, False, None))
               
        if i+1 == 7:
            if j-1 >= 0 and self.board[i+1][j-1].name != "F" and self.board[i+1][j-1].color == "b":   #Wen links schlagen
                l.append(mo.Move("P", (i,j), (i+1, j-1), True, False, "R"))
                l.append(mo.Move("P", (i,j), (i+1, j-1), True, False, "N"))
                l.append(mo.Move("P", (i,j), (i+1, j-1), True, False, "B"))
                l.append(mo.Move("P", (i,j), (i+1, j-1), True, False, "Q"))

            if j+1 <= 7 and self.board[i+1][j+1].name != "F" and self.board[i+1][j+1].color == "b":   #Wen rechts schlagen
                l.append(mo.Move("P", (i,j), (i+1, j+1), True, False, "R"))
                l.append(mo.Move("P", (i,j), (i+1, j+1), True, False, "N"))
                l.append(mo.Move("P", (i,j), (i+1, j+1), True, False, "B"))
                l.append(mo.Move("P", (i,j), (i+1, j+1), True, False, "Q"))
        else:
            if j-1 >= 0 and self.board[i+1][j-1].name != "F" and self.board[i+1][j-1].color == "b":   #Wen links schlagen
                l.append(mo.Move("P", (i,j), (i+1, j-1), True, False, None))

            if j+1 <= 7 and self.board[i+1][j+1].name != "F" and self.board[i+1][j+1].color == "b":   #Wen rechts schlagen
                l.append(mo.Move("P", (i,j), (i+1, j+1), True, False, None))
            
    def bpsmP(self, l:list, p:tuple):
        i = p[0]
        j = p[1]
        
        if self.psE != (None, None) and i == 3:
            if j+1 <= 7 and (i-1, j+1) == self.psE:
                l.append(mo.Move("P", (i,j), self.psE, True, False, None))
            elif j-1 >= 0 and (i-1, j-1) == self.psE:
                l.append(mo.Move("P", (i,j), self.psE, True, False, None))
        if self.board[i-1][j].name == "F":                                               #Wenn eins
            if i-1 == 0:
                l.append(mo.Move("P", (i,j), (i-1, j), False, False, "R"))
                l.append(mo.Move("P", (i,j), (i-1, j), False, False, "N"))
                l.append(mo.Move("P", (i,j), (i-1, j), False, False, "B"))
                l.append(mo.Move("P", (i,j), (i-1, j), False, False, "Q"))
            else:
                l.append(mo.Move("P", (i,j), (i-1, j), False, False, None))
                #Wenn zwei möglich
                if i == 6 and self.board[i-2][j].name == "F":
                    l.append(mo.Move("P", (i,j), (i-2, j), False, False, None))
                       
        if i-1 == 0:
            if j-1 >= 0 and self.board[i-1][j-1].name != "F" and self.board[i-1][j-1].color == "w":   #Wen links schlagen
                l.append(mo.Move("P", (i,j), (i-1, j-1), True, False, "R"))
                l.append(mo.Move("P", (i,j), (i-1, j-1), True, False, "N"))
                l.append(mo.Move("P", (i,j), (i-1, j-1), True, False, "B"))
                l.append(mo.Move("P", (i,j), (i-1, j-1), True, False, "Q"))

            if j+1 <= 7 and self.board[i-1][j+1].name != "F" and self.board[i-1][j+1].color == "w":   #Wen rechts schlagen
                l.append(mo.Move("P", (i,j), (i-1, j+1), True, False, "R"))
                l.append(mo.Move("P", (i,j), (i-1, j+1), True, False, "N")) 
                l.append(mo.Move("P", (i,j), (i-1, j+1), True, False, "B")) 
                l.append(mo.Move("P", (i,j), (i-1, j+1), True, False, "Q"))    
        else:
            if j-1 >= 0 and self.board[i-1][j-1].name != "F" and self.board[i-1][j-1].color == "w":   #Wen links schlagen
                l.append(mo.Move("P", (i,j), (i-1, j-1), True, False, None))

            if j+1 <= 7 and self.board[i-1][j+1].name != "F" and self.board[i-1][j+1].color == "w":   #Wen rechts schlagen
                l.append(mo.Move("P", (i,j), (i-1, j+1), True, False, None))                          
            

    def wpsmR(self, l: list, p: tuple):
        i = p[0]
        j = p[1]
        for k in range(1, 8-i, 1): #Nach oben                      
            if self.board[i+k][j].name == "F" or self.board[i+k][j].color == "b":
                if self.board[i+k][j].name == "F":
                    l.append(mo.Move("R", (i,j), (i+k, j), False, False, None))
                else:
                    l.append(mo.Move("R", (i,j), (i+k, j), True, False, None))
                    break
            else:
                break

        for k in range(1, i + 1, 1): #Nach unten     
            if self.board[i-k][j].name == "F" or self.board[i-k][j].color == "b":
                if self.board[i-k][j].name == "F":
                    l.append(mo.Move("R", (i,j), (i-k, j), False, False, None))
                else:
                    l.append(mo.Move("R", (i,j), (i-k, j), True, False, None))
                    break
            else:
                break
                
        for k in range(1, 8-j, 1): #nach rechts
            if self.board[i][j+k].name == "F" or self.board[i][j+k].color == "b":
                if self.board[i][j+k].name == "F":
                    l.append(mo.Move("R", (i,j), (i, j+k), False, False, None))
                else:
                    l.append(mo.Move("R", (i,j), (i, j+k), True, False, None))
                    break
            else:
                break
        
        for k in range(1, j + 1, 1): #Nach links     
            if self.board[i][j-k].name == "F" or self.board[i][j-k].color == "b":
                if self.board[i][j-k].name == "F":
                    l.append(mo.Move("R", (i,j), (i, j-k), False, False, None))
                else:
                    l.append(mo.Move("R", (i,j), (i, j-k), True, False, None))
                    break
            else:
                break
    
    def bpsmR(self, l: list, p: tuple):
        i = p[0]
        j = p[1]

        for k in range(1, 8-i, 1): #nach unten
            if self.board[i+k][j].name == "F" or self.board[i+k][j].color == "w":
                if self.board[i+k][j].name == "F":
                    l.append(mo.Move("R", (i,j), (i+k, j), False, False, None))
                else:
                    l.append(mo.Move("R", (i,j), (i+k, j), True, False, None))
                    break
            else:
                break

        for k in range(1, i + 1, 1): #nach oben      
            if self.board[i-k][j].name == "F" or self.board[i-k][j].color == "w":
                if self.board[i-k][j].name == "F":
                    l.append(mo.Move("R", (i,j), (i-k, j), False, False, None))
                else:
                    l.append(mo.Move("R", (i,j), (i-k, j), True, False, None))
                    break
            else:
                break
        
        for k in range(1, 8-j, 1): #nach rechts
            if self.board[i][j+k].name == "F" or self.board[i][j+k].color == "w":
                if self.board[i][j+k].name == "F":
                    l.append(mo.Move("R", (i,j), (i, j+k), False, False, None))
                else:
                    l.append(mo.Move("R", (i,j), (i, j+k), True, False, None))
                    break
            else:
                break
        
        for k in range(1, j + 1, 1): #Nach links     
            if self.board[i][j-k].name == "F" or self.board[i][j-k].color == "w":
                if self.board[i][j-k].name == "F":
                    l.append(mo.Move("R", (i,j), (i, j-k), False, False, None))
                else:
                    l.append(mo.Move("R", (i,j), (i, j-k), True, False, None))
                    break
            else:
                break


    def wpsmN(self, l: list, p: tuple):
        i = p[0]
        j = p[1]
        #1 -2
        if i+1 <= 7:      
            if j-2 >= 0:
                if self.board[i+1][j-2].name == "F":
                    l.append(mo.Move("N", (i,j), (i+1, j-2), False, False, None))
                if self.board[i+1][j-2].color == "b":
                    l.append(mo.Move("N", (i,j), (i+1, j-2), True, False, None))
        #2 -1
        if i+2 <= 7:      
            if j-1 >= 0:
                if self.board[i+2][j-1].name == "F":
                    l.append(mo.Move("N", (i,j), (i+2, j-1), False, False, None))
                if self.board[i+2][j-1].color == "b":
                    l.append(mo.Move("N", (i,j), (i+2, j-1), True, False, None))
        #2 1
        if i+2 <= 7:      
            if j+1 <= 7:
                if self.board[i+2][j+1].name == "F":
                    l.append(mo.Move("N", (i,j), (i+2, j+1), False, False, None))
                if self.board[i+2][j+1].color == "b":
                    l.append(mo.Move("N", (i,j), (i+2, j+1), True, False, None))
        #1 2
        if i+1 <= 7:      
            if j+2 <= 7:
                if self.board[i+1][j+2].name == "F":
                    l.append(mo.Move("N", (i,j), (i+1, j+2), False, False, None))
                if self.board[i+1][j+2].color == "b":
                    l.append(mo.Move("N", (i,j), (i+1, j+2), True, False, None))
        #-1 2
        if i-1 >= 0:      
            if j+2 <= 7:
                if self.board[i-1][j+2].name == "F":
                    l.append(mo.Move("N", (i,j), (i-1, j+2), False, False, None))
                if self.board[i-1][j+2].color == "b":
                    l.append(mo.Move("N", (i,j), (i-1, j+2), True, False, None))
        #-2 1
        if i-2 >= 0:      
            if j+1 <= 7:
                if self.board[i-2][j+1].name == "F":
                    l.append(mo.Move("N", (i,j), (i-2, j+1), False, False, None))
                if self.board[i-2][j+1].color == "b":
                    l.append(mo.Move("N", (i,j), (i-2, j+1), True, False, None))
        #-2 -1
        if i-2 >= 0:      
            if j-1 >= 0:
                if self.board[i-2][j-1].name == "F":
                    l.append(mo.Move("N", (i,j), (i-2, j-1), False, False, None))
                if self.board[i-2][j-1].color == "b":
                   l.append(mo.Move("N", (i,j), (i-2, j-1), True, False, None))
        #-1 -2
        if i-1 >= 0:      
            if j-2 >= 0:
                if self.board[i-1][j-2].name == "F":
                    l.append(mo.Move("N", (i,j), (i-1, j-2), False, False, None))
                if self.board[i-1][j-2].color == "b":
                    l.append(mo.Move("N", (i,j), (i-1, j-2), True, False, None))
            
    def bpsmN(self, l: list, p: tuple):
        i = p[0]
        j = p[1]
        #1 -2
        if i+1 <= 7:      
            if j-2 >= 0:
                if self.board[i+1][j-2].name == "F":
                    l.append(mo.Move("N", (i,j), (i+1, j-2), False, False, None))
                if self.board[i+1][j-2].color == "w":
                    l.append(mo.Move("N", (i,j), (i+1, j-2), True, False, None))
        #2 -1
        if i+2 <= 7:      
            if j-1 >= 0:
                if self.board[i+2][j-1].name == "F":
                    l.append(mo.Move("N", (i,j), (i+2, j-1), False, False, None))
                if self.board[i+2][j-1].color == "w":
                    l.append(mo.Move("N", (i,j), (i+2, j-1), True, False, None))
        #2 1
        if i+2 <= 7:      
            if j+1 <= 7:
                if self.board[i+2][j+1].name == "F":
                    l.append(mo.Move("N", (i,j), (i+2, j+1), False, False, None))
                if self.board[i+2][j+1].color == "w":
                    l.append(mo.Move("N", (i,j), (i+2, j+1), True, False, None))
        #1 2
        if i+1 <= 7:      
            if j+2 <= 7:
                if self.board[i+1][j+2].name == "F":
                    l.append(mo.Move("N", (i,j), (i+1, j+2), False, False, None))
                if self.board[i+1][j+2].color == "w":
                    l.append(mo.Move("N", (i,j), (i+1, j+2), True, False, None))
        #-1 2
        if i-1 >= 0:      
            if j+2 <= 7:
                if self.board[i-1][j+2].name == "F":
                    l.append(mo.Move("N", (i,j), (i-1, j+2), False, False, None))
                if self.board[i-1][j+2].color == "w":
                    l.append(mo.Move("N", (i,j), (i-1, j+2), True, False, None))
        #-2 1
        if i-2 >= 0:      
            if j+1 <= 7:
                if self.board[i-2][j+1].name == "F":
                    l.append(mo.Move("N", (i,j), (i-2, j+1), False, False, None))
                if self.board[i-2][j+1].color == "w":
                    l.append(mo.Move("N", (i,j), (i-2, j+1), True, False, None))
        #-2 -1
        if i-2 >= 0:      
            if j-1 >= 0:
                if self.board[i-2][j-1].name == "F":
                    l.append(mo.Move("N", (i,j), (i-2, j-1), False, False, None))
                if self.board[i-2][j-1].color == "w":
                   l.append(mo.Move("N", (i,j), (i-2, j-1), True, False, None))
        #-1 -2
        if i-1 >= 0:      
            if j-2 >= 0:
                if self.board[i-1][j-2].name == "F":
                    l.append(mo.Move("N", (i,j), (i-1, j-2), False, False, None))
                if self.board[i-1][j-2].color == "w":
                    l.append(mo.Move("N", (i,j), (i-1, j-2), True, False, None))


    def wpsmB(self, l: list, p: tuple):
        i = p[0]
        j = p[1]

        #nach oben links
        m = j
        for k in range(i + 1, 8, 1):
            m -= 1
            if m < 0 or k > 7:
                break
            if self.board[k][m].name == "F" or self.board[k][m].color == "b":
                if self.board[k][m].name == "F":    
                    l.append(mo.Move("B", (i,j), (k,m), False, False, None))    
                else:
                    l.append(mo.Move("B", (i,j), (k,m), True, False, None)) 
                    break
            else:
                break
        #nach oben rechts
        m = j
        for k in range(i + 1, 8, 1):
            m += 1
            if m > 7 or k > 7:
                break
            if self.board[k][m].name == "F" or self.board[k][m].color == "b":
                if self.board[k][m].name == "F":
                    l.append(mo.Move("B", (i,j), (k,m), False, False, None))        
                else:
                    l.append(mo.Move("B", (i,j), (k,m), True, False, None)) 
                    break
            else:
                break
        #nach unten links
        m = j
        for k in range(i-1, -1, -1): 
            m -= 1
            if m < 0 or k < 0:
                break
            if self.board[k][m].name == "F" or self.board[k][m].color == "b":
                if self.board[k][m].name == "F":        
                    l.append(mo.Move("B", (i,j), (k,m), False, False, None))
                else:
                    l.append(mo.Move("B", (i,j), (k,m), True, False, None))
                    break
            else:
                break
        #nach unten rechts
        m = j
        for k in range(i-1, -1, -1): 
            m += 1
            if m > 7 or k < 0:
                break
            if self.board[k][m].name == "F" or self.board[k][m].color == "b":
                if self.board[k][m].name == "F":        
                    l.append(mo.Move("B", (i,j), (k,m), False, False, None))
                else:
                    l.append(mo.Move("B", (i,j), (k,m), True, False, None))
                    break
            else:
                break

    def bpsmB(self, l: list, p: tuple):
        i = p[0]
        j = p[1]

        #nach oben links
        m = j
        for k in range(i + 1, 8, 1):
            m -= 1
            if m < 0 or k > 7:
                break
            if self.board[k][m].name == "F" or self.board[k][m].color == "w":
                if self.board[k][m].name == "F":        
                    l.append(mo.Move("B", (i,j), (k,m), False, False, None))
                else:
                    l.append(mo.Move("B", (i,j), (k,m), True, False, None))
                    break
            else:
                break
        #nach oben rechts
        m = j
        for k in range(i + 1, 8, 1):
            m += 1
            if m > 7 or k > 7:
                break
            if self.board[k][m].name == "F" or self.board[k][m].color == "w":
                if self.board[k][m].name == "F":        
                    l.append(mo.Move("B", (i,j), (k,m), False, False, None))
                else:
                    l.append(mo.Move("B", (i,j), (k,m), True, False, None)) 
                    break
            else:
                break
        #nach unten links
        m = j
        for k in range(i-1, -1, -1): 
            m -= 1
            if m < 0 or k < 0:
                break
            if self.board[k][m].name == "F" or self.board[k][m].color == "w":
                if self.board[k][m].name == "F":        
                    l.append(mo.Move("B", (i,j), (k,m), False, False, None))
                else:
                    l.append(mo.Move("B", (i,j), (k,m), True, False, None)) 
                    break
            else:
                break
        #nach unten rechts
        m = j
        for k in range(i-1, -1, -1): 
            m += 1
            if m > 7 or k < 0:
                break
            if self.board[k][m].name == "F" or self.board[k][m].color == "w":
                if self.board[k][m].name == "F":        
                    l.append(mo.Move("B", (i,j), (k,m), False, False, None))
                else:
                    l.append(mo.Move("B", (i,j), (k,m), True, False, None))
                    break
            else:
                break
    

    def wpsmQ(self, l: list, p: tuple):
        #schräg
        i = p[0]
        j = p[1]

        #nach oben links
        m = j
        for k in range(i + 1, 8, 1):
            m -= 1
            if m < 0 or k > 7:
                break
            if self.board[k][m].name == "F" or self.board[k][m].color == "b":
                if self.board[k][m].name == "F":
                    l.append(mo.Move("Q", (i,j), (k,m), False, False, None))
                else:
                    l.append(mo.Move("Q", (i,j), (k,m), True, False, None))
                    break
            else:
                break
        #nach oben rechts
        m = j
        for k in range(i + 1, 8, 1):
            m += 1
            if m > 7 or k > 7:
                break
            if self.board[k][m].name == "F" or self.board[k][m].color == "b":
                if self.board[k][m].name == "F":        
                    l.append(mo.Move("Q", (i,j), (k,m), False, False, None))
                else:
                    l.append(mo.Move("Q", (i,j), (k,m), True, False, None))
                    break
            else:
                break
        #nach unten links
        m = j
        for k in range(i-1, -1, -1): 
            m -= 1
            if m < 0 or k < 0:
                break
            if self.board[k][m].name == "F" or self.board[k][m].color == "b":
                if self.board[k][m].name == "F":        
                    l.append(mo.Move("Q", (i,j), (k,m), False, False, None))
                else:
                    l.append(mo.Move("Q", (i,j), (k,m), True, False, None))
                    break
            else:
                break
        #nach unten rechts
        m = j
        for k in range(i-1, -1, -1): 
            m += 1
            if m > 7 or k < 0:
                break
            if self.board[k][m].name == "F" or self.board[k][m].color == "b":
                if self.board[k][m].name == "F":        
                    l.append(mo.Move("Q", (i,j), (k,m), False, False, None))
                else:
                    l.append(mo.Move("Q", (i,j), (k,m), True, False, None))
                    break
            else:
                break
        #gerade
        for k in range(1, 8-i, 1): #Nach oben                      
            if self.board[i+k][j].name == "F" or self.board[i+k][j].color == "b":
                if self.board[i+k][j].name == "F":
                    l.append(mo.Move("Q", (i,j), (i+k, j), False, False, None))
                else:
                    l.append(mo.Move("Q", (i,j), (i+k, j), True, False, None))
                    break
            else:
                break

        for k in range(1, i + 1, 1): #Nach unten     
            if self.board[i-k][j].name == "F" or self.board[i-k][j].color == "b":
                if self.board[i-k][j].name == "F":
                    l.append(mo.Move("Q", (i,j), (i-k, j), False, False, None))
                else:
                    l.append(mo.Move("Q", (i,j), (i-k, j), True, False, None))
                    break
            else:
                break
                
        for k in range(1, 8-j, 1): #nach rechts
            if self.board[i][j+k].name == "F" or self.board[i][j+k].color == "b":
                if self.board[i][j+k].name == "F":
                    l.append(mo.Move("Q", (i,j), (i, j+k), False, False, None))
                else:
                    l.append(mo.Move("Q", (i,j), (i, j+k), True, False, None))
                    break
            else:
                break
        
        for k in range(1, j + 1, 1): #Nach links     
            if self.board[i][j-k].name == "F" or self.board[i][j-k].color == "b":
                if self.board[i][j-k].name == "F":
                    l.append(mo.Move("Q", (i,j), (i, j-k), False, False, None))
                else:
                    l.append(mo.Move("Q", (i,j), (i, j-k), True, False, None))
                    break
            else:
                break
    
    def bpsmQ(self, l: list, p: tuple):
        #schräg
        i = p[0]
        j = p[1]

        #nach oben links
        m = j
        for k in range(i + 1, 8, 1):
            m -= 1
            if m < 0 or k > 7:
                break
            if self.board[k][m].name == "F" or self.board[k][m].color == "w":
                if self.board[k][m].name == "F":
                    l.append(mo.Move("Q", (i,j), (k,m), False, False, None))        
                else:
                    l.append(mo.Move("Q", (i,j), (k,m), True, False, None)) 
                    break
            else:
                break
        #nach oben rechts
        m = j
        for k in range(i + 1, 8, 1):
            m += 1
            if m > 7 or k > 7:
                break
            if self.board[k][m].name == "F" or self.board[k][m].color == "w":
                if self.board[k][m].name == "F":        
                    l.append(mo.Move("Q", (i,j), (k,m), False, False, None))
                else:
                    l.append(mo.Move("Q", (i,j), (k,m), True, False, None)) 
                    break
            else:
                break
        #nach unten links
        m = j
        for k in range(i-1, -1, -1): 
            m -= 1
            if m < 0 or k < 0:
                break
            if self.board[k][m].name == "F" or self.board[k][m].color == "w":
                if self.board[k][m].name == "F":        
                    l.append(mo.Move("Q", (i,j), (k,m), False, False, None))
                else:
                    l.append(mo.Move("Q", (i,j), (k,m), True, False, None))
                    break
            else:
                break
        #nach unten rechts
        m = j
        for k in range(i-1, -1, -1): 
            m += 1
            if m > 7 or k < 0:
                break
            if self.board[k][m].name == "F" or self.board[k][m].color == "w":
                if self.board[k][m].name == "F":        
                    l.append(mo.Move("Q", (i,j), (k,m), False, False, None))
                else:
                    l.append(mo.Move("Q", (i,j), (k,m), True, False, None)) 
                    break
            else:
                break
        #gerade
        for k in range(1, 8-i, 1): #Nach oben                      
            if self.board[i+k][j].name == "F" or self.board[i+k][j].color == "w":
                if self.board[i+k][j].name == "F":
                    l.append(mo.Move("Q", (i,j), (i+k, j), False, False, None))
                else:
                    l.append(mo.Move("Q", (i,j), (i+k, j), True, False, None))
                    break
            else:
                break

        for k in range(1, i + 1, 1): #Nach unten     
            if self.board[i-k][j].name == "F" or self.board[i-k][j].color == "w":
                if self.board[i-k][j].name == "F":
                    l.append(mo.Move("Q", (i,j), (i-k, j), False, False, None))
                else:
                    l.append(mo.Move("Q", (i,j), (i-k, j), True, False, None))
                    break
            else:
                break
                
        for k in range(1, 8-j, 1): #nach rechts
            if self.board[i][j+k].name == "F" or self.board[i][j+k].color == "w":
                if self.board[i][j+k].name == "F":
                    l.append(mo.Move("Q", (i,j), (i, j+k), False, False, None))
                else:
                    l.append(mo.Move("Q", (i,j), (i, j+k), True, False, None))
                    break
            else:
                break
        
        for k in range(1, j + 1, 1): #Nach links     
            if self.board[i][j-k].name == "F" or self.board[i][j-k].color == "w":
                if self.board[i][j-k].name == "F":
                    l.append(mo.Move("Q", (i,j), (i, j-k), False, False, None))
                else:
                    l.append(mo.Move("Q", (i,j), (i, j-k), True, False, None))
                    break
            else:
                break
    
    def wpsmK(self, l: list, p: tuple):
        i = p[0]
        j = p[1]
        if i+1 <= 7:
            # 1, -1
            if j-1 >= 0:
                if self.board[i+1][j-1].name == "F":
                    l.append(mo.Move("K", (i,j), (i+1, j-1), False, False, None))
                if self.board[i+1][j-1].color == "b":
                    l.append(mo.Move("K", (i,j), (i+1, j-1), True, False, None))
            # 1, 0
            if self.board[i+1][j].name == "F":
                l.append(mo.Move("K", (i,j), (i+1, j), False, False, None))
            if self.board[i+1][j].color == "b":
                l.append(mo.Move("K", (i,j), (i+1, j), True, False, None))
            # 1, 1
            if j+1 <= 7:
                if self.board[i+1][j+1].name == "F":
                    l.append(mo.Move("K", (i,j), (i+1, j+1), False, False, None))
                if self.board[i+1][j+1].color == "b":
                    l.append(mo.Move("K", (i,j), (i+1, j+1), True, False, None))
        # 0, 1
        if j+1 <= 7:
            if self.board[i][j+1].name == "F":
                l.append(mo.Move("K", (i,j), (i, j+1), False, False, None))
            if self.board[i][j+1].color == "b":
                l.append(mo.Move("K", (i,j), (i, j+1), True, False, None))
        # 0, -1
        if j-1 >= 0:
            if self.board[i][j-1].name == "F":
                l.append(mo.Move("K", (i,j), (i, j-1), False, False, None))
            if self.board[i][j-1].color == "b":
                l.append(mo.Move("K", (i,j), (i, j-1), True, False, None))
        if i-1 >= 0:
            if j+1 <= 7:
                # -1, 1
                if self.board[i-1][j+1].name == "F":
                    l.append(mo.Move("K", (i,j), (i-1, j+1), False, False, None))
                if self.board[i-1][j+1].color == "b":
                    l.append(mo.Move("K", (i,j), (i-1, j+1), True, False, None))
            # -1, 0
            if self.board[i-1][j].name == "F":
                l.append(mo.Move("K", (i,j), (i-1, j), False, False, None))
            if self.board[i-1][j].color == "b":
                l.append(mo.Move("K", (i,j), (i-1, j), True, False, None))
            # -1, -1
            if j-1 >= 0:
                if self.board[i-1][j-1].name == "F":
                    l.append(mo.Move("K", (i,j), (i-1, j-1), False, False, None))
                if self.board[i-1][j-1].color == "b":
                    l.append(mo.Move("K", (i,j), (i-1, j-1), True, False, None))

    def bpsmK(self, l: list, p: tuple):
        i = p[0]
        j = p[1]
        if i+1 <= 7:
            # 1, -1
            if j-1 >= 0:
                if self.board[i+1][j-1].name == "F":
                    l.append(mo.Move("K", (i,j), (i+1, j-1), False, False, None))
                if self.board[i+1][j-1].color == "w":
                    l.append(mo.Move("K", (i,j), (i+1, j-1), True, False, None))
            # 1, 0
            if self.board[i+1][j].name == "F":
                l.append(mo.Move("K", (i,j), (i+1, j), False, False, None))
            if self.board[i+1][j].color == "w":
                l.append(mo.Move("K", (i,j), (i+1, j), True, False, None))
            # 1, 1
            if j+1 <= 7:
                if self.board[i+1][j+1].name == "F":
                    l.append(mo.Move("K", (i,j), (i+1, j+1), False, False, None))
                if self.board[i+1][j+1].color == "w":
                    l.append(mo.Move("K", (i,j), (i+1, j+1), True, False, None))
        # 0, 1
        if j+1 <= 7:
            if self.board[i][j+1].name == "F":
                l.append(mo.Move("K", (i,j), (i, j+1), False, False, None))
            if self.board[i][j+1].color == "w":
                l.append(mo.Move("K", (i,j), (i, j+1), True, False, None))
        # 0, -1
        if j-1 >= 0:
            if self.board[i][j-1].name == "F":
                l.append(mo.Move("K", (i,j), (i, j-1), False, False, None))
            if self.board[i][j-1].color == "w":
                l.append(mo.Move("K", (i,j), (i, j-1), True, False, None))
        if i-1 >= 0:
            if j+1 <= 7:
                # -1, 1
                if self.board[i-1][j+1].name == "F":
                    l.append(mo.Move("K", (i,j), (i-1, j+1), False, False, None))
                if self.board[i-1][j+1].color == "w":
                    l.append(mo.Move("K", (i,j), (i-1, j+1), True, False, None))
            # -1, 0
            if self.board[i-1][j].name == "F":
                l.append(mo.Move("K", (i,j), (i-1, j), False, False, None))
            if self.board[i-1][j].color == "w":
                l.append(mo.Move("K", (i,j), (i-1, j), True, False, None))
            # -1, -1
            if j-1 >= 0:
                if self.board[i-1][j-1].name == "F":
                    l.append(mo.Move("K", (i,j), (i-1, j-1), False, False, None))
                if self.board[i-1][j-1].color == "w":
                    l.append(mo.Move("K", (i,j), (i-1, j-1), True, False, None))

    def wcheckchecker(self):
        i = self.wK[0]
        j = self.wK[1]
        
        #black Pawn right and left
        if i+1 <= 7:
            if j+1 <= 7 and self.board[i+1][j+1].name == "P" and self.board[i+1][j+1].color == "b":
                return True
            if j-1 >= 0 and self.board[i+1][j-1].name == "P" and self.board[i+1][j-1].color == "b":
                return True
            
        #nach oben links
        m = j
        for k in range(i + 1, 8, 1):
            m -= 1
            if m < 0 or k > 7:
                break
            if (self.board[k][m].name == "B" or self.board[k][m].name == "Q") and self.board[k][m].color == "b":
                return True
            if self.board[k][m].color != " ":
                break
            
        #nach oben rechts
        m = j
        for k in range(i + 1, 8, 1):
            m += 1
            if m > 7 or k > 7:
                break
            if (self.board[k][m].name == "B" or self.board[k][m].name == "Q") and self.board[k][m].color == "b":
                return True
            if self.board[k][m].color != " ":
                break

        #nach unten links
        m = j
        for k in range(i-1, -1, -1): 
            m -= 1
            if m < 0 or k < 0:
                break
            if (self.board[k][m].name == "B" or self.board[k][m].name == "Q") and self.board[k][m].color == "b":
                return True
            if self.board[k][m].color != " ":
                break

        #nach unten rechts
        m = j
        for k in range(i-1, -1, -1): 
            m += 1
            if m > 7 or k < 0:
                break
            if (self.board[k][m].name == "B" or self.board[k][m].name == "Q") and self.board[k][m].color == "b":
                return True
            if self.board[k][m].color != " ":
                break
            
        #gerade
        for k in range(i+1, 8, 1): #Nach oben                      
            if k > 7:
                break
            if (self.board[k][j].name == "R" or self.board[k][j].name == "Q") and self.board[k][j].color == "b":
                return True
            if self.board[k][j].color != " ":
                break

        for k in range(i-1, -1, -1): #Nach unten     
            if k < 0:
                break
            if (self.board[k][j].name == "R" or self.board[k][j].name == "Q") and self.board[k][j].color == "b":
                return True
            if self.board[k][j].color != " ":
                break
                
        for k in range(j+1, 8, 1): #nach rechts
            if k > 7:
                break
            if (self.board[i][k].name == "R" or self.board[i][k].name == "Q") and self.board[i][k].color == "b":
                return True
            if self.board[i][k].color != " ":
                break
        
        for k in range(j-1, -1, -1): #Nach links     
            if k < 0:
                break
            if (self.board[i][k].name == "R" or self.board[i][k].name == "Q") and self.board[i][k].color == "b":
                return True
            if self.board[i][k].color != " ":
                break
        #Knight:
        #1 -2
        if i+1 <= 7:      
            if j-2 >= 0:
                if self.board[i+1][j-2].name == "N" and self.board[i+1][j-2].color == "b":
                    return True

        #2 -1
        if i+2 <= 7:      
            if j-1 >= 0:
                if self.board[i+2][j-1].name == "N" and self.board[i+2][j-1].color == "b":
                    return True
        #2 1
        if i+2 <= 7:      
            if j+1 <= 7:
                if self.board[i+2][j+1].name == "N" and self.board[i+2][j+1].color == "b":
                    return True
        #1 2
        if i+1 <= 7:      
            if j+2 <= 7:
                if self.board[i+1][j+2].name == "N" and self.board[i+1][j+2].color == "b":
                    return True
        #-1 2
        if i-1 >= 0:      
            if j+2 <= 7:
                if self.board[i-1][j+2].name == "N" and self.board[i-1][j+2].color == "b":
                    return True
        #-2 1
        if i-2 >= 0:      
            if j+1 <= 7:
                if self.board[i-2][j+1].name == "N" and self.board[i-2][j+1].color == "b":
                    return True
        #-2 -1
        if i-2 >= 0:      
            if j-1 >= 0:
                if self.board[i-2][j-1].name == "N" and self.board[i-2][j-1].color == "b":
                    return True
        #-1 -2
        if i-1 >= 0:      
            if j-2 >= 0:
                if self.board[i-1][j-2].name == "N" and self.board[i-1][j-2].color == "b":
                    return True
                
        return False

    def bcheckchecker(self):
        i = self.bK[0]
        j = self.bK[1]
        
        #black Pawn right and left
        if i-1 >= 0:
            if j+1 <= 7 and self.board[i-1][j+1].name == "P" and self.board[i-1][j+1].color == "w":
                return True
            if j-1 >= 0 and self.board[i-1][j-1].name == "P" and self.board[i-1][j-1].color == "w":
                return True
            
        #nach oben links
        m = j
        for k in range(i + 1, 8, 1):
            m -= 1
            if m < 0 or k > 7:
                break
            if (self.board[k][m].name == "B" or self.board[k][m].name == "Q") and self.board[k][m].color == "w":
                return True
            if self.board[k][m].color != " ":
                break
            
        #nach oben rechts
        m = j
        for k in range(i + 1, 8, 1):
            m += 1
            if m > 7 or k > 7:
                break
            if (self.board[k][m].name == "B" or self.board[k][m].name == "Q") and self.board[k][m].color == "w":
                return True
            if self.board[k][m].color != " ":
                break

        #nach unten links
        m = j
        for k in range(i-1, -1, -1): 
            m -= 1
            if m < 0 or k < 0:
                break
            if (self.board[k][m].name == "B" or self.board[k][m].name == "Q") and self.board[k][m].color == "w":
                return True
            if self.board[k][m].color != " ":
                break

        #nach unten rechts
        m = j
        for k in range(i-1, -1, -1): 
            m += 1
            if m > 7 or k < 0:
                break
            if (self.board[k][m].name == "B" or self.board[k][m].name == "Q") and self.board[k][m].color == "w":
                return True
            if self.board[k][m].color != " ":
                break
            
        #gerade
        for k in range(i+1, 8, 1): #Nach oben                      
            if k > 7:
                break
            if (self.board[k][j].name == "R" or self.board[k][j].name == "Q") and self.board[k][j].color == "w":
                return True
            if self.board[k][j].color != " ":
                break

        for k in range(i-1, -1, -1): #Nach unten     
            if k < 0:
                break
            if (self.board[k][j].name == "R" or self.board[k][j].name == "Q") and self.board[k][j].color == "w":
                return True
            if self.board[k][j].color != " ":
                break
                
        for k in range(j+1, 8, 1): #nach rechts
            if k > 7:
                break
            if (self.board[i][k].name == "R" or self.board[i][k].name == "Q") and self.board[i][k].color == "w":
                return True
            if self.board[i][k].color != " ":
                break
        
        for k in range(j-1, -1, -1): #Nach links     
            if k < 0:
                break
            if (self.board[i][k].name == "R" or self.board[i][k].name == "Q") and self.board[i][k].color == "w":
                return True
            if self.board[i][k].color != " ":
                break
        #Knight:
        #1 -2
        if i+1 <= 7:      
            if j-2 >= 0:
                if self.board[i+1][j-2].name == "N" and self.board[i+1][j-2].color == "w":
                    return True

        #2 -1
        if i+2 <= 7:      
            if j-1 >= 0:
                if self.board[i+2][j-1].name == "N" and self.board[i+2][j-1].color == "w":
                    return True
        #2 1
        if i+2 <= 7:      
            if j+1 <= 7:
                if self.board[i+2][j+1].name == "N" and self.board[i+2][j+1].color == "w":
                    return True
        #1 2
        if i+1 <= 7:      
            if j+2 <= 7:
                if self.board[i+1][j+2].name == "N" and self.board[i+1][j+2].color == "w":
                    return True
        #-1 2
        if i-1 >= 0:      
            if j+2 <= 7:
                if self.board[i-1][j+2].name == "N" and self.board[i-1][j+2].color == "w":
                    return True
        #-2 1
        if i-2 >= 0:      
            if j+1 <= 7:
                if self.board[i-2][j+1].name == "N" and self.board[i-2][j+1].color == "w":
                    return True
        #-2 -1
        if i-2 >= 0:      
            if j-1 >= 0:
                if self.board[i-2][j-1].name == "N" and self.board[i-2][j-1].color == "w":
                    return True
        #-1 -2
        if i-1 >= 0:      
            if j-2 >= 0:
                if self.board[i-1][j-2].name == "N" and self.board[i-1][j-2].color == "w":
                    return True
                
        return False

    def wpossibleMoves(self):
        l = []
        for i in range(7, -1, -1):
            for j in range(7, -1, -1):
                c = self.board[i][j]
                if c.color == "w":
                    if c.name == "P":
                        self.wpsmP(l, (i,j))
                    elif c.name == "R":
                        self.wpsmR(l, (i,j))
                    elif c.name == "N":
                        self.wpsmN(l, (i,j))
                    elif c.name == "B":
                        self.wpsmB(l, (i,j))
                    elif c.name == "Q":
                        self.wpsmQ(l, (i,j))
                    elif c.name == "K":
                        self.wpsmK(l, (i,j))
        t = []
        for k in range(len(l)):
            a = co.deepcopy(self)
            a.makeMove(l[k])
            if a.wcheckchecker():
                t.append(k)

        for k in range(len(t) -1 , -1, -1):
            l.pop(t[k])
        
        for x in l:
            a = co.deepcopy(self)
            a.makeMove(x)
            if a.bcheckchecker():
                x.check = True
                     
        return l
    
    def bpossibleMoves(self):
        l = []
        for i in range(8):
            for j in range(8):
                c = self.board[i][j]
                if c.color == "b":
                    if c.name == "P":
                        self.bpsmP(l, (i,j))
                    elif c.name == "R":
                        self.bpsmR(l, (i,j))
                    elif c.name == "N":
                        self.bpsmN(l, (i,j))
                    elif c.name == "B":
                        self.bpsmB(l, (i,j))
                    elif c.name == "Q":
                        self.bpsmQ(l, (i,j))
                    elif c.name == "K":
                        self.bpsmK(l, (i,j))
        
        t = []
        for k in range(len(l)):
            a = co.deepcopy(self)
            a.makeMove(l[k])
            if a.bcheckchecker():
                t.append(k)

        for k in range(len(t) -1 , -1, -1):
            l.pop(t[k])

        for k in range(len(l)):
            a = co.deepcopy(self)
            a.makeMove(l[k])
            if a.wcheckchecker():
                l[k].check = True
        return l
    
    def possibleMoves(self):
        if self.ac == "w":
            self.psm = self.wpossibleMoves()
            """
            if self.psm == []:
                if self.history == []:
                    #print("Checkmate: Weiß hat gewonnen")
                    return
                if self.history[-1].check == True:
                    pass
                    #print("Checkmate: Schwarz hat gewonnen")
                else:
                    pass
                    #print("Stalemate!")
                    """
        else:
            self.psm = self.bpossibleMoves()
            """
            if self.psm == []:
                if self.history == []:
                    #print("Checkmate: Weiß hat gewonnen")
                    return
                if self.history[-1][1].check == True:
                    #print("Checkmate: Weiß hat gewonnen")
                    pass
                else:
                    #print("Stalemate!")
                    pass
                    """
                    

        


