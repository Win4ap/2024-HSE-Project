import socket
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.animation import Animation

IP = '127.0.0.1'
PORT = 1233

class RegisterWindow(Screen):
    client_switch = ObjectProperty()
    delivery_switch = ObjectProperty()
    login_input = ObjectProperty()
    password_input = ObjectProperty()
    password_confirm_input = ObjectProperty()
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
        self.password_confirm_input.password = False if self.password_hide_button.state == 'down' else True
        self.password_hide_button.text = 'Скрыть пароль' if self.password_hide_button.state == 'down' else 'Показать пароль'

    def send_register_request(self):
        if (self.password_input.text == self.password_confirm_input.text):
            state = 'client' if self.client_switch.state == 'down' else 'delivery'
            request = 'register ' + state + ' ' + self.login_input.text + ' ' + self.password_input.text
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((IP, PORT))
            client.send(request.encode('utf8'))
            answer = client.recv(1024).decode('utf8')
            client.close()
            if (answer == 'login_exists'):
                Popup(title='Ошибка', content=Label(text='Логин существует'), size_hint=(0.7, 0.2)).open()
            else:
                self.login_input.text = ''
                self.password_input.text = ''
                self.password_confirm_input.text = ''
                self.manager.transition.direction = 'right'
                self.manager.current = 'auth'
        else:
            Popup(title='Ошибка', content=Label(text='Разные пароли'), size_hint=(0.7, 0.2)).open()