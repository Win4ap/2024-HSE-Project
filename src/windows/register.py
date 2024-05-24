from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from windows.baseclass import ColorAnimBase
from windows.server_logic.server_interaction import ServerLogic

class RegisterWindow(Screen, ColorAnimBase, ServerLogic):
    def show_password(self):
        self.password_input.password = False if self.password_hide_button.state == 'down' else True
        self.password_confirm_input.password = False if self.password_hide_button.state == 'down' else True
        self.password_hide_button.text = 'Скрыть пароль' if self.password_hide_button.state == 'down' else 'Показать пароль'

    def send_register_request(self):
        if self.login_input.text != '' and self.password_input.text != '' and self.password_confirm_input.text != '':
            if self.password_input.text == self.password_confirm_input.text:
                state = 'client' if self.client_switch.state == 'down' else 'delivery'
                answer = super().auth_reg_request(state, 'register', self.login_input.text, self.password_input.text)
                if answer == 'server_error':
                    Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
                elif answer == 'Login already in use':
                    Popup(title='Ошибка', content=Label(text='Логин существует'), size_hint=(0.8, 0.2)).open()
                elif answer == 'true':
                    self.login_input.text = ''
                    self.password_input.text = ''
                    self.password_confirm_input.text = ''
                    self.manager.transition.direction = 'right'
                    self.manager.current = 'auth'
                else:
                    Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
            else:
                Popup(title='Ошибка', content=Label(text='Разные пароли'), size_hint=(0.8, 0.2)).open()
        else:
            Popup(title='Ошибка', content=Label(text='Поле пустое'), size_hint=(0.8, 0.2)).open()
