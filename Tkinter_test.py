from Tkinter import *
from tkFileDialog import askopenfilename

class GUI:
	
	def __init__(self):
		self.master = Tk()
		self.video_button = Button(self.master, text="Chose a video", command=self.video_command)
		self.song_button = Button(self.master, text="Chose a song", command=self.song_command)
		self.continue_button = None
		self.video_button.pack()
		self.song_button.pack()
		self.video_file = None
		self.song_file = None
		self.check_files()
		self.master.mainloop()

	def video_command(self):
		self.video_file = askopenfilename()
		self.video_button.config(text=self.video_file)

	def song_command(self):
		self.song_file = askopenfilename()
		self.song_button.config(text=self.song_file)

	def check_files(self):
		if self.video_file != None and self.song_file != None and self.continue_button == None:
			self.continue_button = Button(self.master, text="Continue", command=self.process) 
			self.continue_button.pack()
		self.master.after(1, self.check_files)

	def process(self):
		self.master.quit()
		
GUI()