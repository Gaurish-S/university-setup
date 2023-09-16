#!/usr/bin/python3

import os
from datetime import datetime
from pathlib import Path
import locale
import re
import subprocess


from config import get_week, DATE_FORMAT, CURRENT_COURSE_ROOT

# TODO
locale.setlocale(locale.LC_TIME, "nl_BE.utf8")


def number2filename(n):
    return 'tut_{0:02d}.tex'.format(n)

def filename2number(s):
    return int(str(s).replace('.tex', '').replace('tut_', ''))

class Tutorial():
    def __init__(self, file_path, course):
        with file_path.open() as f:
            for line in f:
                tutorial_match = re.search(r'tutorial\{(.*?)\}\{(.*?)\}\{(.*)\}', line)
                if tutorial_match:
                    break;

        # number = int(tutorial_match.group(1))

        date_str = tutorial_match.group(2)
        date = datetime.strptime(date_str, DATE_FORMAT)
        week = get_week(date)

        title = tutorial_match.group(3)

        self.file_path = file_path
        self.date = date
        self.week = week
        self.number = filename2number(file_path.stem)
        self.title = title
        self.course = course

    def edit(self):
        print(str(self.file_path))
        subprocess.Popen([
            "alacritty",
            "-e", "nvim",
            f"{str(self.file_path)}"
        ])

    def __str__(self):
        return f'<Tutorial {self.course.info["short"]} {self.number} "{self.title}">'


class Tutorials(list):
    def __init__(self, course):
        self.course = course
        self.root = course.path
        self.master_file = self.root / 'master.tex'
        list.__init__(self, self.read_files())

    def read_files(self):
        files = self.root.glob('tut_*.tex')
        return sorted((Tutorial(f, self.course) for f in files), key=lambda l: l.number)

    def parse_tutorial_spec(self, string):
        if len(self) == 0:
            return 0

        if string.isdigit():
            return int(string)
        elif string == 'last':
            return self[-1].number
        elif string == 'prev':
            return self[-1].number - 1

    def parse_range_string(self, arg):
        all_numbers = [tutorial.number for tutorial in self]
        if 'all' in arg:
            return all_numbers

        if '-' in arg:
            start, end = [self.parse_tutorial_spec(bit) for bit in arg.split('-')]
            return list(set(all_numbers) & set(range(start, end + 1)))

        return [self.parse_tutorial_spec(arg)]

    @staticmethod
    def get_header_footer(filepath):
        part = 0
        header = ''
        footer = ''
        with filepath.open() as f:
            for line in f:
                # order of if-statements is important here!
                if 'end tutorials' in line:
                    part = 2

                if part == 0:
                    header += line
                if part == 2:
                    footer += line

                if 'start tutorials' in line:
                    part = 1
        return (header, footer)

    def update_tutorials_in_master(self, r):
        header, footer = self.get_header_footer(self.master_file)
        body = ''.join(
            ' ' * 4 + r'\input{' + number2filename(number) + '}\n' for number in r)
        self.master_file.write_text(header + body + footer)

    def new_tutorial(self):
        if len(self) != 0:
            new_tutorial_number = self[-1].number + 1
        else:
            new_tutorial_number = 1

        new_tutorial_path = self.root / number2filename(new_tutorial_number)

        today = datetime.today()
        date = today.strftime(DATE_FORMAT)

        new_tutorial_path.touch()
        new_tutorial_path.write_text(f'\\tutorial{{{new_tutorial_number}}}{{{date}}}{{}}\n')

        if new_tutorial_number == 1:
            self.update_tutorials_in_master([1])
        else:
            self.update_tutorials_in_master([new_tutorial_number - 1, new_tutorial_number])

        self.read_files()


        l = Tutorial(new_tutorial_path, self.course)

        return l

    def compile_master(self):
        result = subprocess.run(
            ['latexmk', '-f', '-interaction=nonstopmode', str(self.master_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(self.root)
        )
        return result.returncode
