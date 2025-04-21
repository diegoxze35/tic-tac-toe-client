import sys  # modulo para recibir argumentos por terminal
from socket import socket, AF_INET, SOCK_STREAM  # Cosas necesarias para sockets TCP/IP
from pyfiglet import figlet_format  # para textos bonitos por terminal

"""
la función system es para ejecutar un comando en la terminal 
del sistema operativo y la variable name es para
obtener el nombre del sistema operativo donde se ejecuta
el script
"""
from os import system, name as os_name


# Función que limpia la terminal independientemente si se ejecuta en Windows o en un sistema UNIX
def cls():
    system('cls' if os_name == 'nt' else 'clear')


def update_board(b: list[list[str]], coordinates: tuple[int, int] = None, new_square: str = None) -> None:
    """
    Función que actualiza el tablero en cada turno
    :param b: El tablero, una matriz de strings
    :param coordinates: Las coordenadas del tablero donde se acutalizó una casilla
    :param new_square: El nuevo simbolo de la casilla que indican las coordenadas
    :return: None
    """

    """
    El método join de la clase string recibe una lista, la cual concatena con la cadena cada elemento de 
    esa lista separado por el valor de esa cadena.
    Ejemplo:
        my_str = '#'.join([str(i) for i in range(3)])
        my_str = 0#1#2#
    """
    colums_header = ''.join([f'  {i}' for i in range(1, len(b) + 1)])
    print(colums_header)
    if coordinates and new_square:
        x, y = coordinates
        b[x][y] = new_square
    for index, row in enumerate(b):
        print(f'{index + 1}' + ''.join(row))

"""
Ejecutar con python3 main.ip <ip> <puerto>
Ejemplo:
python3 main.ip 192.168.0.20 8090
"""
if __name__ == '__main__':
    server_ip: str
    port: int
    """
    Debe de recibirse 3 argumentos
    sys.argv[0] siempre es el nombre del script
    'main.py' en este caso
    """
    if len(sys.argv) == 3:
        server_ip = sys.argv[1]
        port = int(sys.argv[2])
    else:
        exit('Usage: python3 main.py <ip> <port>')  # Terminamos el programa con error si no se reciben los argumentos
    if port < 1024:  # Sabemos que no es recomendable usar puertos del sistema
        exit('Server port must be greater than 1024')

    # Instanciamos un socket y nos conectamos al servidor
    with socket(AF_INET, SOCK_STREAM) as s:
        s.setblocking(True)
        s.connect((server_ip, port))

        # Creamos un texto de consola con el título del juego
        title = figlet_format(text='Tic Tac Toe!', font='larry3d', width=90)
        print(title)
        print("I want to ...")
        option = str()
        while option != '1' and option != '2':
            print('1 = Create a game room')
            print('2 = Join a game room')
            option = input()
        if option == '1':
            level = str()
            while level != '1' and level != '2':
                print('Please select difficulty level:')
                print('1 = Easy')
                print('2 = Medium')
                level = input()
            square = str()
            while square != 'X' and square != 'O':
                print('Select your square')
                print('X')
                print('O')
                square = input()
            single_player = str()
            while single_player != '1' and single_player != '2':
                print('Players ... ')
                print(1)
                print(2)
                single_player = input()
            """
            Para esta práctica decidimos implementar el siguiente formato de mensajes,
            el cual es una tupla con una cadena y un diccionario de la siguiente manera
            
            ('CADENA QUE INTERPRETA EL SERVIDOR','argumento1','argumento2', ... )
            
            A excepción de las coordenadas para tiro, las cuales se envian como un entero
            truncado a 32 bits con signo
            
            Las respuestas del servidor tienen el mismo formato de mensajes,
            por lo que para finalizar la comunicación compararemos el valor
            de la cadena
            """
            command = f'GAME,{level},{square},{1 if single_player == '1' else 0}'
            n = 3 if int(level) == 1 else 5  # número de filas y columnas según la dificultad
            command_bytes: bytes = str(command).encode()
            # Enviamos el mensaje al servidor
            s.send(command_bytes)
        else:
            valid_code = False
            while not valid_code:
                print('Code ...')
                code = int(input())
                command = f'JOIN,{code},'
                command_bytes: bytes = str(command).encode()
                s.send(command_bytes)
                squares = s.recv(1)
                n = int.from_bytes(squares, byteorder='big', signed=True)
                valid_code = n > 0

        """
        El tablero es una matriz de canedas para saber que fila y columna se va a actualizar
        por las jugadas que haga el servidor o segundo jugador el codigo de abajo es equivalente a
        board = []
        for i in range(n):
            board.append([])
            for _ in range(n):
                board[i].append('-')    
        range(n) devuelve un objeto que representa una secuencia de 0 a n - 1, además es iterable
        """
        board = [[' - ' for _ in range(n)] for _ in range(n)]
        while True:
            message = s.recv(12).decode().split(',') #Mensajes siempre truncados a 12 bytes
            #print(message)
            match message[0]:
                case 'REDY':
                    cls()
                    update_board(board)
                case 'MOVE':
                    x = int(message[1])
                    y = int(message[2])
                    square = message[3]
                    cls()
                    update_board(board, (x, y), square)
                case 'WAIT':
                    print(f' Waiting for {message[1]} ')
                case 'TURN':
                    print(f'Your turn {message[3]} ... ')
                    x = None
                    y = None
                    are_integers = False
                    while not are_integers:
                        try:
                            x = int(input('X: '))
                            y = int(input('Y: '))
                            are_integers = True
                        except ValueError:
                            print('Enter a number')
                            are_integers = False
                    """
                    Es importante truncar los bytes de un mensaje para que no se leea más de un mensaje
                    a la vez con el método recv
                    """
                    assert s.send(x.to_bytes(length=32, byteorder='big', signed=True)) == 32  # Verificar que si se envian 32 bytes al servidor
                    assert s.send(y.to_bytes(length=32, byteorder='big', signed=True)) == 32
                    #s.send(f'{move[0]},{move[1]}'.encode())
                case 'INMV':
                    cls()
                    msg = 'out of range' if message[1] == 'NORANGE' else 'taken'
                    print(f'The square is {msg}')
                    update_board(board)
                case 'SHAC':  # Share code
                    cls()
                    print('Please share this code with someone to play')
                    print(message[1])
                case 'ENDG':
                    winner = message[1]
                    time_taken = message[2]
                    msg = winner if winner == 'Tie' else f'{winner} won!'
                    winner = figlet_format(text=msg, font='slant')
                    print(winner)
                    print(f'Time taken: {time_taken} seconds!')
                    break
