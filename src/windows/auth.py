import socket
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.animation import Animation

IP = '127.0.0.1'
PORT = 1233

class AuthWindow(Screen):
    client_switch = ObjectProperty()
    delivery_switch = ObjectProperty()
    login_input = ObjectProperty()
    password_input = ObjectProperty()
    password_hide_button = ObjectProperty()

    def change_color(self, widget, color):
        animation = Animation(animated_color=color, duration=0.2)
        animation.start(widget)

    def change_client_state(self):
        self.client_switch.state, self.delivery_switch.state = 'down', 'normal'
        self.change_color(self.client_switch, (120/255, 120/255, 120/255, 1))
        self.change_color(self.delivery_switch, (80/255, 80/255, 80/255, 1))
    
    def change_delivery_state(self):
        self.client_switch.state, self.delivery_switch.state = 'normal', 'down'
        self.change_color(self.client_switch, (80/255, 80/255, 80/255, 1))
        self.change_color(self.delivery_switch, (120/255, 120/255, 120/255, 1))

    def show_password(self):
        self.password_input.password = False if self.password_hide_button.state == 'down' else True

    def send_login_request(self):
        state = 'client' if self.client_switch.state == 'down' else 'delivery'
        request = 'login {state} {self.login_input.text} {self.password_input.text}'
        self.login_input.text = ''
        self.password_input.text = ''
        #client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #client.connect((IP, PORT))
        #client.send(request.encode('utf8'))
        #answer = client.recv(1024).decode('utf8')
        #client.close()
        #if (answer == 'incorrect'):
        #    # неверный логин или пароль + проверьте кто вы курьер или клиент
        #else:
        #    # входим в основное приложение и делаем запросы далее через логин