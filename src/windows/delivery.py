import os

from kivy.uix.screenmanager import Screen
from kivy.uix.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from windows.baseclass import ColorAnimBase
from windows.server_logic.server_interaction import ServerLogic

class DeliveryActiveOrderPreview(ButtonBehavior, BoxLayout):
    pass

class DeliveryFreeOrderPreview(ButtonBehavior, BoxLayout):
    pass

class DeliverySide(Screen, ColorAnimBase, ServerLogic):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.delivery_main_frame.current = 'delivery_orders'

    def switch_main_to(self, screen):
        if self.delivery_main_frame.current != screen:
            self.delivery_main_frame.current = screen
        if screen == 'delivery_chat':
            self.icon_chat.source, self.icon_list.source, self.icon_user.source = 'img/bold_chat.png', 'img/list.png', 'img/user.png'
        elif screen == 'delivery_orders':
            self.icon_chat.source, self.icon_list.source, self.icon_user.source = 'img/chat.png', 'img/bold_list.png', 'img/user.png'
        elif screen == 'delivery_profile':
            self.icon_chat.source, self.icon_list.source, self.icon_user.source = 'img/chat.png', 'img/list.png', 'img/bold_user.png'

    def show_profile(self):
        pass