#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import datetime
import html
import re
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

class BaseScraper:
    "Parent class defining the required variables for a scraper"

    url: str
    title: str

    day_titles: dict[int, str]
    day_dishes: dict[int, (str, str)]

    def __init__(self):
        self.scrape()

    def scrape(self):
        "Scrapes the website and stores the relevant information"

    def get_restaurant_title(self):
        "Gets the name of the restaurant"
        return self.title

    def get_day_title(self, day):
        "Gets the name of the day on the menu"
        return self.day_titles[day]

    def get_day_dishes(self, day):
        "Gets a list of tuples containg a days menu item names and descriptions"
        return self.day_dishes[day]

class BrygganScraper(BaseScraper):
    "Class for scraping the Bryggan website"

    url = "https://mersmak.me/vara-stallen/bryggan/"
    title = "[Café Bryggan]"

    def scrape(self):
        self.day_titles = {}
        self.day_dishes = {}

        try:
            self.site = requests.get(self.url, timeout=5).text
        except requests.ConnectTimeout:
            for day in WEEKDAYS:
                self.day_titles[day] = "Café Bryggan did not respond in time"
                self.day_dishes[day] = [("","")*5]
            return

        day_menus = re.split("<p><b><i>|<p><b>", self.site)
        for day in WEEKDAYS:
            self.day_titles[day] = re.split("</i></b></p>|</b></p>", day_menus[day])[0]
            self.day_dishes[day]=[]
            dishes = day_menus[day].split('400;">')
            for dish in dishes[1:3]:
                try:
                    full_dish = html.unescape(dish.split("</span>")[0]).split(",")
                    name = full_dish[0]
                    description = ",".join(full_dish[1:])
                    self.day_dishes[day].append((name, description))
                except IndexError:
                    pass

class EdisonScraper(BaseScraper):
    "Class for scraping the Edison website"

    url = "https://restaurangedison.se"
    title = "[Restaurang Edison]"

    def scrape(self):
        self.day_titles = {}
        self.day_dishes = {}

        try:
            self.site = requests.get(self.url, timeout=5).text
        except requests.ConnectTimeout:
            for day in WEEKDAYS:
                self.day_titles[day] = "Restaurang Edison did not respond in time"
                self.day_dishes[day] = [("","")*5]
            return

        day_menus = self.site.split("lunchmeny_wrapper")
        for day in WEEKDAYS:
            self.day_titles[day] = day_menus[day-1]\
                                   .split('elementor-size-default">')[-1]\
                                   .split("</h3>")[0]
            self.day_dishes[day]=[]
            dishes = day_menus[day].split('<div class="lunchmeny_container">')
            for dish in dishes[1:]:
                try:
                    category = html.unescape(dish.split('lunch_title">')[1]\
                                                 .split("<")[0])\
                                                 .split(",")[0]
                    full_dish = dish.split('<div class="lunch_desc">')[1]\
                                    .split("</div>")[0].strip()\
                                    .split(",")
                    name = category + " | " + full_dish[0]
                    description = ",".join(full_dish[1:])

                    self.day_dishes[day].append((name, description))
                except IndexError:
                    pass

class InspiraScraper(BaseScraper):
    "Class for scraping the Inspira website"

    url = "https://restauranginspira.se"
    title = "[Restaurang Inspira]"

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
            self.day_titles[day] = day_menus[day-1]\
                                   .split('elementor-size-default">')[-1]\
                                   .split("</h3>")[0]
            self.day_dishes[day]=[]
            dishes = day_menus[day].split('<div class="lunchmeny_container">')
            for dish in dishes[1:]:
                try:
                    name = html.unescape(dish.split("</span>")[0].split(">")[1])
                    description = dish.split('<div class="lunch_desc">')[1]\
                                       .split("</div>")[0]

                    self.day_dishes[day].append((name, description))
                except IndexError:
                    pass

def display(title, lines, window):
    "Display a list of lines in a curses window with a title and a border around the edge"

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
    "Print some text styled with a curses attribute in the center of a curses window"
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
    "Main curses function"

    scrapers = [InspiraScraper(), EdisonScraper(), BrygganScraper()]
    selected_scraper = 0

    valid_keys = ["KEY_LEFT", "KEY_RIGHT", "KEY_UP", "KEY_DOWN", "q", "Q", "KEY_RESIZE"]

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
            for scraper in scrapers:
                scraper.scrape()
            selected_day = min(datetime.datetime.today().weekday(), 5)
            week = datetime.datetime.today().isocalendar()[1]

        scraper = scrapers[selected_scraper]

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

        display(scraper.get_restaurant_title(), lines, window)

        keypress = window.getkey()
        while(not keypress in valid_keys and not repr(keypress) in valid_keys):
            keypress = window.getkey()

        if keypress == "KEY_RIGHT" and (selected_day != 5):
            selected_day += 1
        elif keypress == "KEY_LEFT" and (selected_day != 1):
            selected_day -= 1
        elif keypress == "KEY_UP":
            if selected_scraper == len(scrapers)-1:
                selected_scraper = 0
            else:
                selected_scraper += 1
        elif keypress == "KEY_DOWN":
            if selected_scraper == 0:
                selected_scraper = len(scrapers)-1
            else:
                selected_scraper -= 1
        elif keypress in ["q", "Q"]:
            return


curses.wrapper(run)
