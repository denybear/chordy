#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Receive messages from the input port and print them out.
"""
import sys
import mido
from mido.ports import multi_receive

# BBT class
class BBT:
	PPQN = 24
	
	def clear (self):
		self.bar = 0
		self.beat = 0
		self.tick = -1
		self.tickFromStartOfBar = -1
		self.previousBar = -1
		self.previousBeat = -1
		self.previousTick = -1
		self.previousTickFromStartOfBar = -1
		self.hasBarChanged = False
		self.hasBeatChanged = False

	def __init__(self):
		self.clear ()

	def save (self):
		self.barSave = self.bar
		self.beatSave = self.beat
		self.tickSave = self.tick 
		self.tickFromStartOfBarSave = self.tickFromStartOfBar
		self.previousBarSave = self.previousBar 
		self.previousBeatSave = self.previousBeat 
		self.previousTickSave = self.previousTick 
		self.previousTickFromStartOfBarSave = self.previousTickFromStartOfBar
		self.hasBarChangedSave = self.hasBarChanged
		self.hasBeatChangedSave = self.hasBeatChanged

	def restore (self):
		self.bar = self.barSave
		self.beat = self.beatSave
		self.tick = self.tickSave
		self.tickFromStartOfBar = self.tickFromStartOfBarSave
		self.previousBar = self.previousBarSave
		self.previousBeat = self.previousBeatSave
		self.previousTick = self.previousTickSave
		self.previousTickFromStartOfBar = self.previousTickFromStartOfBarSave
		self.hasBarChanged = self.hasBarChangedSave
		self.hasBeatChanged = self.hasBeatChangedSave

	def display (self):
		print ('Bar:' + str (self.bar) + ' Beat:' + str (self.beat) + ' Tick: ' + str (self.tick) + ' Tick from bar start:' + str (self.tickFromStartOfBar))

	def increment (self):
		self.hasBarChanged = False
		self.hasBeatChanged = False
		self.previousTick = self.tick
		self.previousTickFromStartOfBar = self.tickFromStartOfBar
		self.tick +=1
		self.tickFromStartOfBar +=1
		if self.tick >= self.PPQN:
			self.tick = 0
			self.previousBeat = self.beat
			self.beat +=1
			self.hasBeatChanged = True
			if self.beat >= 4:
				self.beat = 0
				self.previousBar = self.bar
				self.bar += 1
				self.tickFromStartOfBar = 0
				self.hasBarChanged = True
					

# define and open ports
# virtual ports need to be created in windows. For this, use this software: https://www.tobias-erichsen.de/software/loopmidi.html
# get the right port numbers for all ports that need to be opened
inPorts = []
outPorts = []

names = mido.get_input_names()
for name in names:
	if ('LPD8 mk2' in name) or ('chordyCLKIN' in name):
		inPorts.append (mido.open_input(name))			# use virtual=True on non-windows systems

names = mido.get_output_names()
for name in names:
	if ('chordyOUT' in name):
		outPorts.append (mido.open_output(name))		# use virtual=True on non-windows systems



# main loop
bbt = BBT ()
bbt.clear ()
try:

	for inPort in inPorts:
		print (f'Using IN:{inPort}')
	for outPort in outPorts:
		print (f'Using OUT:{outPort}')

	for message in multi_receive (inPorts):
		if message.type == 'start':			# reaper only sends start when play is pressed and pos = 0
			bbt.clear ()
			bbt.save ()
		if message.type == 'stop':			# reaper management of stop/continue is inconsistent; implementation is not perfect here
			bbt.save ()
		if message.type == 'continue':		# reaper management of stop/continue is inconsistent; implementation is not perfect here
			bbt.restore ()

		if message.type == 'clock':			# clock received from reaper
			bbt.increment ()
			if bbt.hasBarChanged:
				bbt.display ()

		if message.type in ('note_on', 'note_off'):		# note on/off events from keyboard
			print(f'Received {message}')
			message.note += 60
			for outPort in outPorts:
				outPort.send (message)

except KeyboardInterrupt:
	pass
