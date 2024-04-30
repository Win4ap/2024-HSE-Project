import os

from kivy.animation import Animation
from kivy.uix.popup import Popup
from kivy.uix.label import Label

from windows.server_logic.server_interaction import ServerLogic

class ColorAnimBase():
    def change_color(self, widget, color):
        animation = Animation(animated_color=color, duration=0.2)
        animation.start(widget)

    def change_color_state(self, first, second, first_state, second_state, first_color, second_color):
        first.state, second.state = first_state, second_state
        self.change_color(first, first_color)
        self.change_color(second, second_color)

class ProfileBase(ServerLogic):
    def quit(self):
        path_to_login = os.path.join(os.getcwd(), 'src', 'windows', 'server_logic', 'state_login')
        path_to_fullname = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'fullname')
        path_to_avatar = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'avatar.jpg')
        path_to_no_avatar = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'no_avatar.png')
        with open(path_to_login, 'wb'):
            pass
        with open(path_to_fullname, 'wb'):
            pass
        if os.path.isfile(path_to_avatar):
            os.remove(path_to_avatar)
        self.manager.transition.direction = 'down'
        self.manager.current = 'auth'
        self.icon_chat.source, self.icon_list.source, self.icon_user.source = 'img/chat.png', 'img/bold_list.png', 'img/user.png'
        self.user_fullname.text = '[b]Неизвестно[/b]'
        self.user_avatar.path = path_to_no_avatar

    def show_profile(self):
        path_to_avatar = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'avatar.jpg')
        path_to_fullname = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'fullname')
        if not os.path.isfile(path_to_avatar):
            answer = super().get_profile_data()
            if answer == 'server_error':
                Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
            elif answer == 'Not Found':
                Popup(title='Завершить регистрацию', content=Label(text='Заполните профиль\nПрофиль -> Редактировать данные'), size_hint=(0.9, 0.2)).open()
            else:
                answer = answer.split('~')
                self.user_fullname.text = f'[b]{answer[0]} {answer[1]}[/b]'
                with open(path_to_fullname, 'w') as file:
                    file.write(f'{answer[0]} {answer[1]}')
                self.user_avatar.path = path_to_avatar
        else:
            with open(path_to_fullname, 'r') as file:
                data = file.read()
            data = data.split(' ')
            self.user_fullname.text = f'[b]{data[0]} {data[1]}[/b]'
            self.user_avatar.path = path_to_avatar