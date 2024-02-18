import kivy
kivy.require('2.3.0')

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.properties import ObjectProperty

Window.size = (360, 640)
Window.clearcolor = (60/255, 60/255, 60/255, 1)
Window.title = "Delivery: Fast&Smart"


class RoundedButton(Button):
    pass


class EmptyWindow(Screen):
    pass


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

    # placeholder yet, just say thx to god 'cause it is working
    # TODO: connect with server instead of print
    def send_login_request(self):
        if (self.login_input.text == '' or self.password_input.text == ''):
            print('Логин / пароль не может быть пустым!')
        else:
            status = 'курьер'
            if self.client_switch.state == 'down':
                status = 'клиент'
            print(f'Попытка входа: {status}, логин: {self.login_input.text}, пароль: {self.password_input.text}')
            self.login_input.text = ''
            self.password_input.text = ''


class DFSApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(AuthWindow(name='auth'))
        sm.add_widget(EmptyWindow(name='empty'))
        return sm



if __name__ == '__main__':
    DFSApp().run()
