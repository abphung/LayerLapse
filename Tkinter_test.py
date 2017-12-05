from Tkinter import *
from tkFileDialog import askopenfilename

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
		self.video_button.config(text=self.video_file)

	def song_command(self):
		self.song_file = askopenfilename()
		self.song_button.config(text=self.song_file)

	def check_files(self):
		if self.video_file != None and self.song_file != None and self.continue_button == None:
			self.continue_button = Button(self.master, text="Continue", command=self.preprocess) 
			self.continue_button.pack()
		self.master.after(1, self.check_files)

	def preprocess(self):
		self.master.quit()
		Preprocess(self.video_file, self.song_file)

import cv2
import numpy as np
from aubio import onset, tempo, source

class Preprocess:

	def __init__(self, video_file, song_file):
		self.video_file = video_file
		self.song_file = song_file

		self.master = Tk()
		self.open_file_button = Button(self.master, text="open", command=self.open_command)
		self.save_file_button = Button(self.master, text="save", command=self.save_command)
		self.continue_button = Button(self.master, text="continue", command=self.generate_video)
		self.open_file_button.pack()
		self.save_file_button.pack()
		self.continue_button.pack()
		self.open_file = None
		self.save_file = None
		self.master.mainloop()

		self.cap = cv2.VideoCapture(video_file)
		self.update()

	def open_command(self):
		self.open_file = askopenfilename()

	def save_command(self):
		self.save_file = asksaveasfile()

	def generate_video(self):
		self.master.quit()
		GenerateVideo()

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

		self.master.after(1, self.update)

if __name__ == '__main__':
	VideoSongSelector()