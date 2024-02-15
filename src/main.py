import kivy
kivy.require('2.3.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import ObjectProperty

Window.size = (360, 640)
Window.clearcolor = (64/255, 64/255, 64/255, 1)
Window.title = "Delivery: Fast&Smart"

class Container(BoxLayout):
    client_state = ObjectProperty()
    delivery_state = ObjectProperty()

    def change_delivery(self):
        self.client_state.state = 'down'
        self.delivery_state.state = 'normal'
    
    def change_client(self):
        self.client_state.state = 'normal'
        self.delivery_state.state = 'down'

class DFSApp(App):
    def build(self):
        return Container()


if __name__ == '__main__':
    DFSApp().run()
