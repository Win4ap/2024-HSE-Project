from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from windows.baseclass import ColorAnimBase, ProfileBase, ClientOrderPreview
from windows.server_logic.server_interaction import ServerLogic

class DeliveryActiveOrderPreview(ClientOrderPreview):
    def __init__(self, **kwargs):
        super(ClientOrderPreview, self).__init__(**kwargs)

    def on_release(self):
        self.link_button.text = 'Завершить'
        self.link_button.operation = 'complete'
        return super().on_release()

class DeliveryFreeOrderPreview(ClientOrderPreview):
    def __init__(self, **kwargs):
        super(ClientOrderPreview, self).__init__(**kwargs)

    def on_release(self):
        self.link_button.text = 'Взять'
        self.link_button.operation = 'take'
        return super().on_release()

class DeliverySide(Screen, ColorAnimBase, ProfileBase, ServerLogic):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.delivery_main_frame.current = 'delivery_orders'

    def on_enter(self, *args):
        self.show_orders()
        return super().on_enter(*args)

    def quit(self):
        super().quit()
        self.delivery_main_frame.current = 'delivery_orders'
        self.active_orders.animated_color, self.free_orders.animated_color = (217/255, 217/255, 217/255, 0), (217/255, 217/255, 217/255, 0)

    def switch_main_to(self, screen):
        if self.delivery_main_frame.current != screen:
            self.delivery_main_frame.current = screen
        if screen == 'delivery_chat':
            self.icon_chat.source, self.icon_list.source, self.icon_user.source = 'img/bold_chat.png', 'img/list.png', 'img/user.png'
        elif screen == 'delivery_orders':
            self.icon_chat.source, self.icon_list.source, self.icon_user.source = 'img/chat.png', 'img/bold_list.png', 'img/user.png'
        elif screen == 'delivery_profile':
            self.icon_chat.source, self.icon_list.source, self.icon_user.source = 'img/chat.png', 'img/list.png', 'img/bold_user.png'

    def show_orders(self):
        cur = self.active_orders.state
        #answer = super().get_delivery_orders() if cur == 'down' else super().get_free_orders()
        #for answer.json()[i]['elem']

    def order_interaction(self, operation):
        print(operation)