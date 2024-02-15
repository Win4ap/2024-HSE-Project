import kivy
kivy.require('2.3.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

Window.size = (360, 640)
Window.clearcolor = (64/255, 64/255, 64/255, 1)
Window.title = "Delivery: Fast&Smart"

class Container(BoxLayout):
    pass

class DFSApp(App):
    def build(self):
        pass


if __name__ == '__main__':
    DFSApp().run()