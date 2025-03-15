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
    :return:
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

        print('Please select difficulty level:')
        print('1 - Easy')
        print('2 - Medium')
        level = input()

        print('Select your square')
        print('X')
        print('O')
        square = input()

        """
        Para esta práctica decidimos implementar el siguiente formato de mensajes,
        el cual es una tupla con una cadena y un diccionario de la siguiente manera
        
        ('CADENA QUE INTERPRETA EL SERVIDOR', {arg0: 'argumento', ...})
        
        Las respuestas del servidor tienen el mismo formato de mensajes,
        por lo que para finalizar la comunicación compararemos el valor
        de la cadena
        """
        command = f'GAME,{level},{square}'

        """
        Solo se pueden enviar bytes por sockets, por lo que es necesario serializar el objeto
        con el modulo pickle con el método dumps
        """
        command_bytes: bytes = str(command).encode()

        # Enviamos el mensaje al servidor
        s.send(command_bytes)
        n = 3 if int(level) == 1 else 5 #número de filas y columnas según la dificultad

        """
        El tablero es una matriz de canedas para saber que fila y columna se va a actualizar
        por las jugadas que haga el servidor o segundo jugador
        
        el codigo de abajo es equivalente a
        board = []
        for i in range(n):
            board.append([])
            for _ in range(n):
                board[i].append('-')
        
        range(n) devuelve un objeto que representa una secuencia de 0 a n - 1, además es iterable
        """
        board = [[' - ' for _ in range(n)] for _ in range(n)]
        update_board(board)
        """
        if square == 'X':
            x = int(input('X: '))
            y = int(input('Y: '))
            s.send(str(f'{x},{y}').encode())
        """
        while True:
            message = s.recv(12).decode().split(',') #Mensajes siempre truncados a 12 bytes
            print(message)
            match message[0]:
                case 'MOVE':
                    x = int(message[1])
                    y = int(message[2])
                    square = message[3]
                    cls()
                    update_board(board, (x, y), square)
                case 'TURN':
                    move = (int(input('X: ')), int(input('Y: ')))
                    s.send(f'{move[0]},{move[1]}'.encode())
                case 'INMV':
                    cls()
                    print(f'The square ({message[1]},{message[2]}) is taken or invalid')
                    update_board(board)
                case 'ENDG':
                    winner = message[1]
                    time_taken = message[2]
                    msg = winner if winner == 'Tie' else f'{winner} won!'
                    winner = figlet_format(text=msg, font='slant')
                    print(winner)
                    print(f'Time taken: {time_taken} seconds!')
                    break
