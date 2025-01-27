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


# Chord class
class Chord:
	notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
	
	def __init__(self):
		self.chord = 0			# 24-bit field containing the notes that are part of the chord
		self.note = 0

	def setNote (self, note):
		notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

		if note in notes:
			self.note = notes.index (note)
			self.chord = 0
		else:
			raise TypeError('note must be a note')

	# 0b000000000000000000000000
	#   R 2334 5 677R 9  1   1
	#      mM     mM     1   3

	def setRoot (self):
		self.chord |= 0b100000000000000000000000
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3

	def setMajor (self):
		self.chord &= 0b111001111111111111111111
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3
		self.chord |= 0b100010010000000000000000
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3

	def setMinor (self):
		self.chord &= 0b111001111111111111111111
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3
		self.chord |= 0b100100010000000000000000
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3

	def set7 (self):
		self.chord &= 0b111111111100111111111111
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3
		self.chord |= 0b000000000010000000000000
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3

	def setMaj7 (self):
		self.chord &= 0b111111111100111111111111
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3
		self.chord |= 0b000000000001000000000000
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3

	def setSus2 (self):
		self.chord &= 0b111001111111111111111111
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3
		self.chord |= 0b001000000000000000000000
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3

	def setSus4 (self):
		self.chord &= 0b111001111111111111111111
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3
		self.chord |= 0b000001000000000000000000
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3

	def set5 (self):
		self.chord &= 0b100000000000111111111111
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3
		self.chord |= 0b000000010000000000000000
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3

	def setDim (self):
		self.chord &= 0b100000000000111111111111
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3
		self.chord |= 0b000100100100000000000000
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3

	def setB5 (self):
		self.chord &= 0b111111101111111111111111
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3
		self.chord |= 0b000000100000000000000000
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3

	def setAdd9 (self):
		self.chord |= 0b000000000000001000000000
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3

	def setAdd11 (self):
		self.chord |= 0b000000000000000001000000
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3

	def setAdd13 (self):
		self.chord |= 0b000000000000000000000100
		#               R 2334 5 677R 9  1   1
		#                  mM     mM     1   3

	def display (self):
		print ('Note:' + self.notes [self.note] + ' ' + str (self.note).zfill(2))
		print ('Chord:' + format (self.chord, '24b'))
		print ('      R 2334 5 677R 9  1   1')
		print ('         mM     mM     1   3')

	def midiList (self, voicing):
		lst = []
		startVoicing = voicing % 12
		endVoicing = startVoicing + 11
		
		ch = self.chord
		index = 0
		root = 0
		
		# go through chord and retrieve all the notes to be played; C=0, C#=1, etc
		while ch > 0:
			if ((ch & 0b100000000000000000000000) != 0):			# test MSB
				elt = self.note + index								# note to be played (C being 0)

				# now, make sure the chord is in the voicing
				if elt < startVoicing:
					elt += 12
				if elt > endVoicing:
					elt -=12
				if elt not in range (startVoicing, endVoicing):		# this should never happen, except for add9, add11 and add13
					print ('Warning: index ' + str (index) + ' out of voicing range')
					
				elt = elt + voicing									# add to final voicing: this is the "note" in the midi message

				if (elt > 127):										# final test to make sure we are within midi range²
					elt -= 12
				if (elt < 0):										# final test to make sure we are within midi range²
					elt += 12

				lst.append (elt)

			ch = ch & 0b011111111111111111111111					# shift to next degree
			ch = ch << 1
			index += 1

		return lst													# list of all chords to be played, in line with voicing


def isNote (self, note):
	notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

	if note in self.notes:
		return True
	return False


# inits
bbt = BBT ()
chord = Chord ()

# mapping from control pad
padAction = {
	0x00:chord.setMajor, 0x01:chord.setMinor, 0x02:chord.setSus4,
	0x10:chord.setMaj7, 0x11:chord.set7, 0x12:chord.setSus2,
	0x20:chord.set5, 0x21:chord.setDim, 0x22:chord.setB5,
	0x30:chord.setAdd9, 0x31:chord.setAdd11, 0x32:chord.setAdd13,
	0x03:'A#', 0x04:'B', 0x05:'', 0x06:chord.display, 0x07:'send',
	0x13:'F', 0x14:'F#', 0x15:'G', 0x16:'G#', 0x17:'A',
	0x23:'C', 0x24:'C#', 0x25:'D', 0x26:'D#', 0x27:'E',
	0x33:'', 0x34:'', 0x35:'', 0x36:'', 0x37:''
}


# define and open ports
# virtual ports need to be created in windows. For this, use this software: https://www.tobias-erichsen.de/software/loopmidi.html
# get the right port numbers for all ports that need to be opened
inPorts = []
outPorts = []

names = mido.get_input_names()
for name in names:
#	if ('LPD8 mk2' in name) or ('chordyCLKIN' in name):
	if ('Launchpad Mini' in name) or ('chordyCLKIN' in name):
		inPorts.append (mido.open_input(name))			# use virtual=True on non-windows systems

names = mido.get_output_names()
for name in names:
	if ('chordyOUT' in name):
		outPorts.append (mido.open_output(name))		# use virtual=True on non-windows systems



# main loop

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

		if (message.type in ('note_on')):						# note on events from keyboard; we don't care about note-off
			if (message.velocity != 0):

				print(f'Received {message}')

				action = padAction [message.note]				# get corresponding action
				if action is not None:
					if type (action) is str:
						if (action != ''):
							if (action == 'send'):
								msgList = chord.midiList (60)	# voicing of 60
								print (msgList)
								for msg in msgList:
									message.note = msg
									for outPort in outPorts:
										print(f'Sending {message}')
										outPort.send (message)
							else:
								chord.setNote (action)
					else:
						action ()


except KeyboardInterrupt:
	pass


"""
TO DO:
assign midi numbers to actions, notes, etc
(we can implement a "chord" class to build chord)
build chord based on actions
implement voicing
play chord

implement led on launchpad
implement chord actions that are switchable on/off

implement rhythm library
implement bass voicing

play with rythm
implement pages of songs (including 1/2 bars)
play from pages
"""
