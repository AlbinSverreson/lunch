 #!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import requests
import html
import curses

def run(stdscr):

    inspira_site = requests.get("https://restauranginspira.se").text
    valid_keys = ["KEY_LEFT", "KEY_RIGHT", "q", "Q", "KEY_RESIZE"]

    HORIZ = "─"
    VERT = "│"
    U_L = "┌"
    U_R = "┐"
    L_L = "└"
    L_R = "┘"

    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)

    selected_day = datetime.datetime.today().weekday()
    if selected_day > 5:
        selected_day = 5

    window = curses.newwin(curses.LINES, curses.COLS)
    window.keypad(1)
    window.scrollok(True)

    week = datetime.datetime.today().isocalendar()[1]

    def display(lines):
        title = "[Restaurang Inspira]"
        if(((curses.COLS-2-len(title)) % 2) != 0):
            title = title + HORIZ
        spacing = HORIZ * int((curses.COLS-2-len(title))/2)
        window.addstr(U_L+spacing+title+spacing+U_R)

        for i in range(int((curses.LINES-len(lines)-2)/2)+((curses.LINES-len(lines)-2)%2)):
            print_center("", None)

        for text, attr in lines:
            print_center(text, attr)

        for i in range(int((curses.LINES-len(lines)-2)/2)):
            print_center("", None)

        window.insstr(L_L+HORIZ*(curses.COLS-2)+L_R)

        window.refresh()

    def print_center(text, attr):
        if(((curses.COLS-2-len(text)) % 2) != 0):
            text = text + " "
        if (len(text)>(curses.COLS-2)):
            text = text[:curses.COLS-5]+"..."
        spacing = " " * int((curses.COLS-2-len(text))/2)
        if attr == None:
            window.addstr(VERT+spacing+text+spacing+VERT)
        else:
            window.addstr(VERT)
            window.addstr(spacing+text+spacing, attr)
            window.addstr(VERT)


    while(True):
        if week != datetime.datetime.today().isocalendar()[1]:
            inspira_site = requests.get("https://restauranginspira.se").text
            selected_day = datetime.datetime.today().weekday()
            week = datetime.datetime.today().isocalendar()[1]

        curses.update_lines_cols()
        window.resize(curses.LINES, curses.COLS)
        curses.curs_set(0)

        lines = []

        day_menus = inspira_site.split("lunchmeny_wrapper")
        selected_day_menu = day_menus[selected_day+1]
        day_title = day_menus[selected_day].split("""<h3 class="elementor-heading-title elementor-size-default">""")[-1].split("</h3>")[0]
        lines.append((day_title, curses.color_pair(2)|curses.A_BOLD))
        lines.append(("", None))

        dishes = selected_day_menu.split("""<div class="lunchmeny_container">""")

        for dish in dishes[1:]:
            try:
                name = dish.split("</span>")[0].split(">")[1]
                lines.append((html.unescape(name), curses.color_pair(1)|curses.A_BOLD))

                ingr_list = dish.split("""<div class="lunch_desc">""")[1].split("</div>")[0]
                ingredients = ingr_list.strip()
                lines.append((ingredients, None))
            except IndexError:
                pass

            lines.append(("", None))

        display(lines)

        keypress = window.getkey()
        while(not keypress in valid_keys and not repr(keypress) in valid_keys):
            keypress = window.getkey()

        if(keypress == "KEY_RIGHT" and (selected_day != 4)):
            selected_day += 1
        elif(keypress == "KEY_LEFT" and (selected_day != 0)):
            selected_day -= 1
        elif(keypress == "q" or keypress == "Q"):
            return


curses.wrapper(run) 
