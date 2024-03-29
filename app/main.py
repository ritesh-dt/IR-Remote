import os
os.environ["KIVY_AUDIO"] = "sdl2"

import kivy
import requests
from io import BytesIO
from zipfile import ZipFile


from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import NumericProperty, ObjectProperty, StringProperty

from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel as Label
from kivymd.uix.list import OneLineIconListItem, TwoLineIconListItem

Clock.max_iterations = 20
DATABASE_URL = "http://127.0.0.1:5000/"
iconDict = {"AC": "air-conditioner", "Music Player": "music", "TV": "television"}
remoteList = []

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

remoteDict = {"AC": LayoutMusic, "Music Player": LayoutMusic, "TV": LayoutTV}
soundDict = {}
currentRemote = -1

root_screen_manager = None
class RootScreenManager(ScreenManager):
	title = StringProperty()
	currentRemote = NumericProperty()
	currentCaption = StringProperty()

class IRRemote(MDApp):
	def build(self):
		global root_screen_manager
		root_screen_manager = RootScreenManager()
		return root_screen_manager

	def delete_remote(self):
		global remoteList, currentRemote
		with open("remotes.txt", "w") as remoteTxt:
			index = remoteList.index(str(currentRemote))
			del remoteList[index:index+3]
			for file in os.listdir(f"Remotes/{currentRemote}"):
				os.remove(os.path.join(f"Remotes/{currentRemote}", file))
			os.rmdir(f"Remotes/{currentRemote}")
			#print(remoteList)
			for line in remoteList:
				remoteTxt.write(line + os.linesep)

			self.updateDrawer()
			if remoteList != []:
				currentRemote = int(remoteList[0])
				self.currentRemote = currentRemote
				self.currentCaption = remoteList[2]
				self.transition("Remote", "left", remoteList[1], currentRemote)
			else:
				self.transition("No added remotes...", "left")


	def findItems(self, dropdown_type, selection, caption=None):
		global remoteList
		#print(selection)
		request_data = {
							"dropdown_type": dropdown_type,
							"selection": selection
						}
		response = requests.get(DATABASE_URL, data=request_data)
		#print(response.text)
		if dropdown_type == "appliance":
			self.root.ids.brand_dropdown.items = response.text.split("|")
			#self.root.ids.brand_dropdown.current_item = response.text.split("|")[0]
			self.root.ids.model_dropdown.items = ['']
			#self.root.ids.model_dropdown.current_item = ''
		elif dropdown_type == "add":
			remoteTxt = open("remotes.txt", "r+")
			next_id = max([int(num.replace(os.linesep, "")) for num in remoteTxt.readlines()[::3]]+[-1]) + 1
			appliance = selection.split("/")[0]
			model = selection.split("/")[-1]
			remoteTxt.write(f"{next_id}" + os.linesep)
			remoteTxt.write(f"{appliance}" + os.linesep)
			remoteTxt.write(f"{caption}" + os.linesep)
			remoteTxt.close()
			receiveFile = ZipFile(BytesIO(response.content))
			receiveFile.extractall(path="Remotes")
			model = selection.split("/")[-1]
			os.rename(f"Remotes/{model}", f"Remotes/{next_id}")
			receiveFile.close()
			remoteList = [line.replace(os.linesep, "") for line in open("remotes.txt", "r").readlines()]
			self.updateDrawer()
		else:
			self.root.ids.model_dropdown.items = set(response.text.split("|"))
			#self.root.ids.model_dropdown.current_item = response.text.split("|")[0]

	def on_start(self):
		global remoteList, currentRemote
		request_data = {
							"dropdown_type": "None",
							"selection": "None"
						}
		response = requests.get(DATABASE_URL, data=request_data)
		self.root.ids.appliance_dropdown.items = response.text.split("|")
		remoteList = [line.replace(os.linesep, "") for line in open("remotes.txt", "r").readlines()]
		self.updateDrawer()
		if remoteList != []:
			currentRemote = int(remoteList[-3])
			self.currentRemote = currentRemote
			self.currentCaption = remoteList[-1]
			self.transition("Remote", "left", remoteList[-2], currentRemote)
		else:
			self.transition("No added remotes...", "left")

	def play(self, filename):
		#print(filename)
		if filename in soundDict:
			soundDict[filename].play()
		else:
			print(f"{filename} not in soundDict")

	def save(self, new_caption):
		pass


	def transition(self, name, direction, remoteType=None, remoteId=None):
		global root_screen_manager, currentRemote, soundDict
		if remoteType:
			self.root.ids.remote_screen.clear_widgets()
			buttonLayout = remoteDict[remoteType]()
			buttonLayout.pos_hint = {"x":0, "top":0.9}
			buttonLayout.size_hint = (1, 0.9)
			self.root.ids.remote_screen.add_widget(buttonLayout)
			secondary_text = remoteList[remoteList.index(str(int(remoteId)))+2]
			
			self.root.title = secondary_text
			self.root.ids.md_toolbar.title = secondary_text if secondary_text else remoteList[remoteList.index(str(remoteId).split(".")[0])+1]
			currentRemote = int(remoteId)
			self.currentRemote = currentRemote
			self.currentCaption = secondary_text
			soundDict = {}
			for audioFile in os.listdir(f"Remotes/{int(currentRemote)}"):
				if audioFile.split(".")[-1].lower() in ["wav", "obb"]:
					soundDict[audioFile.split(".")[0]] = SoundLoader.load(f"Remotes/{currentRemote}/{audioFile}")
			#print(soundDict)
		else:
			self.root.title = name
		self.root.ids.screen_manager.direction = direction
		self.root.ids.screen_manager.current = name

	def updateDrawer(self):
		if remoteList != ['']:
			content_nav_drawer = self.root.ids.content_nav_drawer.children[0].children[0]
			childList = content_nav_drawer.children.copy()
			for index in range(len(childList)):
				if isinstance(childList[index], TwoLineItemDrawer):
					content_nav_drawer.remove_widget(childList[index])
				#else:
					#print(childList[index].text)
			for index in range(0, len(remoteList), 3):
				item = TwoLineItemDrawer(text=remoteList[index+2], secondary_text=remoteList[index+1], icon=iconDict[remoteList[index+1]])
				#item.on_press = self.transition("Remote", "left")
				item.nav_drawer = self.root.ids.nav_drawer
				item.remoteId = remoteList[index]
				content_nav_drawer.add_widget(item, index=100) # Why 100?

if __name__ == "__main__":
	ir = IRRemote()
	ir.run()