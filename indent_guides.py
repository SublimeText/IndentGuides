import sublime
import sublime_plugin
import indentation
import re

#if you want the guides drawn, add this to your user file preferences:
#  "show_indent_guides": true

#if you want your guides to be drawn all the way up to the text, add this
#to your user file preferences:
#  "indent_guides_flush_with_text": true

#Normally the color of the guides is the same as the color of comments
#in your code. If you'd like to customize the color, add this to your
#theme file and change EDF2E9 to whatever color you want, then change
#the scope variable, below, from "comment" to "guide".
#(thanks to theblacklion)
#---ADD TEXT BELOW THIS LINE TO YOUR THEME FILE---
#       <dict>
#          <key>name</key>
#          <string>Guide</string>
#          <key>scope</key>
#          <string>guide</string>
#          <key>settings</key>
#          <dict>
#             <key>fontStyle</key>
#             <string>italic</string>
#             <key>foreground</key>
#             <string>#EDF2E9</string>
#          </dict>
#       </dict>
#---ADD TEXT ABOVE THIS LINE TO YOUR THEME FILE---
scope = "comment"



class IndentGuidesListener(sublime_plugin.EventListener):
  def bust_it_out(self, view, whole_file=False):
    if not view.settings().get("show_indent_guides"):
      view.add_regions("IndentGuidesListener", [], scope, sublime.DRAW_EMPTY)
      return
    tab_size = indentation.get_tab_size(view)
    flush_guides = int(bool(view.settings().get("indent_guides_flush_with_text")))
    
    find_str = r"^(( )|(\t))+"
    if whole_file:
      regions = []
      indent_regions = view.find_all(find_str)
    else:
      regions = view.get_regions("IndentGuidesListener")
      indent_regions = []
      for s in view.sel():
        begin_row,_ = view.rowcol(s.begin())
        end_row,_ = view.rowcol(s.end())
        for row in xrange(begin_row,end_row+1):
          bol = view.text_point(row,0)
          m = re.search(find_str, view.substr(view.line(bol)))
          if m:
            indent_regions.append(sublime.Region(bol,bol + len(m.group(0))))
    
    for indent_region in indent_regions:
      pos = 0 
      for pt in xrange(indent_region.begin(), indent_region.end()):
        ch = view.substr(pt)
        if pos % tab_size == 0:
          loc = pt
          regions.append(sublime.Region(loc,loc))
        if ch == '\t':
            pos += tab_size - (pos % tab_size)
        elif ch.isspace():
            pos += 1 
        else:
            pos+=1
      if(flush_guides):
        regions.append(sublime.Region(indent_region.end(),indent_region.end()))
    view.add_regions("IndentGuidesListener", regions, scope, sublime.DRAW_EMPTY)
  
  def on_load(self, view):
    self.bust_it_out(view, whole_file=True)
  def on_activated(self, view):
    self.bust_it_out(view, whole_file=True)
  def on_modified(self, view):
    #we still need to do the whole file here because doing things like pasting
    #a block of code won't make the indent guides show up correctly
    self.bust_it_out(view, whole_file=True)
