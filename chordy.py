#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Receive messages from the input port and print them out.
"""
import sys
import mido
from mido.ports import multi_receive, multi_send


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
		self.chordField = 0			# 24-bit field containing the notes that are part of the chord
		self.rootNote = 0
		self.chordAttributes = []

	def setRootNote (self, note):
		if note in self.notes:
			self.rootNote = self.notes.index (note)
		else:
			raise TypeError('note must be a note')

	def getRootNote (self):
		return self.notes [self.rootNote]

	def setRoot (self):		# useless function
		self.chordField |= 0b100000000000000000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def setAdd12 (self):	# add root note to the octave
		self.chordField |= 0b000000000000100000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def setMajor (self):
		self.chordField |= 0b100010010000000000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def setMinor (self):
		self.chordField |= 0b100100010000000000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def set7 (self):
		self.chordField |= 0b000000000010000000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def setMaj7 (self):
		self.chordField |= 0b000000000001000000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def setSus2 (self):
		self.chordField &= 0b111001111111111111111111
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3
		self.chordField |= 0b001000000000000000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def setSus4 (self):
		self.chordField &= 0b111001111111111111111111
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3
		self.chordField |= 0b000001000000000000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def set5 (self):
		self.chordField &= 0b100000000000111111111111
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3
		self.chordField |= 0b100000010000000000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def setDim (self):
		self.chordField &= 0b100000000000111111111111
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3
		self.chordField |= 0b100100100100000000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def setB5 (self):
		self.chordField &= 0b111111101111111111111111
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3
		self.chordField |= 0b000000100000000000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def setAdd9 (self):
		self.chordField |= 0b000000000000001000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def setAdd11 (self):
		self.chordField |= 0b000000000000000001000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def setAdd13 (self):
		self.chordField |= 0b000000000000000000000100
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def display (self):
		print ('Note:' + self.notes [self.rootNote] + ' ' + str (self.rootNote).zfill(2))
		print ('Chord:' + format (self.chordField, '24b'))
		print ('      R 2334 5 677R 9  1   1')
		print ('         mM     mM     1   3')
		print (self.chordAttributes)

	def rankAttribute (self, attribute):		# add additional char in front of attribute to ease the sorting
		if attribute in ('maj', 'min', 'maj7', '7'):
			return ('0' + attribute)
		if attribute in ('sus2', 'sus4', '5'):
			return ('1' + attribute)
		if attribute in ('dim', 'b5', 'add9', 'add11', 'add12', 'add13'):
			return ('2' + attribute)
		return ''

	def derankAttribute (self, attribute):	# remove additional sorting char in front of attribute
		if attribute == '':
			return ''
		return attribute [1:]

	def toChord (self, attribute):							# add or remove attribute of the chord to/from the list of the chord attributes
		attribute = self.rankAttribute (attribute)			# add a sorting rank to the incoming attribute
	
		if attribute in self.chordAttributes:				# check whether we should add or remove chord attribute in the chord attributes list
			self.chordAttributes.remove (attribute)			# removal from the list
			addition = False
		else:
			self.chordAttributes.append (attribute)			# addition to the list
			addition = True
	
		self.chordAttributes.sort ()						# sort list to make sure attributes are always in the correct order; for ex. to make sure b5, dim etc is always managed properly

		# rebuild chord field based on updated chord attributes
		self.chordField = 0
		
		for attribute in self.chordAttributes:
			attribute = self.derankAttribute (attribute)

			if (attribute == 'maj'):
				self.setMajor ()
			elif (attribute == 'min'):
				self.setMinor ()
			elif (attribute == 'maj7'):
				self.setMaj7 ()
			elif (attribute == '7'):
				self.set7 ()
			elif (attribute == 'sus2'):
				self.setSus2 ()
			elif (attribute == 'sus4'):
				self.setSus4 ()
			elif (attribute == '5'):
				self.set5 ()
			elif (attribute == 'dim'):
				self.setDim ()
			elif (attribute == 'b5'):
				self.setB5 ()
			elif (attribute == 'add9'):
				self.setAdd9 ()
			elif (attribute == 'add11'):
				self.setAdd11 ()
			elif (attribute == 'add12'):
				self.setAdd12 ()
			elif (attribute == 'add13'):
				self.setAdd13 ()
			else:
				pass

		return addition

	def getMidiList (self, voicing):
		lst = []
		startVoicing = voicing % 12
		endVoicing = startVoicing + 11
		
		ch = self.chordField
		index = 0
		root = 0
		
		# go through chord and retrieve all the notes to be played; C=0, C#=1, etc
		while ch > 0:
			if ((ch & 0b100000000000000000000000) != 0):			# test MSB
				elt = self.rootNote + index								# note to be played (C being 0)

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


# Bass Chord class inherits from Chord class
class BassChord (Chord):

	def getMidiList (self, voicing):
		lst = []
		startVoicing = voicing % 12
		endVoicing = startVoicing + 11
		
		ch = self.chordField
		ch = ch & 0b100000110000100000000000						# For bass chords, leave root, b5, 5 and octave (12th) only
		index = 0
		root = 0
		
		# go through chord and retrieve all the notes to be played; C=0, C#=1, etc
		while ch > 0:
			if ((ch & 0b100000000000000000000000) != 0):			# test MSB
				elt = self.rootNote + index								# note to be played (C being 0)

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



# Novation Launchpad class
class NovationLaunchpad:
	# name
	name ='Launchpad Mini'

	# mapping from control pad
	padAttribute = {
		0x00:'maj', 0x01:'min', 0x02:'sus4',
		0x10:'maj7', 0x11:'7', 0x12:'sus2',
		0x20:'5', 0x21:'dim', 0x22:'b5',
		0x30:'add9', 0x31:'add11', 0x32:'add13'
	}

	padRootNote = {
		0x03:'A#', 0x04:'B',
		0x13:'F', 0x14:'F#', 0x15:'G', 0x16:'G#', 0x17:'A',
		0x23:'C', 0x24:'C#', 0x25:'D', 0x26:'D#', 0x27:'E'
	}

	padAction = {
		0x08:'display', 0x18:'send'
	}

	# colors of çthe pads
	padColor = {
		'black':0x0C, 'lowRed':0x0D, 'highRed':0x0F, 'lowAmber':0x1D, 'highAmber':0x3F,
		'lowGreen':0x1C, 'highGreen':0x3C, 'lowOrange':0x1E, 'highOrange':0x2F, 'lowYellow':0x2D, 'highYellow':0x3E
	}

	def getKeyByValue (self, d, value):
		return next(filter(lambda item: item[1] == value, d.items()), (None,))[0]

	def __init__(self):
		pass

	def clear (self):	# reset launchpad: B0 00 00
		lst = []
		lst.append (mido.Message ('control_change', control = 0, value = 0))
		#lst.append (mido.Message.from_bytes([0xB0, 0x00, 0x00]))
		return lst
		
	def clearAttribute (self):
		lst = []
		keyList = list (self.padAttribute.keys())
		for key in keyList:
			lst.append (mido.Message ('note_on', note = key, velocity = self.padColor ['highGreen']))
		return lst

	def clearRootNote (self):
		lst = []
		keyList = list (self.padRootNote.keys())
		for key in keyList:
			if '#' in self.padRootNote [key]:
				lst.append (mido.Message ('note_on', note = key, velocity = self.padColor ['lowAmber']))	# this is sharp/flat key
			else:
				lst.append (mido.Message ('note_on', note = key, velocity = self.padColor ['highAmber']))	# this is standard key
		return lst

	def clearAction (self):
		lst = []
		keyList = list (self.padAction.keys())
		for key in keyList:
			lst.append (mido.Message ('note_on', note = key, velocity = self.padColor ['highGreen']))
		return lst

	def liteAttribute (self, value):
		lst = []
		val = self.getKeyByValue (self.padAttribute, value)
		lst.append (mido.Message ('note_on', note = val, velocity = self.padColor ['highRed']))
		return lst

	def unliteAttribute (self, value):
		lst = []
		val = self.getKeyByValue (self.padAttribute, value)
		lst.append (mido.Message ('note_on', note = val, velocity = self.padColor ['highGreen']))
		return lst

	def liteRootNote (self, value):
		lst = []
		val = self.getKeyByValue (self.padRootNote, value)
		lst.append (mido.Message ('note_on', note = val, velocity = self.padColor ['highRed']))
		return lst

	def unliteRootNote (self, value):
		lst = []
		val = self.getKeyByValue (self.padRootNote, value)
		if '#' in value:
			lst.append (mido.Message ('note_on', note = val, velocity = self.padColor ['lowAmber']))	# this is sharp/flat key
		else:
			lst.append (mido.Message ('note_on', note = val, velocity = self.padColor ['highAmber']))	# this is standard key
		return lst

		
		
# inits
bbt = BBT ()
chord = Chord ()
control = NovationLaunchpad ()


# define and open ports
# virtual ports need to be created in windows. For this, use this software: https://www.tobias-erichsen.de/software/loopmidi.html
# get the right port numbers for all ports that need to be opened
inPorts = []
outPorts = []
displayPorts = []

names = mido.get_input_names()
for name in names:
#	if ('LPD8 mk2' in name) or ('chordyCLKIN' in name):
	if (control.name in name) or ('chordyCLKIN' in name):
		inPorts.append (mido.open_input(name))			# use virtual=True on non-windows systems

names = mido.get_output_names()
for name in names:
	if ('chordyOUT' in name):
		outPorts.append (mido.open_output(name))		# use virtual=True on non-windows systems

names = mido.get_output_names()
for name in names:
	if (control.name in name):
		displayPorts.append (mido.open_output(name))


# clear display (control pad)
msgDisplayList = []
msgDisplayList = control.clear ()
for msg in msgDisplayList:
	multi_send (displayPorts, msg)

msgDisplayList = control.clearAttribute ()
for msg in msgDisplayList:
	multi_send (displayPorts, msg)

msgDisplayList = control.clearRootNote ()
for msg in msgDisplayList:
	multi_send (displayPorts, msg)

msgDisplayList = control.liteRootNote (chord.getRootNote ())	# lite root note
for msg in msgDisplayList:
	multi_send (displayPorts, msg)
	
msgDisplayList = control.clearAction ()
for msg in msgDisplayList:
	multi_send (displayPorts, msg)


# main loop

try:

	for inPort in inPorts:
		print (f'Using IN:{inPort}')
	for outPort in outPorts:
		print (f'Using OUT:{outPort}')
	for displayPort in displayPorts:
		print (f'Using DISPLAY:{displayPort}')

	
	for messageIn in multi_receive (inPorts):

		if messageIn.type == 'start':			# reaper only sends start when play is pressed and pos = 0
			bbt.clear ()
			bbt.save ()
		if messageIn.type == 'stop':			# reaper management of stop/continue is inconsistent; implementation is not perfect here
			bbt.save ()
		if messageIn.type == 'continue':		# reaper management of stop/continue is inconsistent; implementation is not perfect here
			bbt.restore ()

		if messageIn.type == 'clock':			# clock received from reaper
			bbt.increment ()
			if bbt.hasBarChanged:
				bbt.display ()

		if (messageIn.type in ('note_on')):						# note on events from keyboard; we don't care about note-off
			if (messageIn.velocity != 0):

				print(f'Received {messageIn}')
				note = messageIn.note
				
				# check if note
				try:
					value = control.padRootNote [note]								# get note: C, C#, etc
				
					msgDisplayList = control.unliteRootNote (chord.getRootNote ())	# unlite previous root note
					for msg in msgDisplayList:
						multi_send (displayPorts, msg)

					chord.setRootNote (value)										# set chord's root note

					msgDisplayList = control.liteRootNote (value)					# lite new root note
					for msg in msgDisplayList:
						multi_send (displayPorts, msg)
					
				except KeyError:
					
					# check if chord attribute
					try:
						value = control.padAttribute [note]							# get chord attribute: maj, min, maj7, etc
						lite = chord.toChord (value)								# add/remove the chord attribute to/from the list of attributes
						if lite:
							msgDisplayList = control.liteAttribute (value)			# chord attribute pad shall be lit
							for msg in msgDisplayList:
								multi_send (displayPorts, msg)
						else:
							msgDisplayList = control.unliteAttribute (value)		# chord attribute pad shall be unlit
							for msg in msgDisplayList:
								multi_send (displayPorts, msg)
					except KeyError:
					
						# check if action
						try:
							value = control.padAction [note]
							if value == 'send':
								msgOutList = chord.getMidiList (60)		# get all the midi commands to be sent to synthetizer (eg. reaper)
								print (msgOutList)
								for msg in msgOutList:
									messageOut = mido.Message ('note_on', note = msg, velocity = 127)
									print(f'Sending {messageOut}')
									multi_send (outPorts, messageOut)
							elif value == 'display':
								chord.display ()
							else:
								pass
						except KeyError:
							pass

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
