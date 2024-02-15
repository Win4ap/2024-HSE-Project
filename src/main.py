import kivy
kivy.require('2.3.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.core.window import Window
from kivy.properties import ObjectProperty

Window.size = (360, 640)
Window.clearcolor = (60/255, 60/255, 60/255, 1)
Window.title = "Delivery: Fast&Smart"

class RoundedButton_auth(Button):
    pass

class LeftRoundedToggleButton_auth(ToggleButton):
    pass

class RightRoundedToggleButton_auth(ToggleButton):
    pass

class AuthWindow(BoxLayout):
    client_switch = ObjectProperty()
    delivery_switch = ObjectProperty()
    login_input = ObjectProperty()
    password_input = ObjectProperty()
    password_hide_button = ObjectProperty()


    def change_delivery(self):
        self.client_switch.state, self.delivery_switch.state = 'down', 'normal'
    
    def change_client(self):
        self.client_switch.state, self.delivery_switch.state = 'normal', 'down'

    def show_password(self):
        self.password_input.password = False if self.password_hide_button.state == 'down' else True


    # placeholder yet, just say thx to god 'cause it is working
    def send_login_request(self):
        if (self.login_input.text == '' or self.password_input.text == ''):
            print('Логин / пароль не может быть пустым!')
        else:
            status = 'курьер'
            if self.client_switch.state == 'down':
                status = 'клиент'
            print(f'Попытка входа: {status}, логин: {self.login_input.text}, пароль: {self.password_input.text}')


class DFSApp(App):
    def build(self):
        return AuthWindow()


if __name__ == '__main__':
    DFSApp().run()
