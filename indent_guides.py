import sublime
import sublime_plugin
import indentation

#if you want the guides drawn, add this to your user file preferences:
#  "show_indent_guides": true

#if you want your guides to be drawn all the way up to the text, add this
#to your user file preferences:
#  "indent_guides_flush_with_text": true


def lines_in_buffer(view):
  #todo: maybe this is wrong? do i need size - 1?
  row, col = view.rowcol(view.size())
  #"row" is the index of the last row; need to add 1 to get number of rows
  return row + 1

class IndentGuidesListener(sublime_plugin.EventListener):
  def bust_it_out(self, view):
    if not view.settings().get("show_indent_guides"):
      view.add_regions("IndentGuidesListener", [], "comment", sublime.DRAW_EMPTY)
      return
    tab_size = indentation.get_tab_size(view)
    flush_guides = int(bool(view.settings().get("indent_guides_flush_with_text")))
    indent_regions = view.find_all(r"^(( )|(\t))+")
    regions = []
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
    view.add_regions("IndentGuidesListener", regions, "comment", sublime.DRAW_EMPTY)
  
  def on_load(self, view):
    self.bust_it_out(view)
  def on_activated(self, view):
    self.bust_it_out(view)
  def on_modified(self, view):
    self.bust_it_out(view)
