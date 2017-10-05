import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import urllib.parse
import game

def parse_args():
    ''' Extracts command line arguments '''
    parser = argparse.ArgumentParser()

    parser.add_argument("port", type = int)
    parser.add_argument("file_name")

    arguments = parser.parse_args()

    return (arguments.port, arguments.file_name)

def format_output(file_name):
    ''' Formats a .txt file (containing a board) into a more appealing format for html display'''

    # Initializes input file, output text, and counter
    fin = open(file_name, 'r')
    output = "<html>"
    input_line = fin.readline()
    i = 9

    # Loops through every line in the input file
    while input_line:
        input_line = list(str(i) + input_line)  # splits input line into a list of chars
        input_line = " ".join(input_line)       # rejoins input line, now with spaces between the chars
        output += input_line + "<br>"           # adds a break to the end of the line, adds it to the output
        i -= 1                                  # i creates descending numbers, the y coordinates on the board
        input_line = fin.readline()             # gets the next line

    fin.close()
    # adds the bottom row of x coordinates to the output
    output += "- " + ' '.join(str(x) for x in range(10)) + "</html>"

    return output

class request_handler(BaseHTTPRequestHandler):
    ''' Creates a basic request handler that can handle HEAD, GET, and POST requests'''

    def set_headers(self):
        # sends basic response for HEAD and GET requests
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_HEAD(self):
        self.set_headers()

    def do_GET(self):
        self.set_headers()
        # Chooses which board to output, then encodes it
        if self.path == "/own_board.html":
            self.wfile.write(bytes(format_output(own_board.get_name()), "utf-8"))
        elif self.path == "/opponent_board.html":
            self.wfile.write(bytes(format_output(opponent_board.get_name()), "utf-8"))

    def do_POST(self):

        # decodes the POST request
        content_length = int(self.headers["Content-Length"])
        post_data = urllib.parse.parse_qs(self.rfile.read(content_length).decode("utf-8"))

        # Check that input coordinates are of type int, returns GONE error if invalid
        try:
            coordinates = (int(post_data['x'][0]), int(post_data['y'][0]))
        except ValueError:
            self.send_error(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            return

        # Check that input coordinates are within board bounds, sends BAD REQUEST error if invalid
        for i in range(2):
            if coordinates[i] < 0 or coordinates[i] > 9:
                self.send_error(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                return

        # Check that coordinates have not been used yet, sends GONE error if invalid
        if own_board.check_coordinates(coordinates[0], coordinates[1]):
            self.send_error(410)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            return

        # Making it this far indicates the coordinates are valid

        # Asks the board if these coordinates are a hit
        answer = own_board.check_hit(coordinates[0], coordinates[1])

        # if nothing sunk, returns the hit=0 or 1 messages
        if len(answer) == 1:
            result = "hit=" + str(answer)
        # else if something sunk, returns hit=1&sink= ship descriptor
        else:
            result = "hit=" + str(answer[0]) + "&sink=" + str(answer[1])
        self.send_response(200, result)
        self.send_header("Content-type", "text/html")
        self.end_headers()


def open_port(port):
    ''' Initializes a server that will run until a keyboard interrupt (ctrl-c) forces an exit'''

    # retrieves address, creates a basic server with our custom handler, then prints the server info
    server_address = (socket.gethostbyname(socket.gethostname()), port)
    server = HTTPServer(server_address, request_handler)
    print("Server running on", server.socket.getsockname())

    # the server will listen until a keyboard interrupt
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    # closes server and prints exit statement
    server.server_close()
    print("\nExiting...")

def main():
    # creates a global instance of the input board, initializes server creation
    global own_board, opponent_board
    game.start()
    opponent_board = game.get_opponent_board()

    port, own_board = parse_args()
    own_board = game.Board(own_board)

    open_port(port)

if __name__ == "__main__":
    main()
