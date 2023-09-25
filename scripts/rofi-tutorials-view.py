#!/usr/bin/python3
from courses import Courses
from rofi import rofi

tutorials = Courses().current.tutorials

commands = ['last', 'prev-last', 'all', 'prev']
options = ['Current tutorial', 'Last two tutorials', 'All tutorials', 'Previous tutorials']

key, index, selected = rofi('Select view', options, [
    '-lines', 4,
    '-auto-select'
])

if index >= 0:
    command = commands[index]
else:
    command = selected

tutorial_range = tutorials.parse_range_string(command)
tutorials.update_tutorials_in_master(tutorial_range)
tutorials.compile_master()
