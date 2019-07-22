#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

from __future__ import print_function

import sys
if sys.version_info[0] == 2:
	from Tkinter import *
else:
	from tkinter import *
#import thread
import dummy_threading
import time

class SliderMulti(Frame):
	def __init__(self, channels, master=None):
		Frame.__init__(self, master)
		self.init(channels)
		self.pack()


	def init(self, channels):
		self._channels = channels
		self.var = []
		self.scales = []
		self.option_add('*font', 'system 9')
		
		i = 0
		for channel in self._channels:
			self.var.append(DoubleVar(0))
			self.scales.append(
				Scale(self, label=channel[0], variable=self.var[i],
					  to=channel[1], orient=VERTICAL))
			self.scales[i]["from"] = channel[2]
			self.scales[i]["resolution"] = channel[3]
			self.scales[i]["length"] = channel[4]
			self.scales[i].pack(side=LEFT)
			i = i + 1

	def get(self):
		val = []
		for v in self.var:
			val.append(v.get())

		return val

	def set(self, value):
		i = 0
		for v in value:
			self.var[i].set(v)

			i = i + 1
		return


def test ():
	channels = (("angle", 0, 360, 0.1, 200), ("velocity", -100, 100, 0.1, 200))
	slider = SliderMulti(channels)
	sth = dummy_threading.Thread(target=slider.mainloop, args=())
	sth.start()
#	thread.start_new_thread(slider.mainloop, ())

	while (1):
		print(slider.get())
		time.sleep(0.5)
#		slider.update()

if  __name__ == '__main__': test()
