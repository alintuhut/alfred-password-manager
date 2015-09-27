on run argv
	set separator to "|--SPLITTER--|"
    set query to item 1 of argv
    if separator is in query then
		tell application "System Events"
		set frontApp to name of first application process whose frontmost is true
		set AppleScript's text item delimiters to separator
		set usr to text item 1 of query
		set pwd to text item 2 of query
		tell application "System Events" to keystroke usr
		tell application "System Events" to keystroke tab
		tell application "System Events" to keystroke pwd
		tell application "System Events" to keystroke return
		end tell
	else
		tell application "System Events" to keystroke query
	end if
end run