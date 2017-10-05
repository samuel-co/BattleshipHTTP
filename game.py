import os.path

class Board:

    def __init__(self, file_name):
        ''' initializes a board object, which contains its file name, a dictionary of ship sizes, and an array that
            reflects the contents of the file. The array allows for fast searching of the board without parsing through
            an entire file. Note that because files are read in top-to-bottom, while y-axis values ascend, the table was
            built with the x and y values switched, e.g. the coordinates 3,5 relate to current_board[5][3]. This allows
            board to be written to a file with no extra parsing, and coordinates to still be easily searched for in the array'''

        self.file_name = file_name
        self.current_board = [['_' for x in range(10)] for y in range(10)]  # creates a new 10 x 10 board
        self.ship_dict = {'C':4, 'B':3, 'R':2, 'S':2, 'D':1}                # key for ship sizes

        if not os.path.isfile(file_name):   # if this board is new it writes a new board file
            self.make_file()
        else:                               # else makes the board array match the file
            self.make_board()

    def write_file(self):
        ''' rewrites the txt file from the board array to reflect any update '''

        fout = open(self.file_name + ".tmp", 'w')

        for i in range(10):
            output_line = ''.join(self.current_board[9-i]) + '\n'
            fout.write(output_line)

        fout.close()
        os.rename(self.file_name + ".tmp", self.file_name)

    def make_file(self):
        ''' creates a new blank file for the opponent board '''

        fout = open(self.file_name, 'w')
        for i in range(10):
            fout.write("__________\n")
        fout.close()

    def make_board(self):
        ''' creates the board array to match the input file board state'''

        fin = open(self.file_name, 'r')
        for i in range(10):
            input_line = fin.readline().strip()
            self.current_board[9-i] = list(input_line)
        fin.close()

    def update_board(self, hit, yco, xco):
        # updates the opponent board for the client, based on whether a shot was a hit or a miss

        if hit == '0':
            self.current_board[xco][yco] = 'o'
        else:
            self.current_board[xco][yco] = 'x'
        self.write_file()

    def get_name(self):
        return self.file_name

    def check_coordinates(self, yco, xco):
        ''' checks if input coordinates have been fired upon yet, returns False if they have not been used'''

        if self.current_board[xco][yco] != 'x' and self.current_board[xco][yco] != 'o':
            return False
        else:
            return True

    def check_hit(self, yco, xco):
        ''' determines whether the shot hit a ship'''

        status = self.current_board[xco][yco]   # status reflects the value of the board at the coordinates fired upon

        # if the shot hit water then update the board, rewrite the file, and return a miss
        if status == '_':
            self.current_board[xco][yco] = 'o'
            self.write_file()
            return '0'
        # else if the shot hit a ship then update the board, rewrite the file, and check if the shot sunk the ship
        else:
            self.current_board[xco][yco] = 'x'
            self.write_file()
            # if the ship was sunk return a hit and the descriptor for the ship
            if self.check_sunk(yco, xco, status):
                return (1, status)
            # else if nothing sunk then just return a hit
            else:
                return '1'

    def check_sunk(self, yco, xco, status):
        ''' check whether a shot sunk a ship by determining if any possible zones still contain the ships descriptor '''

        search_radius = self.ship_dict[status] # the search readius is determined by the size of the ship

        # first we search along the x-axis for the ship
        # create the minimum and maximum xcoordinates to search for the ship
        min = xco - search_radius
        max = xco + search_radius + 1
        if min < 0: min = 0
        if max > 10: max = 10
        # if a zone still contains the ships descriptor then it hasn't sunk
        for i in range(min, max):
            if self.current_board[i][yco] == status:
                return False

        # next search along the y-axis for the ship
        min = yco - search_radius
        max = yco + search_radius + 1
        if min < 0: min = 0
        if max > 10: max = 10
        # if the ship is found, it still hasn't sunk
        for i in range(min, max):
            if self.current_board[xco][i] == status:
                return False

        # to reach this point no ship descriptor was found in the possible zones, so the ship was sunk
        return True

opponent_board = Board("opponent_board.txt")

def start():
    os.remove("opponent_board.txt")
    start_board = Board("opponent_board.txt")

def get_opponent_board():
    return opponent_board

def update_opponent_board(hit, xco, yco):
    opponent_board.update_board(hit, xco, yco)
