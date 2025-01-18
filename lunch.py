 #!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import datetime
import html
import requests

HORIZ = "─"
VERT = "│"
U_L = "┌"
U_R = "┐"
L_L = "└"
L_R = "┘"

MONDAY = 1
TUESDAY = 2
WEDNESDAY = 3
THURSDAY = 4
FRIDAY = 5

WEEKDAYS = [MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY]

class InspiraScraper():
    url = "https://restauranginspira.se"
    title = "[Restaurang Inspira]"

    def __init__(self):
        self.scrape()

    def scrape(self):
        self.day_titles = {}
        self.day_dishes = {}

        try:
            self.site = requests.get(self.url, timeout=5).text
        except requests.ConnectTimeout:
            for day in WEEKDAYS:
                self.day_titles[day] = "Restaurang Inspira did not respond in time"
                self.day_dishes[day] = [("","")*5]
            return

        day_menus = self.site.split("lunchmeny_wrapper")
        for day in WEEKDAYS:
            self.day_titles[day] = day_menus[day-1].split("""<h3 class="elementor-heading-title elementor-size-default">""")[-1].split("</h3>")[0]
            self.day_dishes[day]=[]
            dishes = day_menus[day].split("""<div class="lunchmeny_container">""")
            for dish in dishes[1:]:
                try:
                    name = html.unescape(dish.split("</span>")[0].split(">")[1])
                    description = dish.split("""<div class="lunch_desc">""")[1].split("</div>")[0]
                    self.day_dishes[day].append((name, description))
                except IndexError:
                    pass

    def get_day_title(self, day):
        return self.day_titles[day]

    def get_day_dishes(self, day):
        return self.day_dishes[day]

def display(title, lines, window):
    if ((curses.COLS-2-len(title)) % 2) != 0:
        title = title + HORIZ
    spacing = HORIZ * int((curses.COLS-2-len(title))/2)
    window.addstr(U_L+spacing+title+spacing+U_R)

    for _ in range(int((curses.LINES-len(lines)-2)/2)+((curses.LINES-len(lines)-2)%2)):
        print_center("", None, window)

    for text, attr in lines:
        print_center(text, attr, window)

    for _ in range(int((curses.LINES-len(lines)-2)/2)):
        print_center("", None, window)

    window.insstr(L_L+HORIZ*(curses.COLS-2)+L_R)

    window.refresh()

def print_center(text, attr, window):
    if ((curses.COLS-2-len(text)) % 2) != 0:
        text = text + " "
    if len(text)>(curses.COLS-2):
        text = text[:curses.COLS-5]+"..."
    spacing = " " * int((curses.COLS-2-len(text))/2)
    if attr is None:
        window.addstr(VERT+spacing+text+spacing+VERT)
    else:
        window.addstr(VERT)
        window.addstr(spacing+text+spacing, attr)
        window.addstr(VERT)

def run(stdscr):
    scraper = InspiraScraper()

    valid_keys = ["KEY_LEFT", "KEY_RIGHT", "q", "Q", "KEY_RESIZE"]

    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)

    selected_day = min(datetime.datetime.today().weekday(), 5)

    window = curses.newwin(curses.LINES, curses.COLS)
    window.keypad(1)
    window.scrollok(True)

    week = datetime.datetime.today().isocalendar()[1]

    while True:
        if week != datetime.datetime.today().isocalendar()[1]:
            scraper.scrape()
            selected_day = min(datetime.datetime.today().weekday(), 5)
            week = datetime.datetime.today().isocalendar()[1]

        curses.update_lines_cols()
        window.resize(curses.LINES, curses.COLS)
        curses.curs_set(0)

        lines = []

        lines.append((scraper.get_day_title(selected_day), curses.color_pair(2)|curses.A_BOLD))
        lines.append(("", None))

        for dish in scraper.get_day_dishes(selected_day):
            lines.append((dish[0], curses.color_pair(1)|curses.A_BOLD))
            lines.append((dish[1], None))

            lines.append(("", None))

        display(scraper.title, lines, window)

        keypress = window.getkey()
        while(not keypress in valid_keys and not repr(keypress) in valid_keys):
            keypress = window.getkey()

        if keypress == "KEY_RIGHT" and (selected_day != 5):
            selected_day += 1
        elif keypress == "KEY_LEFT" and (selected_day != 1):
            selected_day -= 1
        elif keypress in ["q", "Q"]:
            return


curses.wrapper(run)
