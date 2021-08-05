from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivymd.uix.behaviors import RectangularRippleBehavior, BackgroundColorBehavior
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRectangleFlatButton,MDRoundFlatButton,MDRectangleFlatButton,MDRaisedButton,MDIconButton
from kivy.graphics import Color


b = Builder.load_file("my.kv")
class LayoutIconButton(MDIconButton):
	pass

class MyApp(MDApp):
    sm = ScreenManager()
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        return Screen()
if __name__ == '__main__':
    MyApp().run()
