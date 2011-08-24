"""
PLACEMENT OPTIONS
	"flush_with_text": true
		if you want your guides to be drawn all the way up to the text, add this to
		your user file preferences.

	"flush_with_gutter": true
		if you want your guides to be drawn all the way to the gutter, add this to
		your user file preferences.

	"max_file_characters": 524288
		if you want to limit the size of files that will be processed by this
		plugin, add this to your user file preferences with any number you like.

COLOR OPTIONS
	"color_scope_name" : "guide"
		Normally the color of the guides is the same as the color of comments in
		your code. If you'd like to customize the color, add the below to your color
		scheme file and change EDF2E9 to whatever color you want, then add this to
		your user file preferences. (thanks to theblacklion)
---ADD TEXT BELOW THIS LINE TO YOUR COLOR SCHEME FILE---
			<dict>
					<key>name</key>
					<string>Guide</string>
					<key>scope</key>
					<string>guide</string>
					<key>settings</key>
					<dict>
						<key>foreground</key>
						<string>#EDF2E9</string>
				 </dict>
			</dict>
---ADD TEXT ABOVE THIS LINE TO YOUR COLOR SCHEME FILE---
"""

import sublime
import sublime_plugin
import indentation
import re

DEFAULT_COLOR_SCOPE_NAME = "comment"
DEFAULT_MAX_FILE_CHARACTERS = 524288

def unload_handler():
	for window in sublime.windows():
		for view in window.views():
			view.erase_regions('IndentGuidesListener')

class IndentGuidesListener(sublime_plugin.EventListener):
	def __init__(self):
		#Files don't get their guides redrawn until they're activated or loaded,
		#so let's generate guides for the front file.
		#Views in other groups won't have their guides refreshed, but I don't
		#believe it's possible to find the active view in another group without
		#switching to that view.
		self.refresh(sublime.active_window().active_view(), whole_file=True)
	
	def find_regions_of_interest(self, view, whole_file):
		find_str = r"^(( )|(\t))+"
		if whole_file:
			regions_of_interest = view.find_all(find_str)
		else:
			regions_of_interest = []
			for s in view.sel():
				begin_row,_ = view.rowcol(s.begin())
				end_row,_ = view.rowcol(s.end())
				for row in xrange(begin_row,end_row+1):
					bol = view.text_point(row,0)
					m = re.search(find_str, view.substr(view.line(bol)))
					if m:
						regions_of_interest.append(sublime.Region(bol,bol + len(m.group(0))))
		return regions_of_interest
	
	def get_current_guides(self, view, whole_file):
		if whole_file:
			guides = []
		else:
			guides = view.get_regions("IndentGuidesListener")
		return guides
	
	def file_is_small_enough(self, view):
		settings = sublime.load_settings('Indent Guides.sublime-settings')
		max_size = settings.get('max_file_characters')
		max_size = long(max_size or DEFAULT_MAX_FILE_CHARACTERS)
		if view.size() > max_size:
			print(__name__+": "+view.file_name()+" too long to process")
			return False
		return True
	
	def update_guides(self, view, regions_of_interest, guides):
		tab_size = indentation.get_tab_size(view)
		
		settings = sublime.load_settings('Indent Guides.sublime-settings')
		flush_with_text = int(bool(settings.get('flush_with_text')))
		flush_with_gutter = bool(settings.get('flush_with_gutter'))
		
		for roi in regions_of_interest:
			pos = 0
			for pt in xrange(roi.begin(), roi.end()):
				ch = view.substr(pt)
				if pos % tab_size == 0 and (flush_with_gutter or pos != 0):
					loc = pt
					guides.append(sublime.Region(loc,loc))
				if ch == '\t':
						pos += tab_size - (pos % tab_size)
				elif ch.isspace():
						pos += 1
				else:
						pos+=1
			if flush_with_text and pos % tab_size == 0:
				guides.append(sublime.Region(roi.end(),roi.end()))
		return guides
	
	def refresh(self, view, whole_file=False):
		if (not self.file_is_small_enough(view)):
			view.erase_regions('IndentGuidesListener')
			return
		
		regions_of_interest = self.find_regions_of_interest(view, whole_file)
		guides = self.get_current_guides(view, whole_file)
		guides = self.update_guides(view, regions_of_interest, guides)
		
		settings = sublime.load_settings('Indent Guides.sublime-settings')
		color_scope_name = settings.get('color_scope_name', DEFAULT_COLOR_SCOPE_NAME)
		view.add_regions("IndentGuidesListener", guides, color_scope_name, sublime.DRAW_EMPTY)
	
	def on_load(self, view):
		self.refresh(view, whole_file=True)
	def on_activated(self, view):
		self.refresh(view, whole_file=True)
	def on_modified(self, view):
		#we still need to do the whole file here because doing things like pasting
		#a block of code won't make the indent guides show up correctly
		self.refresh(view, whole_file=True)
