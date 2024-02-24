import kivy
kivy.require('2.3.0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from windows.auth import AuthWindow
from windows.register import RegisterWindow

Window.size = (360, 640)
Window.clearcolor = (60/255, 60/255, 60/255, 1)
Window.title = "Delivery: Fast&Smart"

class DFSApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(AuthWindow(name='auth'))
        sm.add_widget(RegisterWindow(name='register'))
        return sm


if __name__ == '__main__':
    DFSApp().run()
