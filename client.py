import argparse
import http.client
import urllib.parse
import game
import server

def parse_args():
    ''' Argument parser to extract command line arguments'''
    parser = argparse.ArgumentParser()

    parser.add_argument("host")
    parser.add_argument("port")
    parser.add_argument('x', type = int)
    parser.add_argument('y', type = int)

    arguments = parser.parse_args()

    return (arguments.host, arguments.port, arguments.x, arguments.y)


def create_connection(host, port, xco, yco):
    ''' Establishes connection with the input host and port, then fire at the input x and y coordinates'''

    # Establishes initial connection
    connection = http.client.HTTPConnection(host, port)

    # Creates arguments for the 'POST' request
    params = urllib.parse.urlencode({'x':xco, 'y':yco})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    connection.request("POST", '', params, headers)

    # Retrieves the server's response to the 'POST' request, then prints response and closes the connection
    response = connection.getresponse()
    print(response.status, response.reason)
    connection.close()

    # If initial request was valid, update the opponent board with a hit or miss
    if response.status == 200:
        hit = response.reason.split('=')
        game.update_opponent_board(hit[1], xco, yco)


def main():

    # Extract command line arguments
    host, port, x, y = parse_args()

    # Initialize connection with server
    create_connection(host, port, x, y)


if __name__ == "__main__":
    main()