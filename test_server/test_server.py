import socket
import os


HDRS_404 = 'HTTP/1.0 404 Not Found\r\n\r\n'


def start_the_server():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #семья и тип сервера в скобках
        IP = '127.0.0.1' #socket.gethostbyname(socket.gethostname())
        PORT = 1233
        server.bind((IP, PORT)) 
        #server = socket.create_server((IP, PORT)) то же, что и выше - создание самого сервера
        server.listen(4) #кол-во принимаемых запросов для режима ожидания

        print('Start working...')
        
        while True:
            client, address = server.accept() #принятие запроса с разделением на клиента и его адрес, ждем сигнала.
            data = client.recv(1024).decode('utf8')

            print(data, "\n\n\n\n")
            
            content = load_page_of_request(data)
            if content.decode('utf8') == 'SHUTDOWN':
                client.send((HDRS_404 + 'Shutdown...').encode('UTF8'))
                return
            client.send(content)
            client.shutdown(socket.SHUT_WR)
    except KeyboardInterrupt:
        server.close()
        print('\nShutdown...')


def load_page_of_request(request_data):
    path = request_data.split(' ')[1]
    HDRS = 'HTTP/1.1 200 OK\r\nContent-Type: text/html;charset=UTF8\r\nConnection: close\r\n'
    content = ''
    try:
        if path == '/' or path == 'main':
            path = '/WelcomePage'
        if path == '/shutdown':
            return ("SHUTDOWN").encode('utf8')
        full_path = os.path.join(os.getcwd(), 'views', path.strip('/'))
        with open(full_path, 'rb') as file:
            content = file.read()
        HDRS += 'Content-Length: ' + str(len(content)) + '\r\n\r\n'
        HDRS = HDRS.encode('UTF8')
        return HDRS + content
    except FileNotFoundError:
        return (HDRS_404 + 'Sorry, we have not page like that yet...').encode('UTF8')
    


start_the_server()