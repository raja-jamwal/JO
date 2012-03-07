#
#	(C) Raja Jamwal <linux1@zoho.com>
# 
#  	JO is joystick to mouse emulator
#
# 
#

import sys
import commands
import thread
import threading
import time

import string
import bisect

import pygtk
pygtk.require('2.0')
import gtk, sys, cairo
gtk.threads_init()

break_b = False

letters = string.lowercase
numbers = '00000011111122222233333333'
letter_mapping = dict(zip(letters, numbers))
print letter_mapping

liststore = gtk.ListStore(str)

class predict_word:
	
	def __init__(self):
		self.read_dict()

	def word_to_num(self, word):
        	nums=''
        	for letter in word:
            		if letter in letter_mapping:
               			nums += letter_mapping[letter]
        	return nums

	def read_dict(self):
		words = []
		for line in file("dict"):
			word = line.strip().lower()
			nums = self.word_to_num(word)
			words.append((nums, word))
		words.sort()
		self.dict = words
	def get_match(self, number_str):
        	tup = (number_str,)
        	left = bisect.bisect_left(self.dict,   tup)

        	for num, word in self.dict[left:]:
            		if num.startswith(number_str):
                		yield word
            		else:
                		break

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

pd = predict_word()
view = None
win = None
tree_select = 0

def show_predict(num):
	print num
	liststore.clear()
	pred = list(pd.get_match(num))
	for i in range(0, len(pred) if len(pred)<15 else 15):
		liststore.append([pred[i]])		

def thread_main():
 global tree_select
 pipe = open('/dev/input/js0','r')
 action = []
 spacing = 0
 mouse_rate = 3
 mode_type = False
 mode_sel = False

 word_num = ""

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
					button = int(action[7])

					if int(action[7]) == 5:
						mode_sel=True
						print mode_sel

					if int(action[7]) == 4:
						mode_type=True
						print mode_type
					
					if int(action[7]) == 3:
						if mode_type==True:
							word_num += str(button)
							show_predict(word_num)
						elif mode_sel == True:
							selection = view.get_selection()
							entry1, entry2 = selection.get_selected()
							if entry2 != None:
								entry = entry1.get_value(entry2, 0)
								mouse_s("type '"+str(entry)+"'")
								print entry
							word_num = ""
						else:
							mouse_s("mousedown 1")
							
					if int(action[7]) == 1:

						if mode_type==True:
							word_num += str(button)
							show_predict(word_num)
						elif mode_sel == True:
							mouse_s("key KP_Enter") 
						else:
							mouse_s("mousedown 3")
							

					if int(action[7]) == 0:

						if mode_type==True:
							word_num += str(button)
							show_predict(word_num)
						elif mode_sel == True:
							mouse_s("type ' '")
						else:
							mouse("click 4")

					if int(action[7]) == 2:
						if mode_type==False:
							mouse("click 5")
						else:
							word_num += str(button)
							show_predict(word_num)
					if int(action[7]) == 7:	
						# model, iter
						selection = view.get_selection()
						entry1, entry2 = selection.get_selected()
						if entry2 != None:
							entry = entry1.get_value(entry2, 0)
							print entry
							selection.select_path(str(tree_select))
							#view.scroll_to_cell(path, None, 2, 0)
							#win.hide()
							#mouse_s("xdotool type '"+str(entry)+"'")
							#win.show_all()
						word_num = ""
				else:
					print 'You released button: ' + action[7]

					if int(action[7]) == 5:
						mode_sel=False
						print mode_sel

					if int(action[7]) == 4:
						mode_type=False
						print mode_type
					
					if int(action[7]) == 3:
						#break_event()
						if mode_sel == False:
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
					
					if mode_sel == True:
						selection = view.get_selection()
						tree_select = tree_select+1 if tree_select+1 <= len(liststore) else len(liststore)-1
						selection.select_path(str(tree_select))
					else:
						mouse("mousemove_relative 0 "+str((mouse_rate)))

				elif action[4] == '01':
					print  'You pressed up on the D-pad'
					if mode_sel == True:
						selection = view.get_selection()
						tree_select = tree_select-1 if tree_select-1 >= 0 else 0
						selection.select_path(str(tree_select))
					else:
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

#pygtk wonderland

def main (argc):
    global view
    global win
    win = gtk.Window()
    thread.start_new_thread(thread_main, ())

    #win.set_decorated(False)

    # Makes the window paintable, so we can draw directly on it
    #win.set_app_paintable(True)
    win.set_size_request(100, 500)

    vbox = gtk.VBox()
    label = gtk.Label(letters[0:6])

    hbox = gtk.VBox()
    label1 = gtk.Label(letters[6:12])
    label2 = gtk.Label(letters[12:18])
    hbox.pack_start(label1)
    hbox.pack_start(label2)
    
    label3 = gtk.Label(letters[18:26])
    vbox.pack_start(label)
    vbox.pack_start(hbox)
    vbox.pack_start(label3)

    view = gtk.TreeView(model=liststore)
    column = gtk.TreeViewColumn('T9')
    cell = gtk.CellRendererText()
    column.pack_start(cell)
    column.add_attribute(cell, 'text', 0)
    column.add_attribute(cell, 'background', 3)
    view.append_column(column)
    #view.connect('cursor-changed', treeview_sel)
    vbox.pack_start(view)
    win.add(vbox)

    # This sets the windows colormap, so it supports transparency.
    # This will only work if the wm support alpha channel
    #screen = win.get_screen()
    #rgba = screen.get_rgba_colormap()
    #win.set_colormap(rgba)

    #win.connect('expose-event', expose)

    win.show_all()
    gtk.main()

main("")


