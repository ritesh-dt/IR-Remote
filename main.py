import kivy
import os
import requests
from io import BytesIO
from kivymd.app import MDApp


from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel as Label
from kivymd.uix.list import OneLineIconListItem, TwoLineIconListItem

Clock.max_iterations = 20
DATABASE_URL = "http://127.0.0.1:5000/"
iconDict = {"AC": "air-conditioner", "TV": "television"}

class OneLineItemDrawer(OneLineIconListItem):
	icon = StringProperty()
class TwoLineItemDrawer(TwoLineIconListItem):
	icon = StringProperty()
	nav_drawer = ObjectProperty()
	remoteId = NumericProperty()

class ContentNavigationDrawer(BoxLayout):
	nav_drawer = ObjectProperty()

class LayoutIconButton(MDIconButton):
	pass

class LayoutTV(FloatLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

class LayoutMusic(FloatLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

remoteDict = {"AC": LayoutMusic, "TV": LayoutTV}

root_screen_manager = None
class RootScreenManager(ScreenManager):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

class IRRemote(MDApp):
	def build(self):
		global root_screen_manager
		root_screen_manager = RootScreenManager()
		return root_screen_manager

	def findItems(self, dropdown_type, selection, caption=None):
		print(selection)
		request_data = {
							"dropdown_type": dropdown_type,
							"selection": selection
						}
		response = requests.get(DATABASE_URL, data=request_data)
		print(response.text)
		if dropdown_type == "appliance":
			self.root.ids.brand_dropdown.items = response.text.split("|")
			#self.root.ids.brand_dropdown.current_item = response.text.split("|")[0]
			self.root.ids.model_dropdown.items = ['']
			#self.root.ids.model_dropdown.current_item = ''
		elif dropdown_type == "add":
			remoteTxt = open("remotes.txt", "r+")
			next_id = max([int(num) for num in remoteTxt.readlines()[::3]]+[-1])
			appliance = selection.split("/")[0]
			remoteTxt.write(f"{next_id+1}" + os.linesep)
			remoteTxt.write(f"{appliance}" + os.linesep)
			remoteTxt.write(f"{caption}" + os.linesep)
			receiveFile = BytesIO(response.content)
			with open(f"Remotes/{next_id+1}.txt", "wb") as remoteFile:
				remoteFile.write(receiveFile.getbuffer())
		else:
			self.root.ids.model_dropdown.items = response.text.split("|")
			#self.root.ids.model_dropdown.current_item = response.text.split("|")[0]

	def on_start(self):
		request_data = {
							"dropdown_type": "None",
							"selection": "None"
						}
		response = requests.get(DATABASE_URL, data=request_data)
		#file = BytesIO(response.content)
		print(response.text)
		self.root.ids.appliance_dropdown.items = response.text.split("|")
		remoteFile = open("remotes.txt", "r").readlines()
		content_nav_drawer = self.root.ids.content_nav_drawer.children[0].children[0]
		for index in range(0, len(remoteFile), 3):
			item = TwoLineItemDrawer(text=remoteFile[index+2].replace(os.linesep, ""), secondary_text=remoteFile[index+1].replace(os.linesep, ""), icon=iconDict[remoteFile[index+1].replace(os.linesep, "")])
			#item.on_press = self.transition("Remote", "left")
			item.nav_drawer = self.root.ids.nav_drawer
			item.remoteId = remoteFile[index].replace(os.linesep, "")
			content_nav_drawer.add_widget(item, index=100)


	def transition(self, name, direction, remoteType=None, remoteId=None):
		global root_screen_manager
		if remoteType:
			self.root.ids.remote_screen.clear_widgets()
			buttonLayout = remoteDict[remoteType]()
			buttonLayout.pos_hint = {"x":0, "top":0.9}
			buttonLayout.size_hint = (1, 0.9)
			self.root.ids.remote_screen.add_widget(buttonLayout)
		self.root.ids.screen_manager.direction = direction
		self.root.ids.screen_manager.current = name

if __name__ == "__main__":
	ir = IRRemote()
	ir.run()