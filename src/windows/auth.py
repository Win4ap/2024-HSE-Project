from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty

from windows.baseclass import AuthRegBase
from windows.server_logic.server_interaction import ServerLogic

class AuthWindow(Screen, AuthRegBase, ServerLogic):
    client_switch = ObjectProperty()
    delivery_switch = ObjectProperty()
    login_input = ObjectProperty()
    password_input = ObjectProperty()
    password_hide_button = ObjectProperty()

    def show_password(self):
        self.password_input.password = False if self.password_hide_button.state == 'down' else True
        self.password_hide_button.text = 'Скрыть пароль' if self.password_hide_button.state == 'down' else 'Показать пароль'

    def send_login_request(self):
        state = 'client' if self.client_switch.state == 'down' else 'delivery'
        answer = super().auth_reg_request(state, 'login', self.login_input.text, self.password_input.text)
        if (answer == 'server_error'):
            Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
        elif (answer == 'incorrect'):
            Popup(title='Ошибка', content=Label(text='Неверный пароль'), size_hint=(0.8, 0.2)).open()
        elif (answer == 'login_doesnt_exists'):
            Popup(title='Ошибка', content=Label(text='Логин не найден'), size_hint=(0.8, 0.2)).open()
        else:
            answer = answer.split(' ')
            if (len(answer) == 3 and answer[0] == 'correct'):
                self.login_input.text = ''
                self.password_input.text = ''
                self.manager.transition.direction = 'up'
                self.manager.current = 'client'
            else:
                Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()