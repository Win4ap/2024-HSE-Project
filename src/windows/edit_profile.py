import os

from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label

from plyer import filechooser

from windows.server_logic.server_interaction import ServerLogic

class EditProfile(Screen, ServerLogic):
    avatar = ''
    passport = ''

    def check_state(self) -> str:
        try:
            path_to_login = os.path.join(os.getcwd(), 'src', 'windows', 'server_logic', 'state_login')
            with open(path_to_login, 'r') as file:
                data = file.read()
            data = data.split(' ')[0]
        except:
            Popup(title='Ошибка', content=Label(text='FATAL, выход'), size_hint=(0.8, 0.2)).open()
            data = 'auth'
        return data
    
    def open_native_filechooser(self, photo):
        path = filechooser.open_file()
        if photo:
            if photo == 'avatar':
                self.avatar = path[0]
            elif photo == 'passport':
                self.passport = path[0]

    def send_edit_request(self):
        answer = super().get_profile_fullness()
        if answer == 'server_error':
            Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
        elif answer[:4] != 'done':
            Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
        else:
            answer = answer.split(' ')
            if answer[0] == 'done':
                if self.firstname.text != '' and self.lastname.text != '' and self.phone.text != '' and self.avatar != '' and self.passport != '':
                    answer = super().edit_profile(self.firstname.text, self.lastname.text, self.phone.text, self.avatar, self.passport)
                    if answer[:5] == 'debug':
                        self.firstname.text = ''
                        self.lastname.text = ''
                        self.phone.text = ''
                        self.avatar = ''
                        self.passport = ''
                        self.manager.transition.direction = 'right'
                        self.manager.current = self.check_state()
                    elif answer == 'server_error':
                        Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
                    else:
                        Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
                else:
                    Popup(title='Ошибка', content=Label(text='Нужно заполнить все поля'), size_hint=(0.8, 0.2)).open()
            else:
                Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()