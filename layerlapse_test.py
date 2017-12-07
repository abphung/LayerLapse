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
		self.master.destroy()
		Preprocess(self.video_file, self.song_file)

from Tkinter import *
from tkFileDialog import askopenfile, asksaveasfile
import cv2
import numpy as np
from aubio import onset, tempo, source
from random import *
import pickle
import copy as cp

class Preprocess:

	def __init__(self, video_file, song_file):
		self.video_file = video_file
		self.song_file = song_file
		
		self.master = Tk()
		self.open_file_button = Button(self.master, text="open", command=self.open_command)
		self.save_file_button = Button(self.master, text="save", command=self.save_command)
		self.continue_button = Button(self.master, text="continue", command=self.generate_video)
		# self.dialate_button = Button(self.master, text="dialate", command=self.dialate_selection)
		# self.erode_button = Button(self.master, text="erode", command=self.erode_selection)
		self.open_file_button.pack()
		self.save_file_button.pack()
		self.continue_button.pack()
		# self.dialate_button.pack()
		# self.erode_button.pack()
		self.open_file = None
		self.save_file = None

		self.onsets = self.get_onsets(song_file)

		self.color = self.get_random_color()
		self.drawing = False
		self.mode = True
		self.ix, self.iy = -1, -1
		self.cap = cv2.VideoCapture(video_file)
		self.ret, self.frame = self.cap.read()
		cv2.namedWindow('image')

		self.regions = [np.zeros(self.frame.shape, np.uint8)]
		cv2.setMouseCallback('image', self.mouse_callback)
		self.update()

		self.master.mainloop()

	def open_command(self):
		self.open_file = askopenfile(filetypes=[("Text files", "*.pleasegivemealltens")])
		self.regions = pickle.load(self.open_file)

	def save_command(self):
		self.save_file = asksaveasfile()
		pickle.dump(self.regions, self.save_file)

	def dialate_selection(self):
		self.frame[cv2.dilate(self.frame[self.frame == self.color], None)] = self.color

	def erode_selection(self):
		self.frame[cv2.dilate(self.frame[self.frame == self.color], None)] = self.color

	def get_random_color(self):
		return (randrange(255), randrange(255), randrange(255))

	def get_onsets(self, song_file):
		win_s = 512
		hop_s = win_s // 2
		filename = song_file
		samplerate = 0
		s = source(filename, samplerate, hop_s)
		samplerate = s.samplerate
		o = onset("default", win_s, hop_s, samplerate)
		onsets = []
		total_frames = 0
		while True:
			samples, read = s()
			if o(samples):
				onsets.append(o.get_last())
			total_frames += read
			if read < hop_s: break
		return onsets

	def mouse_callback(self, event, x, y, flags, param):
		if event == cv2.EVENT_LBUTTONDOWN:
			self.drawing = True
			self.ix, self.iy = x, y
		elif event == cv2.EVENT_MOUSEMOVE:
			if self.drawing == True:
				if self.mode == True:
					cv2.rectangle(self.regions[-1], (self.ix, self.iy), (x, y), self.color, -1)
				else:
					cv2.circle(self.regions[-1], (x, y), 5, self.color, -1)
		elif event == cv2.EVENT_LBUTTONUP:
			self.drawing = False
			if self.mode == True:
				cv2.rectangle(self.regions[-1], (self.ix, self.iy), (x, y), self.color, -1)
			else:
				cv2.circle(self.regions[-1], (x, y), 5, self.color, -1)


	def update(self):
		#draw
		#print len(self.regions)
		image = self.frame.copy()
		for region in self.regions:
			image = cv2.addWeighted(image, 1, region, .5, 0)
		cv2.imshow('image', image)

		#handle events
		k = cv2.waitKey(1) & 0xFF
		if k == ord('m'):
			self.mode = not self.mode
		elif k == ord('q'):
			cv2.destroyAllWindows()
		elif k == 13:
			#create a new region that uses a new color
			self.regions.append(np.zeros(self.frame.shape, np.uint8))
			self.color = self.get_random_color()
		self.master.after(1, self.update)

	def generate_video(self):
		self.master.destroy()
		cv2.destroyAllWindows()
		GenerateVideo(self.video_file, self.song_file, self.regions, self.onsets)

from playsound import playsound
import cv2
import numpy as np
import time
from random import *
import copy


class GenerateVideo:

	def __init__(self, video_file, song_file, regions, onsets):
		self.video_file = video_file
		self.song_file = song_file
		self.regions = [regions[0], regions[2], regions[-1]]
		self.onsets = self.get_onsets(song_file)#range(0,100,3)
		print self.onsets
		cap = cv2.VideoCapture(self.video_file)
		cap.set(1, 75)

		self.alphas = {}
		self.futures = {}
		for i in range(len(self.regions)):
			self.regions[i] = cv2.resize(self.regions[i], (640, 480), interpolation = cv2.INTER_LINEAR)
			self.alphas[np.amax(self.regions[i])] = 3

			cap2 = cv2.VideoCapture(self.video_file)
			cap2.set(1, int(3*cap.get(cv2.CAP_PROP_FRAME_COUNT))/4)
			self.futures[np.amax(self.regions[i])] = cap2

		self.start_time = time.time()

		self.update(cap)

	def get_onsets(self, song_file):
		win_s = 512
		hop_s = win_s // 2
		filename = song_file
		samplerate = 0
		s = source(filename, samplerate, hop_s)
		samplerate = s.samplerate
		o = onset("default", win_s, hop_s, samplerate)
		onsets = []
		total_frames = 0
		while True:
			samples, read = s()
			if o(samples):
				onsets.append(o.get_last_s())
			total_frames += read
			if read < hop_s: break
		return onsets

	def draw(self):
		for region in self.regions:
			future = self.futures[np.amax(region)]
			if self.alphas[np.amax(region)] != 0:
				ret, future_frame = future.read()
				#future frame is None sometimes
				future_frame = cv2.resize(future_frame, (640, 480), interpolation = cv2.INTER_LINEAR)
				present_frame = self.present*(region != 0)
				#black out the region in the present image
				self.present = self.present*(region == 0)
				#generate the new image for the region
				alpha = min(1, self.alphas[np.amax(region)])
				self.present_region = cv2.addWeighted(present_frame, 1 - alpha, future_frame*(region != 0), alpha, 0)
				#add the region back into the image
				self.present = cv2.add(self.present, self.present_region)
				#self.present = cv2.add(self.present, future_frame*(region != 0))
		cv2.imshow('image', self.present)

	def update(self, cap):
		running = True
		while running:
			# Capture frame-by-frame
			ret, self.present = cap.read()
			self.present = cv2.resize(self.present, (640, 480), interpolation = cv2.INTER_LINEAR)
			#draw
			self.draw()
			# try:
			# 	self.draw()
			# except:
			# 	print 'bad thing happened'
			# 	running = False
			#handle events
			if cv2.waitKey(1) & 0xFF == 27:
				running = False
			#if the song plays a beat then set alpha to 2
			if time.time() - self.start_time > self.onsets[0]:
				self.onsets = self.onsets[1:]
				region = choice(self.regions)
				self.alphas[np.amax(region)] = 3
				self.futures[np.amax(region)].set(1, int(3*cap.get(cv2.CAP_PROP_FRAME_COUNT))/4)

			#update alphas
			for key in self.alphas:
				if self.alphas[key] > 0:
					self.alphas[key] -= .1

		cap.release()
		cv2.destroyAllWindows()

if __name__ == '__main__':
	#VideoSongSelector()
	GenerateVideo('/Users/andrewphung/Library/Mobile Documents/com~apple~CloudDocs/2017 Fall/371r/371r Final Project/LayerLapse/IMG_2002.MOV',
		'/Users/andrewphung/Library/Mobile Documents/com~apple~CloudDocs/2017 Fall/371r/371r Final Project/LayerLapse/Feel It Still.mp3',
		pickle.load(open('/Users/andrewphung/Library/Mobile Documents/com~apple~CloudDocs/2017 Fall/371r/371r Final Project/LayerLapse/2002.2.pleasegivemealltens')),
		None)