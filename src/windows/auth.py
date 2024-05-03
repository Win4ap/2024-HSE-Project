import os

from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from windows.baseclass import ColorAnimBase
from windows.server_logic.server_interaction import ServerLogic

class AuthWindow(Screen, ColorAnimBase, ServerLogic):
    def show_password(self):
        self.password_input.password = False if self.password_hide_button.state == 'down' else True
        self.password_hide_button.text = 'Скрыть пароль' if self.password_hide_button.state == 'down' else 'Показать пароль'

    def send_login_request(self):
        if self.login_input.text != '' and self.password_input.text != '':
            state = 'client' if self.client_switch.state == 'down' else 'delivery'
            answer = super().auth_reg_request(state, 'login', self.login_input.text, self.password_input.text)
            if answer == 'server_error':
                Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
            elif answer == 'false' or answer == 'Login not found':
                Popup(title='Ошибка', content=Label(text='Неверный логин или пароль'), size_hint=(0.8, 0.2)).open()
            elif answer == 'true':
                self.manager.transition.direction = 'up'
                self.manager.current = state
                path_to_login = os.path.join(os.getcwd(), 'src', 'windows', 'server_logic', 'state_login')
                with open(path_to_login, 'w') as file:
                    file.write(f'{state} {self.login_input.text}')
                self.login_input.text = ''
                self.password_input.text = ''
            else:
                Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
        else:
            Popup(title='Ошибка', content=Label(text='Поле пустое'), size_hint=(0.8, 0.2)).open()
