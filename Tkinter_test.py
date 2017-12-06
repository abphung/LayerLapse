from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfile

class VideoSongSelector:
	
	def __init__(self):
		self.master = Tk()
		self.video_button = Button(self.master, text="Choose a video", command=self.video_command)
		self.song_button = Button(self.master, text="Choose a song", command=self.song_command)
		self.continue_button = None
		self.video_button.pack()
		self.song_button.pack()
		self.video_file = None
		self.song_file = None
		self.check_files()
		self.master.mainloop()

	def video_command(self):
		self.video_file = askopenfilename()
		print self.video_file
		self.video_button.config(text=self.video_file)

	def song_command(self):
		self.song_file = askopenfilename()
		print self.song_file
		self.song_button.config(text=self.song_file)

	def check_files(self):
		if self.video_file != None and self.song_file != None and self.continue_button == None:
			self.continue_button = Button(self.master, text="Continue", command=self.preprocess) 
			self.continue_button.pack()
		try:
			self.master.after(1, self.check_files)
		except:
			pass

	def preprocess(self):
		Preprocess(self.video_file, self.song_file)

import cv2
import numpy as np
from aubio import onset, tempo, source
from random import *
import pickle

class Preprocess:

	def __init__(self, video_file, song_file):
		self.video_file = video_file
		self.song_file = song_file

		self.master = Tk()
		self.open_file_button = Button(self.master, text="open", command=self.open_command)
		self.save_file_button = Button(self.master, text="save", command=self.save_command)
		self.continue_button = Button(self.master, text="continue", command=self.generate_video)
		self.dialate_button = Button(self.master, text="dialate", command=self.dialate_selection)
		self.erode_button = Button(self.master, text="erode", command=self.erode_selection)
		self.open_file_button.pack()
		self.save_file_button.pack()
		self.continue_button.pack()
		self.dialate_button.pack()
		self.erode_button.pack()
		self.open_file = None
		self.save_file = None

		self.color = self.get_random_color()
		self.drawing = False
		self.mode = True
		self.ix, self.iy = -1, -1
		self.cap = cv2.VideoCapture(video_file)
		self.ret, self.frame = self.cap.read()
		cv2.namedWindow('image')
		cv2.setMouseCallback('image', self.draw)

		self.draw()
		self.update()
		self.master.mainloop()

	def open_command(self):
		self.open_file = askopenfilename()

	def save_command(self):
		self.save_file = asksaveasfile()
		pickle.dump(self.frame, self.save_file)

	def dialate_selection(self):
		self.frame[cv2.dilate(self.frame[self.frame == self.color], None)] = self.color

	def erode_selection(self):
		self.frame[cv2.dilate(self.frame[self.frame == self.color], None)] = self.color

	def get_random_color(self):
		return (randrange(255), randrange(255), randrange(255))

	def draw(self, event, x, y, flags, param):
		if event == cv2.EVENT_LBUTTONDOWN:
			self.drawing = True
			self.ix, self.iy = x, y
		elif event == cv2.EVENT_MOUSEMOVE:
			if self.drawing == True:
				if self.mode == True:
					cv2.rectangle(self.frame, (self.ix, self.iy), (x, y), self.color, -1)
				else:
					cv2.circle(self.frame, (x, y), 5, self.color, -1)
		elif event == cv2.EVENT_LBUTTONUP:
			self.drawing = False
			if self.mode == True:
				cv2.rectangle(self.frame, (self.ix, self.iy), (x, y), self.color, -1)
			else:
				cv2.circle(self.frame, (x, y), 5, self.color, -1)

	def update(self):
		cv2.imshow('image', self.frame)
		k = cv2.waitKey(1) & 0xFF
		if k == ord('m'):
			self.mode = not self.mode
		elif k == ord('q'):
			cv2.destroyAllWindows()
		elif k == 13:
			self.color = self.get_random_color()
		try:
			self.master.after(1, self.update)
		except:
			pass

	def generate_video(self):
		GenerateVideo()

class GenerateVideo:

	def __init__(self):
		pass

	def update(self):
		# Capture frame-by-frame
		ret, frame = self.cap.read()

		# Our operations on the frame come here
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		dy = cv2.getTrackbarPos('dy', 'image')
		threshold1 = cv2.getTrackbarPos('threshold1', 'image')
		threshold2 = cv2.getTrackbarPos('threshold2', 'image')
		#edges = cv2.Canny(frame, dy, threshold1, threshold2)
		dst = cv2.cornerHarris(gray,2,3,0.04)

		#result is dilated for marking the corners, not important
		dst = cv2.dilate(dst,None)
		# Threshold for an optimal value, it may vary depending on the image.
		frame[dst>0.01*dst.max()]=[0,0,255]
		#img_erosion = cv2.erode(edges, kernel, iterations=1)
		# Display the resulting frame
		cv2.imshow('frame', frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			self.master.quit()
			self.cap.release()
			cv2.destroyAllWindows()
		try:
			self.master.after(1, self.update)
		except:
			pass

if __name__ == '__main__':
	#VideoSongSelector()
	Preprocess('/Users/andrewphung/Library/Mobile Documents/com~apple~CloudDocs/2017 Fall/371r/371r Final Project/LayerLapse/IMG_2002.MOV',
		'/Users/andrewphung/Library/Mobile Documents/com~apple~CloudDocs/2017 Fall/371r/371r Final Project/LayerLapse/Feel It Still.mp3')