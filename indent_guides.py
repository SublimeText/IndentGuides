import sublime
import sublime_plugin

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
    
    spaces_per_tab = int(view.settings().get("tab_size"))
    flush_guides = int(bool(view.settings().get("indent_guides_flush_with_text")))
    all_indents = view.find_all("^(" + (" " * spaces_per_tab) + ")*")
    regions = []
    for spaces in all_indents:
      for i in range(0, len(spaces)/spaces_per_tab + flush_guides):
        tab_location = spaces.begin() + spaces_per_tab * i
        regions.append(sublime.Region(tab_location,tab_location))
    view.add_regions("IndentGuidesListener", regions, "comment", sublime.DRAW_EMPTY)
  
  def on_load(self, view):
    self.bust_it_out(view)
  def on_activated(self, view):
    self.bust_it_out(view)
  def on_modified(self, view):
    self.bust_it_out(view)
