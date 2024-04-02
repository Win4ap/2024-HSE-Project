from kivy.animation import Animation

class ColorAnimBase():
    def change_color(self, widget, color):
        animation = Animation(animated_color=color, duration=0.2)
        animation.start(widget)

    def change_color_state(self, first, second, first_state, second_state, first_color, second_color):
        first.state, second.state = first_state, second_state
        self.change_color(first, first_color)
        self.change_color(second, second_color)