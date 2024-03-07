from kivy.animation import Animation

class AuthRegBase():
    def change_color(self, widget, color):
        animation = Animation(animated_color=color, duration=0.2)
        animation.start(widget)

    def change_client_state(self):
        self.client_switch.state, self.delivery_switch.state = 'down', 'normal'
        self.change_color(self.client_switch, (120/255, 120/255, 120/255, 1))
        self.change_color(self.delivery_switch, (80/255, 80/255, 80/255, 1))
    
    def change_delivery_state(self):
        self.client_switch.state, self.delivery_switch.state = 'normal', 'down'
        self.change_color(self.client_switch, (80/255, 80/255, 80/255, 1))
        self.change_color(self.delivery_switch, (120/255, 120/255, 120/255, 1))