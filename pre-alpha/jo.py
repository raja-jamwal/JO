#
#	(C) Raja Jamwal <linux1@zoho.com>
# 
#  	JO is joystick to mouse emulator
#
#  this is pre-alpha version, use at your own risk
#

import sys
import commands
import thread
import threading
import time

break_b = False

def threadt(exet,d):
	time_s = 0.01
	multi = 1
	while not break_b:
		if exet.split(" ")[1] == "mousemove_relative":
			opt = exet.split(" ")
			ratex = 0
			reatey = 0
			
			if opt[2] == "--":
				print "negative"
				if int(opt[3]) != 0:
					ratex = multi*int(opt[3])
					exe("xdotool mousemove_relative -- "+str(ratex)+" 0")
				else:
					ratey = multi*int(opt[4])
					exe("xdotool mousemove_relative -- 0 "+str(ratey))
			else:
				print "positive"
				if int(opt[2]) != 0:
					ratex = multi*int(opt[2])
					exe("xdotool mousemove_relative "+str(ratex)+" 0")
				else:
					ratey = multi*int(opt[3])
					exe("xdotool mousemove_relative 0 "+str(ratey))

			multi=multi+0.1
		else:
			exe(exet)
		time.sleep(time_s)
		#time_s = time_s - 0.001

def mouse(cmd):
	global break_b
	break_b = False
	thread.start_new_thread(threadt, ("xdotool "+str(cmd),"0"))

def mouse_s(cmd):
	exe("xdotool "+str(cmd))

def break_event():
	global break_b
	break_b = True

def exe(cmd):
	commands.getoutput(cmd)
	print cmd


pipe = open('/dev/input/js0','r')
action = []
spacing = 0
mouse_rate = 3

while 1:
	for character in pipe.read(1):
		action += ['%02X' % ord(character)]
		if len(action) == 8:

			num = int(action[5], 16) # Translate back to integer form
			percent254 = str(((float(num)-128.0)/126.0)-100)[4:6] # Calculate the percentage of push
			percent128 = str((float(num)/127.0))[2:4]

			if percent254 == '.0':
				percent254 = '100'
			if percent128 == '0':
				percent128 = '100'

			if action[6] == '01': # Button
				
				if action[4] == '01':
					print 'You pressed button: ' + action[7]
					
					if int(action[7]) == 3:
						mouse_s("mousedown 1")
						
					if int(action[7]) == 1:
						mouse_s("mousedown 3")
						
					if int(action[7]) == 0:
						mouse("click 4")
						
					if int(action[7]) == 2:
						mouse("click 5")

				else:
					print 'You released button: ' + action[7]
					
					if int(action[7]) == 3:
						#break_event()
						mouse_s("mouseup 1")
					if int(action[7]) == 1:
						break_event()
						mouse_s("mouseup 3")
					if int(action[7]) == 0:
						break_event()
						#mouse_s("mouseup 4")
					if int(action[7]) == 2:
						break_event()
						#mouse_s("mouseup 5")

			elif action[7] == '00': # D-pad left/right
				if action[4] == 'FF':
					print 'You pressed right on the D-pad'
					mouse("mousemove_relative "+str((mouse_rate))+" 0")
				elif action[4] == '01':
					print 'You pressed left on the D-pad'
					mouse("mousemove_relative -- "+str((-1*mouse_rate))+" 0")
				else:
					print 'You released the D-pad'
					break_event()


			elif action[7] == '01': # D-pad up/down
				if action[4] == 'FF':
					print 'You pressed down on the D-pad'
					mouse("mousemove_relative 0 "+str((mouse_rate)))
				elif action[4] == '01':
					print  'You pressed up on the D-pad'
					mouse("mousemove_relative -- 0 "+str((-1*mouse_rate)))
				else:
					print 'You released the D-pad'
					break_event()


			elif action[7] == '04': # Left Joystick left/right
				if action[4] == 'FF':
					print 'You pressed right on the left joystick'
				elif action[4] == '01':
					print 'You pressed left on the left joystick'
				else:
					print 'You released the left joystick'

			elif action[7] == '05': # Left Joystick up/down
				if action[4] == 'FF':
					print 'You pressed down on the left joystick'
				elif action[4] == '01':
					print 'You pressed up on the left joystick'
				else:
					print 'You released the left joystick'

			elif action[7] == '02': # Right Joystick left/right
				num = int(action[5], 16) # Translate back into integer form
				if num >= 128:
					print 'You moved the right joystick left to %' + percent254
				elif num <= 127 \
				and num != 0:
					du=0
					#print 'You moved the right joystick right to %' + percent128
				else:
					print 'You stopped moving the right joystick'

			elif action[7] == '03': # Right Joystick up/ down
				if num >= 128:
					print 'You moved the right joystick upward to %' + percent254
				elif num <= 127 \
				and num != 0:
					print 'You moved the right joystick downward to %' + percent128
				else:
					print 'You stopped moving the right joystick' 
			action = []



