import socket
import os

def start_the_connection():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #семья и тип соккета в скобках
        IP = '127.0.0.1' #socket.gethostbyname(socket.gethostname())
        PORT = 1233
        while True:
            plot = 0
            while plot != 1 and plot != 2:
                try:
                    plot = int(input("Привет! Ты здесь новенький или уже смешарик?\n 1) Создать аккаунт \n 2) Войти в аккаунт\n"))
                except ValueError:
                    print("Пожалуйста, выберите один из предложенных вариантов(цифру)!")
            if plot == 1:
                ok = False 
                answer = '-'
                while not ok:
                    if answer != '-':
                        print("Извините, такой логин уже занят! Попробуйте ввести другой.")
                    login = input("Введите желаемый логин: ")
                    request = "Check_is_login_free " + login
                    client.connect((IP, PORT))
                    client.send(request.encode('utf8'))
                    answer = client.recv(1024).decode('utf8')
                    client.close()
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    ok = (answer == 'YES')
                password = input("Введите желаемый пароль: ")
                request = 'Set_login_and_password ' + login + ' ' + password
                client.connect((IP, PORT))
                client.send(request.encode('utf8'))
                answer = client.recv(1024).decode('utf8')
                client.close()
                if answer != 'Done':
                    print('Error!!!')
                    return
            print("END")
            return
    except KeyboardInterrupt:
        return
        
        
start_the_connection()