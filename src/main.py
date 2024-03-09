import kivy
import os
kivy.require('2.3.0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from windows.auth import AuthWindow
from windows.register import RegisterWindow
from windows.client import ClientSide

Window.size = (360, 640)
Window.clearcolor = (60/255, 60/255, 60/255, 1)
Window.title = "Delivery: Fast&Smart"

class DFSApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(AuthWindow(name='auth'))
        sm.add_widget(RegisterWindow(name='register'))
        sm.add_widget(ClientSide(name='client'))
        path_to_login = os.path.join(os.getcwd(), 'src', 'windows', 'server_logic', 'state_login')
        try:
            with open(path_to_login, 'r') as file:
                data = file.read()
        except FileNotFoundError:
            data = ''
        if data == '':
            sm.current = 'auth'
        else:
            data = data.split(' ')
            if len(data) == 2:
                sm.current = data[0]
            else:
                sm.current = 'auth'
        return sm


if __name__ == '__main__':
    DFSApp().run()
