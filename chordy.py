#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Denybear
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
		self.beat = 0			# quarter note
		self.eighth = 0			# eighth note
		self.sixteenth = 0		# sixteenth note
		self.tickFromBeat = -1
		self.tick = -1
		self.previousBar = -1
		self.previousBeat = -1
		self.previousEighth = -1
		self.previousSixteenth = -1
		self.previousTickFromBeat = -1
		self.previousTick = -1
		self.hasBarChanged = False
		self.hasBeatChanged = False
		self.hasEighthChanged = False
		self.hasSixteenthChanged = False

	def __init__(self):
		self.clear ()

	def save (self):
		self.barSave = self.bar
		self.beatSave = self.beat
		self.eighthSave = self.eighth
		self.sixteenthSave = self.sixteenth
		self.tickFromBeatSave = self.tickFromBeat 
		self.tickSave = self.tick
		self.previousBarSave = self.previousBar 
		self.previousBeatSave = self.previousBeat 
		self.previousEighthSave = self.previousEighth
		self.previousSixteenthSave = self.previousSixteenth
		self.previousTickFromBeatSave = self.previousTickFromBeat 
		self.previousTickSave = self.previousTick
		self.hasBarChangedSave = self.hasBarChanged
		self.hasBeatChangedSave = self.hasBeatChanged
		self.hasEighthChangedSave = self.hasEighthChanged
		self.hasSixteenthChangedSave = self.hasSixteenthChanged

	def restore (self):
		self.bar = self.barSave
		self.beat = self.beatSave
		self.eighth = self.eighthSave
		self.sixteenth = self.sixteenthSave
		self.tickFromBeat = self.tickFromBeatSave
		self.tick = self.tickSave
		self.previousBar = self.previousBarSave
		self.previousBeat = self.previousBeatSave
		self.previousEighth = self.previousEighthSave
		self.previousSixteenth = self.previousSixteenthSave
		self.previousTickFromBeat = self.previousTickFromBeatSave
		self.previousTick = self.previousTickSave
		self.hasBarChanged = self.hasBarChangedSave
		self.hasBeatChanged = self.hasBeatChangedSave
		self.hasEighthChanged = self.hasEighthChangedSave
		self.hasSixteenthChanged = self.hasSixteenthChangedSave

	def display (self):
		print ('Bar:' + str (self.bar) + ' Beat:' + str (self.beat) + ' 8th:' + str (self.eighth) + ' 16th:' + str (self.sixteenth) + ' Tick: ' + str (self.tick) + ' TickFromBeat:' + str (self.tickFromBeat))

	def increment (self):
		self.hasBarChanged = False
		self.hasBeatChanged = False
		self.hasEighthChanged = False
		self.hasSixteenthChanged = False
		self.previousTickFromBeat = self.tickFromBeat
		self.previousTick = self.tick
		self.tickFromBeat +=1
		self.tick +=1
		if self.tickFromBeat >= (self.PPQN / 4):
			self.previousSixteenth = self.sixteenth
			self.sixteenth += 1
			self.hasSixteenthChanged = True
		if self.tickFromBeat >= (self.PPQN / 2):
			self.previousEighth = self.eighth
			self.eighth += 1
			self.hasEighthChanged = True
		if self.tickFromBeat >= self.PPQN:
			self.tickFromBeat = 0
			self.previousBeat = self.beat
			self.beat +=1
			self.hasBeatChanged = True
			if self.beat >= 4:
				self.beat = 0
				self.eighth = 0
				self.sixteenth = 0		
				self.tick = 0
				self.previousBar = self.bar
				self.bar += 1
				self.hasBarChanged = True


# Chord class
class Chord:
	notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

	def __init__(self):
		self.chordField = 0			# 24-bit field containing the notes that are part of the chord
		self.rootNote = 0
		self.chordType = ''			# either dim, maj, min, sus (exclusively)
		self.chordAttributes = []	# either 6, min7, maj7, 9 (can be combined)

	def setRootNote (self, note):
		if note in self.notes:
			self.rootNote = self.notes.index (note)
			self.setRoot ()
		else:
			raise TypeError('note must be a note')

	def getRootNote (self):
		return self.notes [self.rootNote]

	def setRoot (self):
		self.chordField |= 0b100000000000000000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def setDim (self):
		self.chordField |= 0b100100100100000000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def setMin (self):
		self.chordField |= 0b100100010000000000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def setMaj (self):
		self.chordField |= 0b100010010000000000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def setSus (self):		# sus4
		self.chordField |= 0b100001010000000000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def setMin7 (self):
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

	def setB5 (self):
		self.chordField &= 0b111111101111111111111111
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3
		self.chordField |= 0b000000100000000000000000
		#                    R 2334 5 677R 9  1   1
		#                       mM     mM     1   3

	def setAdd6 (self):
		self.chordField |= 0b000000000100000000000000
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

	def setAdd12 (self):	# add root note to the octave
		self.chordField |= 0b000000000000100000000000
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
		print (self.chordType)
		print (self.chordAttributes)


	def buildChordField (self):								# build chord field based on chord type and chord attributes
		# rebuild chord field based on updated chord attributes
		self.chordField = 0

		# check chord type
		if (self.chordType == 'dim'):
			self.setDim ()
		elif (self.chordType == 'min'):
			self.setMin ()
		elif (self.chordType == 'maj'):
			self.setMaj ()
		elif (self.chordType == 'sus'):
			self.setSus ()
		else:
			return											# if no chord type is set, we forget about the attributes and leave
		
		# check chord attributes
		for attribute in self.chordAttributes:
			if (attribute == 'maj7'):
				self.setMaj7 ()
			elif (attribute == 'min7'):
				self.setMin7 ()
			elif (attribute == 'add6'):
				self.setAdd6 ()
			elif (attribute == 'add9'):
				self.setAdd9 ()
			else:
				pass


	def attributeToChord (self, attribute, addition):		# add or remove attribute of the chord to/from the list of the chord attributes
		if addition:										# add attribute
			if attribute not in self.chordAttributes:		# make sure attribute is not in the list already
				self.chordAttributes.append (attribute)		# addition to the list
		else:												# remove attribute
			if attribute in self.chordAttributes:			# make sure attribute is in the list
				self.chordAttributes.remove (attribute)		# removal from the list
	
		self.buildChordField ()


	def typeToChord (self, typ, addition):					# set or reset type of the chord; returns True if type of chord is empty (reset) 
		previous = self.chordType
		typeEmpty = True
		if addition:										# add type
			self.chordType = typ
		else:												# remove type, only if it was the active type
			if (typ == previous):
				self.chordType = ''
				typeEmpty = False

		self.buildChordField ()
		return typeEmpty


	def getMidiList (self, voicing):						# build a list of midi notes based on the chord to be played
		lst = []
		startVoicing = voicing % 12
		endVoicing = startVoicing + 11
		
		ch = self.chordField
		index = 0
		root = 0
		
		# go through chord and retrieve all the notes to be played; C=0, C#=1, etc
		while ch > 0:
			if ((ch & 0b100000000000000000000000) != 0):			# test MSB
				elt = self.rootNote + index							# note to be played (C being 0)

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
	padType = {
		0x00:'dim', 0x01:'min', 0x02:'maj', 0x03:'sus',
	}

	padAttribute = {
		0x10:'add6', 0x11: 'min7', 0x12:'maj7', 0x13:'add9'
	}

	padRootNote = {
		0x21:'C#', 0x22:'D#', 0x24:'F#', 0x25:'G#', 0x26:'A#',
		0x30:'C', 0x31:'D', 0x32:'E', 0x33:'F', 0x34:'G', 0x35:'A', 0x36:'B'
	}

	padAction = {
		0x08:'display',
		0x18:'voicing+',
		0x28:'voicing-'
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
		
	def clearType (self):
		lst = []
		keyList = list (self.padType.keys())
		for key in keyList:
			lst.append (mido.Message ('note_on', note = key, velocity = self.padColor ['highGreen']))
		return lst

	def clearAttribute (self):
		lst = []
		keyList = list (self.padAttribute.keys())
		for key in keyList:
			lst.append (mido.Message ('note_on', note = key, velocity = self.padColor ['lowGreen']))
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

	def liteType (self, value):
		lst = []
		val = self.getKeyByValue (self.padType, value)
		lst.append (mido.Message ('note_on', note = val, velocity = self.padColor ['highRed']))
		return lst

	def unliteType (self, value):
		lst = []
		val = self.getKeyByValue (self.padType, value)
		lst.append (mido.Message ('note_on', note = val, velocity = self.padColor ['highGreen']))
		return lst

	def liteAttribute (self, value):
		lst = []
		val = self.getKeyByValue (self.padAttribute, value)
		lst.append (mido.Message ('note_on', note = val, velocity = self.padColor ['lowRed']))
		return lst

	def unliteAttribute (self, value):
		lst = []
		val = self.getKeyByValue (self.padAttribute, value)
		lst.append (mido.Message ('note_on', note = val, velocity = self.padColor ['lowGreen']))
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
chordVoicing = 60
bassVoicing = 40


# define and open ports
# virtual ports need to be created in windows. For this, use this software: https://www.tobias-erichsen.de/software/loopmidi.html
# get the right port numbers for all ports that need to be opened
inPorts = []
outPorts = []
displayPorts = []
notesPlaying = []

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

		if (messageIn.type in ('note_on', 'note_off')):								# note on events from keyboard
			noteOn = False
			if (messageIn.type == 'note_on') and (messageIn.velocity != 0):
				noteOn = True

			print(f'Received {messageIn}')
			note = messageIn.note

			# check if root note
			try:
				value = control.padRootNote [note]								# get note: C, C#, etc		

"""
il faudrait une liste des notes actuellement on (en train d'être jouées)
en resultat de getmidilist, on a les notes à jouer
Xil faut faire note-off sur les notes de liste et qui ne sont pas dans getmidilist

idem si on change de voicing
Xidem si on change d'attribute
Xidem si on change de type d'accord (si plus de type d'accord, on ne joue rien ou juste la root selon si la touche d'accord est jouée)
Xidem si on fait note-off de la root (on fait note-off sur toute la liste)
"""

				if noteOn:														# NOTE ON
					# we shall : stop all notes currently playing, then play chord notes, then replace notes currently playing with chord notes
					chord.setRootNote (value)									# set chord's root note
					notesToPlay = chord.getMidiList (chordVoicing)				# get all the midi commands to be sent to synthetizer (eg. reaper)

				elif:															# NOTE OFF
					current = chord.getRootNote ()
					if current == value:										# released key is the root note: all notes should be off
						# we shall : stop all notes currently playing, no new notes to be played
						notesToPlay = []
				
			except KeyError:

				# check if chord type
				try:
					value = control.padType [note]								# get chord type: maj, min, dim, sus
					# we shall : stop all notes currently playing, then replace notes currently playing with new chord notes, then play chord notes
					if chord.typeToChord (value, noteOn):						# change the chord type	(remove previous type)
						# nomore chord type: we shall : stop all notes currently playing, no new notes to be played
						notesToPlay = []					

				except KeyError:
					
					# check if chord attribute
					try:
						# we shall : stop all notes currently playing, then play chord notes, then replace notes currently playing with chord notes
						value = control.padAttribute [note]						# get chord attribute: min7, maj7, add9, etc
						chord.attributeToChord (value, noteOn)					# add the chord attribute to the list of attributes

					except KeyError:
					
						# check if action
						try:
							value = control.padAction [note]
							if noteOn:
								if value == 'display':
									chord.display ()
								elif value == 'voicing+':
									if chordVoicing < 115:						# 127 - 12 = 115
										chordVoicing += 1
								elif value == 'voicing-':
									if chordVoicing > 0:
										chordVoicing -= 1								
								else:
									pass
						except KeyError:
							pass

					# we stop all notes currently playing
					for msg in notesPlaying:
						messageOut = mido.Message ('note_off', note = msg, velocity = 0)
						print(f'Sending {messageOut}')
						multi_send (outPorts, messageOut)

					# we play chord notes; and we replace notes currently playing with chord notes
					for msg in notesToPlay:
						messageOut = mido.Message ('note_on', note = msg, velocity = 127)
						print(f'Sending {messageOut}')
						multi_send (outPorts, messageOut)
					notesPlaying = notesToPlay.copy ()


except KeyboardInterrupt:
	pass


"""
	msgDisplayList = control.liteAttribute (value)		# chord attribute pad shall be lit
	for msg in msgDisplayList:
		multi_send (displayPorts, msg)


TO DO:
assign midi numbers to actions, notes, etc
(we can implement a "chord" class to build chord)
build chord based on actions
implement voicing
play chord
implement led on launchpad
implement chord actions that are switchable on/off

HERE
X4- pressing the same type a second time clears the type (single note mode again)
1- press note sends chord (or note) to midi output
2- ability to play a single note, not necessarily a chord
X3- do not play attribute if type is empty
X4b- no need to light the pads when press on-off
4c- manage note-offs (stop sound)

5- refactor bass chord class
implement rhythm library
implement bass voicing
"""
