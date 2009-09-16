#!BPY
# -*- coding: utf-8 -*-

from event_handler import *
import Blender
from Blender import Draw



class Widget:
	"""
	Wrapper class for the Blender widgets
	"""
	def __init__(self, name, size = None, callback = None, callback_args = None, update_function = None, update_args = None):
		"""
		Creates a new Widget parented to Panel parent. If size is passed it will override
		the widget size specified by the parent. callback and callback_args will be triggered when an event is
		triggered by this widget. update_function and update_args will be called on each render call. Both
		callback and update_functions should take their first argument as the calling object.
		"""

		self.event = EventHandler.add_widget(self)
		self.parent = None
		self.name = name
		self.size = size
		self.blender_widget = Draw.Create(0)
		self.callback = callback
		self.callback_args = callback_args
		self.value = 0
		self.update_function = update_function
		self.update_args = update_args

	def update(self):
		if self.update_function:
			self.update_function(self)

	def draw(self, x, y, width, height):
		pass

	def set_size(self, width, height):
		self.width = width
		self.height = height

	def handle_event(self):
		if self.callback:
			if self.callback_args:
				self.callback(self, *self.callback_args)
			else:
				self.callback(self)

	def __str__(self):
		return self.name

	def __repr__(self):
		return self.name

	def make_parent(self, parent):
		self.parent = parent

	def clear_parent(self):
		self.parent.remove(self)
		self.parent = None
		
class Button(Widget):
	"""
	Basic button widget, creates a pushbutton
	"""
	
	def draw(self, x, y, width, height):
		#print self.name, x, y
		self.blender_widget = Draw.PushButton(self.name, self.event, x, y, width, height, "Ara")

class Toggle(Widget):
	"""
	A togglebutton.
	"""
	def draw(self, x, y, width, height):
		#print self.name, x, y
		self.blender_widget = Draw.Toggle(self.name, self.event, x, y, width, height, self.value, "Ara")

	def handle_event(self):
		self.value = self.blender_widget.val
		Widget.handle_event(self)

class Integer(Widget):
	def __init__(self, name, size = None, callback = None, callback_args = None, update_function = None, update_args = None, min = 0, max = 10):
		Widget.__init__(self, name, size, callback, callback_args, update_function, update_args)
		self.value = int(self.value)
		self.min = int(min)
		self.max = int(max)
		
	def draw(self, x, y, width, height):
		self.blender_widget = Draw.Number(self.name, self.event, x, y, width, height, int(self.value), self.min, self.max)

class Float(Widget):
	def __init__(self, name, size = None, callback = None, callback_args = None, update_function = None, update_args = None, min = 0, max = 10):
		Widget.__init__(self, name, size, callback, callback_args, update_function, update_args)
		self.value = float(self.value)
		self.min = float(min)
		self.max = float(max)
		
	def draw(self, x, y, width, height):
		self.blender_widget = Draw.Number(self.name, self.event, x, y, width, height, float(self.value), self.min, self.max)


class StringEntry(Widget):
	def __init__(self, name, size = None, callback = None, callback_args = None, update_function = None, update_args = None):
		Widget.__init__(self, name, size, callback, callback_args, update_function, update_args)
		self.value = ""
		
	def draw(self, x, y, width, height):
		#print self.name, self.event, x, y, width, height, self.value, 255
		self.blender_widget = Draw.String(self.name, self.event, x, y, width, height, self.value, 255)


		
class Menu(Widget):
	def __init__(self, name, size = None, callback = None, callback_args = None, update_function = None, update_args = None, menuitems = {}):
		Widget.__init__(self, name, size, callback, callback_args, update_function, update_args)
		self.menuitems = menuitems # menuitems is a dictionary with "Title" : value, where "title" is the items displayed in the menu
		self.menukeys = self.menuitems.keys() #the list is constructed to be deterministic
		self.current_item = 0
		if self.menuitems:
			self.value = self.menukeys[0]
		

	def draw(self, x, y, width, height):
		menu_text = "%t" + self.name
		for i,item in enumerate(self.menukeys):
			menu_text += "|" + item + "%x" + str(i)
			
		self.blender_widget = Draw.Menu(menu_text, self.event, x, y, width, height, self.current_item, "Ara")

	def handle_event(self):
		self.current_item = self.blender_widget.val
		self.value = self.menuitems[self.menukeys[self.current_item]] #first it looks up the string key from menukeys, then uses that string as key in the menuitems dict
		Widget.handle_event(self)

class MenuNamed(Menu):
	def draw(self, x, y, width, height):
		string_width = Draw.GetStringWidth(self.name) + 20
		Draw.Label(self.name, x, y, string_width, height)	
		Menu.draw(self, x + string_width, y, width - string_width, height)

class TextLabel(Widget):

	def draw(self, x, y, width, height):
		Draw.Label(self.name, x, y, width, height)


class ColorPicker(Widget):
	def __init__(self, name, size = None, callback = None, callback_args = None, update_function = None, update_args = None, color = [0.0,0.0,0.0], picker_rect = None):
		Widget.__init__(self, name, size, callback, callback_args, update_function, update_args)
		self.value = color
		self.picker_rect = picker_rect

	def draw(self, x, y, width, height):
		Widget.draw(self, x, y, width, height)
		if self.picker_rect:
			picker_width, picker_height = self.picker_rect
			self.blender_widget = Draw.ColorPicker(self.event, x, y, picker_width, picker_height, tuple(self.value), "Ara")
		else:
			self.blender_widget = Draw.ColorPicker(self.event, x, y, width, height, tuple(self.value), "Ara")

	def handle_event(self):
		self.value = self.blender_widget.val
		Widget.handle_event(self)


class ColorPickerNamed(ColorPicker):
	def draw(self, x, y, width, height):
		string_width = Draw.GetStringWidth(self.name) + 20
		Draw.Label(self.name, x, y, string_width, height)

		if self.picker_rect:
			picker_width, picker_height = self.picker_rect
			xpos = x + width - picker_width 
			#self.blender_widget = Draw.ColorPicker(self.event, xpos, y, picker_width, picker_height, tuple(self.value), "Ara")
			ColorPicker.draw(self, xpos, y, picker_width, picker_height)
		else:
			ColorPicker.draw(self, x + string_width, y, width - string_width, height)
		

class Panel(Widget):
	"""
	Class to organize widgets in the blender GUI.
	If no parent is defined, the panel is considered a root panel.
	"""
	resize_horizontally = False #what direction the widgets are drawn, if its true it means they are drawn left to right, bottom down. If it's set to false, they're drawn top to bottom, left to right
	table = [] #the table as a matrix of widget-objects laid out like:
				#[
				#[row_1_column_1, row_1_column_2 ... row_1_column_n],
				#[row_2_column_1, row_2_column_2 ... row_2_column_n],
				#... ,
				#[row_n_column_1, row_n_column_2 ... row_n_column_n]
				#]
	
	def __init__(self, name, columns, rows, widget_size = None, size = None, padding = (0,0), is_root = False, color = None):
		"""
		Creates a new Panel object inside object parent (should be another panel or None).
		If the optional argument widget_size is given, contained widgets will be constrained to these dimensions (doesn't affect contained panels though).
		If a widget has it's own size set, it will override the panels widget_size.
		padding will insert space between cells in the table.
		"""
		Widget.__init__(self, name, size)
		self.rows = rows
		self.columns = columns
		self.widget_size = widget_size
		self.is_root = is_root #is this a root-panel?
		self.padding = padding 

		self.row_heights = [0 for row in range(self.rows)]
		self.column_widths = [0 for col in range(self.columns)]

		self.update_size()
		self.color = None
		#create the matrix that represents this table
		self.table = [[None for column in range(self.columns)] for row in range(self.rows)]
		self.original_size = (self.columns, self.rows)
		print self.table

	def make_parent(self, parent):
		Widget.make_parent(self, parent)
		self.is_root = False
		if not self.widget_size:
			self.widget_size = parent.widget_size
		print self.name, self.widget_size

		#propagate to contained widgets
		for row in self.table:
			for cell in row:
				if cell:
					cell.make_parent(self)

	def clear_parent(self):
		Widget.clear_parent(self)
		self.is_root = False

	def remove(self, ob, count = 0):
		"""
		Will remove count instances of the widget ob from this panel. If count
		is 0, it will remove all instances.
		"""
		if count == 0:
			for i,row in enumerate(self.table):
				for j, cell in enumerate(row):
					if cell == ob:
						self.table[i][j] = None

		elif count > 0:
			for i,row in enumerate(self.table):
				for j, cell in enumerate(row):
					if cell == ob:
						self.table[i][j] = None
						count -= 1
						if count == 0:
							return
							
	def remove_all(self):
		"""
		Will remove all objects from this panel. Will reset the panel to it's original size.
		"""
		self.columns, self.rows = self.original_size
		self.table = [[None for column in range(self.columns)] for row in range(self.rows)]
		self.update_size()

	def get_alloted_space(self, widget):
		"""
		Returns how much space the passed widget is allowed to use.
		"""
		if self.columns:
			widget_width = self.size[0]/self.columns
		else:
			widget_width = self.size[0]

		if self.rows:
			widget_height = self.size[1]/self.rows
		else:
			widget_height = self.size[1]
		return (widget_width, widget_height)

	def add_row(self, height = 0):
		"""
		Adds a new row to the end of the table.
		"""
		self.table.append([None for column in range(self.columns)])
		self.rows += 1
		self.row_heights.append(height)

	def add_column(self, width = 0):
		"""
		Adds a new column to the end of the table.
		"""
		for row in self.table:
			row.append(None) #append an empty element to every row
		self.columns += 1
		self.column_widths.append(width)
		
	def add(self, widget, pos = None):
		"""
		Adds a widget to the panel at pos. Pos should be a sequence like (col, row) were col and row are non-negative
		integers. If a widget is already in the position it will get overwritten with the new one.
		"""

		widget.make_parent(self)
		
		if pos:
			x, y = pos
			if x > self.columns - 1:
				columns_to_add = self.columns -1 -x
				for count in range(columns_to_add):
					self.add_column()
				
			if y > self.rows - 1:
				rows_to_add = self.rows -1 -x
				for count in range(rows_to_add):
					self.add_row()

			self.table[y][x] = widget #the rows are the outer list

		else: #no pos argument passed, insert at first empty cell
			empty_cell = self.get_widget_pos(None) #return the first cell-position with the value None
			if not empty_cell: #no available cells, resize table according to self.resize_horizontally
				if self.resize_horizontally:
					#when using horizontal layout, new columns are added
					self.add_column()
				else:
					#using vertical layout, a new row is added
					self.add_row()
				
				#now there should be available cells
				empty_cell = self.get_widget_pos(None)
				
			col, row = empty_cell
			self.table[row][col] = widget
				
		#after a widget has been added, we update the lists of column widths and row heights
		self.update_size()


	def insert(self, widget, pos):
		widget.make_parent(self)
		x, y = pos
		if x > self.columns - 1:
			columns_to_add = self.columns -1 -x
			for count in range(columns_to_add):
				self.add_column()
			
		if y > self.rows - 1:
			rows_to_add = self.rows -1 -x
			for count in range(rows_to_add):
				self.add_row()
		print "inserting", self.table
		self.table[y][x] = widget #the rows are the outer list
		print "after insert", self.table
	

	def get_widget_pos(self, widget):
		"""
		Returns the position as a tuple (col, row) for the first occurance of widget
		in the table.
		"""
		for i,row in enumerate(self.table):
			for j, cell in enumerate(row):
				if cell == widget:
					return (j, i)

		return None

		
	def update_size(self):
		"""
		Update the different size values for the Panel.
		"""
		
		self.row_heights = [0 for row in range(self.rows)]
		self.column_widths = [0 for col in range(self.columns)]

		#first update the sizes of rows and columns
		for i,row in enumerate(self.table):
			for j, cell in enumerate(row):
				if cell:
					cell_width, cell_height = 0,0

					if cell.size:
						cell_width, cell_height = cell.size

					elif self.widget_size:
						cell_width, cell_height = self.widget_size

					if self.row_heights[i] < cell_height:
						self.row_heights[i] = cell_height
						
					if self.column_widths[j] < cell_width:
						self.column_widths[j] = cell_width

		if self.is_root:
			#if this is a root panel, it will claim the whole windows area
			self.size = Blender.Window.GetAreaSize()
			return
		
		padd_x, padd_y = self.padding
		table_width = sum(self.column_widths) + padd_x * self.columns
		table_height = sum(self.row_heights) + padd_y * self.rows
		
		self.size = [table_width, table_height]
		
		
		
	def update(self):
		for row in self.table:
			for cell in row:
				if cell:
					cell.update()

		self.update_size()
	
	def draw(self, x, y, width, height):
		"""
		Draws this panel and its children at the given position with the passed width and height.
		"""
		if self.color:
			glColor3f(*color)
			Blender.BGL.glRecti(x,y, x+width, y+height)

		#blender counts x, y = 0,0 as being in the bottom-left corner
		padd_x, padd_y = self.padding
		xpos = x + padd_x
		ypos = y - padd_y
		ypos += height #add own height for starting position, start in top left corner instead of bottom left
		
		for i,row in enumerate(self.table):
			xpos = x + padd_x # reset the xpos to the beginning of the row
			for j, widget in enumerate(row):
				if widget:
					if widget.size:
						widget.draw(xpos, ypos - widget.size[1], *widget.size)
					else:
						print self
						widget.draw(xpos, ypos - self.widget_size[1], *self.widget_size)
					#print widget.name, xpos,ypos
				xpos += self.column_widths[j] + padd_x #adds the current column width to the draw offset
				
			ypos -= (self.row_heights[i] + padd_y) #remove the current row height from ypos

		
class TogglePanel(Panel):
	def __init__(self, name, columns, rows, widget_size = None, size = None, padding = (0,0), is_root = False, color = None, toggle = 1):
		"""
		Creates a new Panel object inside object parent (should be another panel or None).
		If the optional argument widget_size is given, contained widgets will be constrained to these dimensions (doesn't affect contained panels though).
		If a widget has it's own size set, it will override the panels widget_size.
		padding will insert space between cells in the table.
		"""
		print "Init in TogglePanel"
		self.toggle = Draw.Create(0)
		self.toggle.val = toggle
		Panel.__init__(self, name, columns, rows, widget_size, size, padding, is_root, color)
		
		print "Ara", self.toggle

	def update_size(self):
		if self.widget_size:
			widget_width, widget_height = self.widget_size
		else:
			widget_width, widget_height = 0,0
			
		if self.toggle.val:
			Panel.update_size(self)
			self.size = [self.size[0], self.size[1] + widget_height] #adds space for the toggle button
		else:
			self.size = (widget_width, widget_height) #the panel is hidden

	def draw(self, x, y, width, height):
		if self.widget_size:
			widget_width, widget_height = self.widget_size
		else:
			widget_width, widget_height = 0,0
			
		padd_x, padd_y = self.padding
		xpos = x + padd_x
		ypos = y - padd_y + height
		self.toggle = Draw.Toggle(self.name, self.event, xpos, ypos - widget_height, widget_width, widget_height, self.toggle.val) 

		if self.toggle.val:
			Panel.draw(self, x, y, width, height - widget_height)
		

class FileBrowser(Widget, Button):
	"""
	Creates a Composite widget with a stringentry and button. Pressing the button will open a fileselector window.
	"""
	def __init__(self, name, size = None, callback = None, callback_args = None, update_function = None, update_args = None, browse_title = None, default_path = ""):
		Widget.__init__(self, name, size, callback, callback_args, update_function, update_args)
		self.browse_button = Button("Browse", callback = self.browse_button_callback) # a button to open a fileselector window
		self.value = default_path

		self.browse_title = browse_title
		
	def update(self):
		if self.update_function:
			self.update_function(self)

	def draw(self, x, y, width, height):
		browse_string_width = Draw.GetStringWidth("Browse", "normalfix") + 10
		print self.name, self.event, x, y, width - browse_string_width, height, self.value, 128
		self.blender_widget = Draw.String(self.name, self.event, x, y, width - browse_string_width, height, self.value, 128)
		self.browse_button.draw(x + width - browse_string_width, y, browse_string_width, height)

	def handle_event(self):
		self.value = self.blender_widget.val
		Widget.handle_event(self)

	def browse_button_callback(self, caller):
		if self.browse_title:
			Blender.Window.FileSelector(self.fileselector_callback, self.browse_title, self.value)
		else:
			Blender.Window.FileSelector(self.fileselector_callback, self.value)
		
	def fileselector_callback(self, filename_str):
		self.value = filename_str

class DirectoryBrowser(FileBrowser):
	def __init__(self, name, size = None, callback = None, callback_args = None, update_function = None, update_args = None, browse_title = None):
		FileBrowser.__init__(self, name, size, callback, callback_args, update_function, update_args)
		self.browse_button = Button("Browse", callback = self.browse_button_callback) # a button to open a fileselector window
		self.value = ""
		self.browse_title = "Select Directory"

	def fileselector_callback(self, filename_str):
		#strip any filename from the path
		self.value = Blender.sys.dirname(filename_str)
		
