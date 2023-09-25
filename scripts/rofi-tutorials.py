#!/usr/bin/python3
from courses import Courses
from rofi import rofi
from utils import generate_short_title, MAX_LEN

tutorials = Courses().current.tutorials
print(tutorials)

sorted_tutorials = sorted(tutorials, key=lambda l: -l.number)

options = [
    "{number: >2}. <b>{title: <{fill}}</b> <span size='smaller'>{date}  ({week})</span>".format(
        fill=MAX_LEN,
        number=tutorial.number,
        title=generate_short_title(tutorial.title),
        date=tutorial.date.strftime('%a %d %b'),
        week=tutorial.week
    )
    for tutorial in sorted_tutorials
]

key, index, selected = rofi('Select tutorial', options, [
    '-lines', 5,
    '-markup-rows',
    '-kb-row-down', 'Down',
    '-kb-custom-1', 'Ctrl+n'
])

if key == 0:
    sorted_tutorials[index].edit()
elif key == 1:
    new_tutorial = tutorials.new_tutorial()
    new_tutorial.edit()
