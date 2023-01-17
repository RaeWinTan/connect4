import random
import sys


class SearchNode:
    def __init__(self, board,turn, depth):
        columns = 7
        self.turn = turn
        self.board = board #current board is the board given by the previous player
        self.depth = depth
        self.neighbors = [False for i in range(columns * 2)]
        self.val = 0 #this val is either -10, 0, 10, determine who win and who loses
        self.bestMove = 0 #between range [-3,3], grade max connection
    def toString(self):
        s = "\n"
        s+="turn"+str(self.turn)+"\n"
        s+="depth"+str(self.depth)+"\n"
        s+="val"+str(self.val)+"\n"
        s+=board_string(self.board)
        return s

class Computer:
    #root is the previous turn
    def __init__(self, board, turn, level):
        #board givem is the board as a result of the user's choice 
        self.root = SearchNode(board.copy(), turn, 1)
        self.computer_turn = turn
        self.level = level
        self.create_tree()
        self.print_tree()
        
    def create_tree(self):
        queue = []
        depth = 1
        queue.append(self.root)
        howDeep = 6
        if(self.level == 1):
            howDeep = 1
        elif(self.level == 2 or self.level == 3):
            howDeep = 3
        #building tree by BFS
        while(depth < howDeep):
            depth+=1
            currSize = len(queue) 
            while(currSize > 0):
                currNode = queue.pop(0)
                if not isinstance(currNode, bool):
                    ns = self.generate_neighbours(currNode.board, currNode.turn, depth)
                    currNode.neighbors = ns
                    for s in ns: queue.append(s)
                currSize-=1
        ## now recursively calculate val from bottom up
        self.updateNodeVal(self.root)
        #self.print_tree() ##debug purposes
        
    #return a list of len 14 of posibible next search node 
    def generate_neighbours(self, board, turn, depth):
        columns = 7
        return  [SearchNode(apply_move(board, turn, i%columns , i >= columns), inverseWhoPlayed(turn), depth) if(check_move(board, turn, i%columns, i >= columns)) else False for i in range(columns * 2)]
    def getComputerMove(self): #calls this in main
        columns = 7     
        if(self.level==1):
            l = []
            posible = self.generate_neighbours(self.root.board, self.root.turn, 2)
            #just random pick from all valid neighbours
            for i in range(len(posible)):
                if not isinstance(posible[i], bool):
                    l.append(i)
            r = random.randrange(len(l))
            return (  l[r]%columns, l[r]>= columns  ) 
        maxSoFar = -15
        #finding the best move amounst the direct neighbours
        for i in range(len(self.root.neighbors)):
            if not isinstance(self.root.neighbors[i], bool):
                if(self.root.neighbors[i].val > maxSoFar):
                    maxSoFar = self.root.neighbors[i].val 
        l = []
        for i in range(len(self.root.neighbors)):
            if not isinstance(self.root.neighbors[i], bool):
                if maxSoFar == self.root.neighbors[i].val:
                    l.append((i, self.root.neighbors[i]))
        bestSoFar = -4
        if(self.level == 2): #amongst the neighbour just pic the best move  
            return [(i[0]%columns, i[0] >= columns) for i in l][random.randrange(len(l))]
        for i in range(len(l)): bestSoFar = max(bestSoFar, l[i][1].bestMove)
        a = []
        #further filter moves by getting the neighbours with the best grades(high connectivity compared to adversary)
        for e in l:
            if(e[1].bestMove == bestSoFar): a.append(e[0])
        
        r = random.randrange(len(a))
        #for level 3 and above 
        return (a[r]%columns, a[r] >= columns)#from index, decide put which column and pop?
    
    def print_tree(self):#for debug purposes
        f = open("output.txt","w+")
        queue = []
        parentSet = set() ##debug
        childParentDict = dict() #debug
        depth = 1
        queue.append(self.root)
        while(len(queue) > 0):
            currSize = len(queue)
            f.write("\n--------"+"depth : " +str(depth)+"-------\n")
            while(currSize > 0):
                currNode = queue.pop(0)
                if(depth > 1 and childParentDict[currNode] in parentSet):
                    f.write("parent is : \n")
                    f.write(childParentDict[currNode].toString())
                    parentSet.remove(childParentDict[currNode])
                f.write(currNode.toString())
                for node in currNode.neighbors:
                    if not isinstance(node, bool):
                        parentSet.add(currNode)#debug
                        queue.append(node)
                        childParentDict[node] = currNode#debug
                
                currSize-=1
            depth+=1
        f.close()
    
    def updateNodeVal(self,r):
        vic = check_victory(r.board, inverseWhoPlayed(r.turn))
        if (len(set(r.neighbors)) == 1 or 0<vic<3): #all is false or we found a winner
            if (vic == self.computer_turn):#computer won
                r.val = 10
                r.bestMove = 4
                return (4, 10)
            elif (vic == inverseWhoPlayed(self.computer_turn)): #human won
                r.val = -10
                r.bestMove = -4
                return (-4, -10)
            else: 
                r.val = 0
                r.bestMove = self.maxConsecutive(r)
                return (r.bestMove,0)
        if(r.turn == self.computer_turn):#if r.turn == computer, use max to calculate 
            maxSoFar = -15
            bestMoveSoFar = float("-inf")
            for sn in r.neighbors:
                if not isinstance(sn, bool):
                    valTup = self.updateNodeVal(sn)
                    bestMoveSoFar = max(valTup[0], self.maxConsecutive(sn))
                    maxSoFar = max(valTup[1], maxSoFar)
            r.bestMove = bestMoveSoFar
            r.val = maxSoFar 
            return (bestMoveSoFar, maxSoFar)
        else:#if r.turn == human, use min to calculate 
            minSoFar = 15
            bestMoveSoFar = float("inf")
            for sn in r.neighbors:
                if not isinstance(sn, bool):
                    valTup = self.updateNodeVal(sn)
                    bestMoveSoFar = min(valTup[0], self.maxConsecutive(sn))
                    minSoFar = min(valTup[1], minSoFar)
            r.bestMove = bestMoveSoFar
            r.val = minSoFar
            return (bestMoveSoFar, minSoFar)
    def maxConsecutive(self, sn):#calculate the grading for the board 
        """
        dp[i] = [consecutive row sum , consecutive col sum, consecutive leftDiag sum, consecutive rightDiag sum]
        n is the number of rows the board
        """
        columns = 7
        dp = dict()
        for i in range(len(sn.board)):
            #no need to compute for 0
            if (sn.board[i] == 0): continue
            dp[i] = [1 for j in range(4)] #initialize the dp array element
            #calculate row_consequitive look left
            if (i - 1 >= 0 and (i-1)//columns == i//columns and sn.board[i] == sn.board[i-1]):dp[i][0] = dp[i-1][0] + 1
            #calculate col_consequitive look up
            if (i - columns >= 0 and sn.board[i] == sn.board[i-columns]): dp[i][1] = dp[i-columns][1] + 1
            #calculate leftDiag_consequitive //look 1 left 1 up
            if (i - columns - 1 >= 0 and i//columns - 1 == (i - columns - 1)//columns and sn.board[i] == sn.board[i-columns-1]): dp[i][2] = dp[i-columns-1][2] + 1
            #calculate rightDiag_consequitive //look 1 right 1 up
            if (i - columns + 1 > 0 and i//columns - 1 == (i - columns + 1)//columns and sn.board[i] == sn.board[i-columns+1]): dp[i][3] = dp[i-columns+1][3] + 1
        turn_points = [0,0,0] #first element is just to pad the array by one element
        for i in sorted(dp.keys(), reverse=True):#only add points when it is above 2
            #count row points
            if (((i + 1)//columns != (i)//columns) or ( (i+1)//columns == i//columns and not ((i+1) in dp and sn.board[i] == sn.board[i+1]) )):
                turn_points[sn.board[i]] += addPoints(dp.get(i)[0]) #adding the total consequitive in rows  
            #count col points
            if ( ( i + columns >= len(sn.board) ) or not((i+columns) in dp and sn.board[i] == sn.board[i+columns]  ) ):
                turn_points[sn.board[i]] += addPoints(dp.get(i)[1])
            #count left diag points
            if (i >= len(sn.board) - columns) or (i//columns + 1 == (i + columns + 1)//columns and not((i+columns + 1) in dp and sn.board[i] == sn.board[i+columns+1])):
                turn_points[sn.board[i]] += addPoints(dp.get(i)[2])
            #count right diag points
            if (i >= len(sn.board) - columns) or (i//columns + 1 == (i + columns - 1)//columns and not((i+columns - 1) in dp and sn.board[i] == sn.board[i+columns-1])):
                turn_points[sn.board[i]] += addPoints(dp.get(i)[3])
        #this points is in favour of computer 
        return turn_points[self.computer_turn] - turn_points[inverseWhoPlayed(self.computer_turn)]
        
# only add when above 2
def addPoints(n):
    if(n>=2): 
        if(n == 2): return 10
        if n == 3: return 100
        else: return n*10
    return 0     

def check_move(board, turn, col, pop):
    #7*i + col
    columns = 7
    if not isinstance(pop, bool): return False
    n = int(len(board)/columns) #no of rows
    if not pop:
        if board[columns*(n-1) + col] != 0 : return False
        if col < 0 or col > columns - 1: return False
    else:
        if board[col] != turn: return False
    return True

def apply_move(board, turn, col, pop):
    columns = 7
    tmp_board = board.copy()
    if pop:
        i = 0
        for i in range(col, len(tmp_board), columns):
            if i+columns >= len(tmp_board): tmp_board[i] = 0
            else: tmp_board[i] = tmp_board[i+columns]
    else:
        i = col
        while(tmp_board[i] != 0): i += columns
        tmp_board[i] = turn 
    return tmp_board

def inverseWhoPlayed(who):
    if(who == 1): return 2
    else: return 1

def check_victory(board, who_played):
    """
    dp[i] = [consecutive row sum , consecutive col sum, consecutive leftDiag sum, consecutive rightDiag sum]
    n is the number of rows the board
    """
    columns = 7
    win = [0, False, False]
    dp = dict()
    for i in range(len(board)):
        #no need to compute for 0
        if (board[i] == 0): continue
        dp[i] = [1 for j in range(4)] #initialize the dp array element
        #calculate row_consequitive look left
        if (i - 1 >= 0 and (i-1)//columns == i//columns and board[i] == board[i-1]):dp[i][0] = dp[i-1][0] + 1
        #calculate col_consequitive look up
        if (i - columns >= 0 and board[i] == board[i-columns]): dp[i][1] = dp[i-columns][1] + 1
        #calculate leftDiag_consequitive //look 1 left 1 up
        if (i - columns - 1 >= 0 and i//columns - 1 == (i - columns - 1)//columns and board[i] == board[i-columns-1]): dp[i][2] = dp[i-columns-1][2] + 1
        #calculate rightDiag_consequitive //look 1 right 1 up
        if (i - columns + 1 > 0 and i//columns - 1 == (i - columns + 1)//columns and board[i] == board[i-columns+1]): dp[i][3] = dp[i-columns+1][3] + 1
    for i in dp:
        for j in range(4):
            if(dp[i][j] >= 4):
                win[board[i]] = True
    if(win[inverseWhoPlayed(who_played)]): return inverseWhoPlayed(who_played)
    if(win[who_played]): return who_played
    return 0

def computer_move(b, turn, level):
    com = Computer(b, turn, level)
    #com.print_tree()
    comMove = com.getComputerMove()
    return (comMove[0], comMove[1])

def board_string(board):
    columns = 7
    ans = "\n"
    for row in range(len(board)//columns - 1, -1 , -1):
        for col in range(columns):
            ans+=str(board[columns*row + col])+" "
        ans+="\n" 
    return ans

def display_board(board):
    #7*row + col
    columns = 7 
    for row in range(len(board)//columns - 1, -1 , -1):
        for col in range(columns):
            print(board[columns*row + col], end=" ")
        if(row != 0): print() 
    
def help():
    print("h - help")
    print("p - play")
    print("s - set rows")
    print("d - set difficulty")
    print("f - set player 1")
    print("e - press e anywhere to exit")
    

def getUserMove(b, computer_turn):
    pop = "start with false"
    col = -1
    while(not check_move(b, inverseWhoPlayed(computer_turn), col, pop)):
        i = input("Choose column 0 - 6")
        while not (i.isnumeric() and 0<=int(i)<=6 ):
            if i == "e": sys.exit()
            i = input("Choose column 0 - 6")
        col = int(i)
        #check if it can be applied 
        i = input("Pop? y/n")
        while i not in ["y", "n"] or i == "e":
            if i == "e": sys.exit()
            i = input("Pop? y/n")
        pop = True if (i == "y") else False
        if not check_move(b, inverseWhoPlayed(computer_turn), col, pop):
            print("INVALID MOVE")
    return (col, pop)

def play(rows, computer_turn, difficulty):
    #initialise board 
    print("difficulty  ", difficulty, ", computer_turn ", computer_turn, ", rows ", rows)
    b = initBoard(rows)
    prev = 2
    if(computer_turn == 1):
        prev = 1
        print("computer thinking of a move")
        c_move = computer_move(b,computer_turn, difficulty)
        b = apply_move(b, computer_turn, c_move[0], c_move[1])
    display_board(b)
    print()
    while(not check_victory(b, prev)):
        userChoice = getUserMove(b, computer_turn)
        b = apply_move(b, inverseWhoPlayed(computer_turn), userChoice[0], userChoice[1])
        display_board(b)
        print()
        #check if user win here
        vic = check_victory(b, inverseWhoPlayed(computer_turn)) 
        if(0<vic <3):
            prev = inverseWhoPlayed(computer_turn)
            break
        print("computer thinking of a move")
        c_move = computer_move(b, computer_turn, difficulty)
        b = apply_move(b, computer_turn, c_move[0], c_move[1])
        print("Computer move : col = ", str(c_move[0]), " pop = ", str(c_move[1]))
        display_board(b)
        prev = computer_turn
        print()
    if(check_victory(b, prev) == computer_turn):    
        print("COMPUTER WIN")
    else: print("YOU WIN")
      
def set_firstPlayer():
    computer_turn = 2
    i = input("Set who is player 1 human/computer choose: h/c")
    while(i not in ["h", "c"]):
        if (i=="e"): sys.exit()
        else: i = input("Set who is player 1 human/computer choose: h/c")
    if (i == "h"):computer_turn = 2
    else:computer_turn = 1
    return computer_turn
def set_difficulty():
    difficulty = 1
    i = input("Set difficulty choose 1 - 4")
    while (not (i.isnumeric() and int(i) in range(1,5))):
        if(i== "e"): sys.exit()
        i = input("Set difficulty choose 1 - 4")
    difficulty = int(i)
    return difficulty


def set_rows():
    
    i = input("Set number of rows between 6 - 15(inclusive)")
    while (not(i.isnumeric() and 5<int(i)<16)):
        if(i == "e"): sys.exit()
        i = input("Set number of rows between 6 - 15(inclusive)")
    return int(i)


     
def initBoard(rows):
    return [0 for i in range(rows*7)]

def menu():
    rows = 6
    computer_turn = 2
    difficulty = 1
    while(True):
        i = input("Type Command - Press h for help: ")
        if i == "s": rows = set_rows()
        elif(i) == "p": play(rows, computer_turn, difficulty)
        elif(i) == "f": computer_turn = set_firstPlayer()
        elif i == "d": difficulty = set_difficulty()
        elif i == "e": return
        else: help()


if __name__ == "__main__":        
    menu()
    

