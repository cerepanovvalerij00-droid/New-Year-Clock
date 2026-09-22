
#!/usr/bin/env python3

import gi
import cairo
import json
import math
import random
import os
import subprocess
from datetime import datetime

gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")

from gi.repository import Gtk, GLib, Gdk, GtkLayerShell


TARGET = datetime(2027, 1, 1, 0, 0, 0)

WIDTH = 620
HEIGHT = 310

CONFIG_DIR = os.path.expanduser("~/.config/new-year-widget")
POSITION_FILE = os.path.join(CONFIG_DIR, "position.json")


# ============================================================
# POSITION
# ============================================================

def load_position():
    try:
        with open(POSITION_FILE, "r") as f:
            data = json.load(f)
            return int(data.get("x", 100)), int(data.get("y", 100))
    except Exception:
        return 100, 100


def save_position(x, y):
    os.makedirs(CONFIG_DIR, exist_ok=True)

    with open(POSITION_FILE, "w") as f:
        json.dump({
            "x": int(x),
            "y": int(y)
        }, f)


# ============================================================
# SNOW
# ============================================================

class Snowflake:

    def __init__(self):
        self.reset(True)

    def reset(self, first=False):

        self.x = random.uniform(5, WIDTH - 5)

        if first:
            self.y = random.uniform(0, HEIGHT)
        else:
            self.y = random.uniform(-20, -2)

        self.size = random.uniform(1.5, 4.0)
        self.speed = random.uniform(0.5, 1.5)
        self.wind = random.uniform(-0.25, 0.25)
        self.phase = random.uniform(0, math.pi * 2)
        self.opacity = random.uniform(0.45, 1.0)

    def update(self):

        self.y += self.speed

        self.x += self.wind
        self.x += math.sin(
            self.y * 0.025 + self.phase
        ) * 0.15

        if self.y > HEIGHT + 8:
            self.reset(False)

        if self.x < -10:
            self.x = WIDTH + 5

        if self.x > WIDTH + 10:
            self.x = -5


# ============================================================
# WIDGET
# ============================================================

class NewYearWidget(Gtk.Window):

    def __init__(self):

        super().__init__()

        self.set_decorated(False)
        self.set_resizable(False)

        self.set_default_size(WIDTH, HEIGHT)

        # ----------------------------------------------------
        # LAYER SHELL
        # ----------------------------------------------------

        GtkLayerShell.init_for_window(self)

        GtkLayerShell.set_namespace(
            self,
            "new-year-widget"
        )

        # Над обоями, но под обычными окнами
        GtkLayerShell.set_layer(
            self,
            GtkLayerShell.Layer.BOTTOM
        )

        GtkLayerShell.set_anchor(
            self,
            GtkLayerShell.Edge.TOP,
            True
        )

        GtkLayerShell.set_anchor(
            self,
            GtkLayerShell.Edge.LEFT,
            True
        )

        GtkLayerShell.set_exclusive_zone(
            self,
            -1
        )

        GtkLayerShell.set_keyboard_interactivity(
            self,
            False
        )

        self.x, self.y = load_position()

        self.apply_position()

        # ----------------------------------------------------
        # DRAWING AREA
        # ----------------------------------------------------

        self.area = Gtk.DrawingArea()

        self.area.set_size_request(
            WIDTH,
            HEIGHT
        )

        self.area.connect(
            "draw",
            self.draw
        )

        self.add(self.area)

        # ----------------------------------------------------
        # STATE
        # ----------------------------------------------------

        self.movable = False
        self.dragging = False
        self.total_days_mode = False

        self.drag_start_x = 0
        self.drag_start_y = 0

        self.start_x = 0
        self.start_y = 0

        # ----------------------------------------------------
        # SNOW
        # ----------------------------------------------------

        self.snow = [
            Snowflake()
            for _ in range(70)
        ]

        # ----------------------------------------------------
        # GARLAND
        # ----------------------------------------------------

        self.garland_time = 0

        self.lights = []

        for i in range(11):

            self.lights.append({
                "x": 55 + i * 51,
                "phase": i * 0.65
            })

        # ----------------------------------------------------
        # MOUSE
        # ----------------------------------------------------

        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK
        )

        self.connect(
            "button-press-event",
            self.button_press
        )

        self.connect(
            "button-release-event",
            self.button_release
        )

        self.connect(
            "motion-notify-event",
            self.motion
        )

        # ----------------------------------------------------
        # ANIMATION
        # ----------------------------------------------------

        GLib.timeout_add(
            25,
            self.animation
        )

        GLib.timeout_add(
            1000,
            self.update_countdown
        )

        self.show_all()

    # ========================================================
    # POSITION
    # ========================================================

    def apply_position(self):

        GtkLayerShell.set_margin(
            self,
            GtkLayerShell.Edge.LEFT,
            int(self.x)
        )

        GtkLayerShell.set_margin(
            self,
            GtkLayerShell.Edge.TOP,
            int(self.y)
        )

    # ========================================================
    # MOUSE
    # ========================================================

    def button_press(self, widget, event):

        if event.button == 3:

            self.show_menu(event)

            return True

        if event.button == 1 and self.movable:

            self.dragging = True

            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root

            self.start_x = self.x
            self.start_y = self.y

            return True

        return False

    def button_release(self, widget, event):

        if event.button == 1:

            if self.dragging:

                self.dragging = False

                save_position(
                    self.x,
                    self.y
                )

                return True

        return False

    def motion(self, widget, event):

        if self.dragging:

            dx = event.x_root - self.drag_start_x
            dy = event.y_root - self.drag_start_y

            self.x = self.start_x + dx
            self.y = self.start_y + dy

            self.x = max(0, min(self.x, 2500))
            self.y = max(0, min(self.y, 1400))

            self.apply_position()

            return True

        return False

    # ========================================================
    # MENU
    # ========================================================

    def play_new_year_sound(self, url):
        try:
            subprocess.Popen(
                ["mpv", "--no-video", "--really-quiet", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        except Exception as e:
            print("Ошибка запуска mpv:", e)

    def stop_new_year_sound(self):
        subprocess.run(
            ["pkill", "-f", "mpv --no-video"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def show_menu(self, event):

        menu = Gtk.Menu()

        move = Gtk.CheckMenuItem(
            label="Разрешить перемещать"
        )

        move.set_active(
            self.movable
        )

        move.connect(
            "toggled",
            self.toggle_move
        )

        menu.append(move)

        mode = Gtk.CheckMenuItem(
            label="Режим общего количества дней"
        )

        mode.set_active(
            self.total_days_mode
        )

        mode.connect(
            "toggled",
            self.toggle_mode
        )

        menu.append(mode)

        # ====================================================
        # НОВОГОДНИЕ ЗВУКИ
        # ====================================================

        sounds = Gtk.MenuItem(label="🔔 Звуки НОВЫЙ ГОД!")
        sounds_menu = Gtk.Menu()

        memory = Gtk.MenuItem(
            label="🎄 Somewhere in My Memory — Home Alone"
        )
        memory.connect(
            "activate",
            lambda *_: self.play_new_year_sound(
                "https://www.youtube.com/watch?v=N0NCpe9O1RU"
            )
        )
        sounds_menu.append(memory)

        bells = Gtk.MenuItem(
            label="🔔 Carol of the Bells — Home Alone"
        )
        bells.connect(
            "activate",
            lambda *_: self.play_new_year_sound(
                "https://www.youtube.com/watch?v=xfQmUxri4s8"
            )
        )
        sounds_menu.append(bells)

        all_bells = Gtk.MenuItem(
            label="🔔 Колокола — всё"
        )
        all_bells.connect(
            "activate",
            lambda *_: self.play_new_year_sound(
                "https://www.youtube.com/results?search_query=Christmas+bells+instrumental"
            )
        )
        sounds_menu.append(all_bells)

        stop_sound = Gtk.MenuItem(
            label="⏹ Остановить музыку"
        )
        stop_sound.connect(
            "activate",
            lambda *_: self.stop_new_year_sound()
        )
        sounds_menu.append(stop_sound)

        sounds.set_submenu(sounds_menu)
        menu.append(sounds)

        menu.show_all()

        menu.popup_at_pointer(event)

    def toggle_move(self, item):

        self.movable = item.get_active()

        # Для перемещения временно поднимаем виджет
        if self.movable:

            GtkLayerShell.set_layer(
                self,
                GtkLayerShell.Layer.TOP
            )

        else:

            GtkLayerShell.set_layer(
                self,
                GtkLayerShell.Layer.BOTTOM
            )

            save_position(
                self.x,
                self.y
            )

    def toggle_mode(self, item):

        self.total_days_mode = item.get_active()

        self.area.queue_draw()

    # ========================================================
    # ANIMATION
    # ========================================================

    def animation(self):

        for flake in self.snow:
            flake.update()

        self.garland_time += 0.04

        self.area.queue_draw()

        return True

    def update_countdown(self):

        self.area.queue_draw()

        return True

    # ========================================================
    # COUNTDOWN
    # ========================================================

    def countdown(self):

        delta = TARGET - datetime.now()

        if delta.total_seconds() <= 0:

            return 0, 0, 0, 0, 0, 0

        total = int(
            delta.total_seconds()
        )

        seconds = total % 60

        minutes_total = total // 60

        minutes = minutes_total % 60

        hours_total = minutes_total // 60

        hours = hours_total % 24

        total_days = hours_total // 24

        weeks = total_days // 7

        days = total_days % 7

        months = total_days // 30

        return (
            months,
            weeks,
            days,
            hours,
            minutes,
            seconds
        )

    # ========================================================
    # DRAW
    # ========================================================

    def draw(self, widget, cr):

        # ----------------------------------------------------
        # BACKGROUND
        # ----------------------------------------------------

        cr.set_source_rgba(
            0.025,
            0.035,
            0.065,
            0.96
        )

        self.rounded_rectangle(
            cr,
            0,
            0,
            WIDTH,
            HEIGHT,
            24
        )

        cr.fill()

        # ----------------------------------------------------
        # SNOW
        # ----------------------------------------------------

        self.draw_snow(cr)

        # ----------------------------------------------------
        # GARLAND
        # ----------------------------------------------------

        self.draw_garland(cr)

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        cr.set_source_rgb(
            1,
            1,
            1
        )

        cr.select_font_face(
            "Sans",
            cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_BOLD
        )

        cr.set_font_size(25)

        title = "NEW YEAR IS COMING!"

        ext = cr.text_extents(title)

        cr.move_to(
            (WIDTH - ext.width) / 2,
            82
        )

        cr.show_text(title)

        # ----------------------------------------------------
        # COUNTDOWN
        # ----------------------------------------------------

        (
            months,
            weeks,
            days,
            hours,
            minutes,
            seconds
        ) = self.countdown()

        cr.set_font_size(17)

        if self.total_days_mode:

            total_days = (
                weeks * 7 + days
            )

            text = (
                f"{total_days} DAYS   "
                f"{weeks} WEEKS   "
                f"{days} DAYS"
            )

            ext = cr.text_extents(text)

            cr.move_to(
                (WIDTH - ext.width) / 2,
                130
            )

            cr.show_text(text)

        else:

            text = (
                f"{months} MONTHS   "
                f"{weeks} WEEKS   "
                f"{days} DAYS"
            )

            ext = cr.text_extents(text)

            cr.move_to(
                (WIDTH - ext.width) / 2,
                130
            )

            cr.show_text(text)

        # ----------------------------------------------------
        # CLOCK
        # ----------------------------------------------------

        clock = (
            f"{hours:02d} : "
            f"{minutes:02d} : "
            f"{seconds:02d}"
        )

        cr.set_font_size(32)

        ext = cr.text_extents(clock)

        cr.move_to(
            (WIDTH - ext.width) / 2,
            180
        )

        cr.show_text(clock)

        # ----------------------------------------------------
        # TREES
        # ----------------------------------------------------

        self.draw_tree(
            cr,
            75,
            245,
            0.85
        )

        self.draw_tree(
            cr,
            WIDTH - 75,
            245,
            0.85
        )

        # ----------------------------------------------------
        # SNOW GROUND
        # ----------------------------------------------------

        return False

    # ========================================================
    # GARLAND
    # ========================================================

    def draw_garland(self, cr):

        cr.set_line_width(2)

        cr.set_source_rgba(
            0.15,
            0.15,
            0.18,
            1
        )

        cr.move_to(
            25,
            32
        )

        for i in range(11):

            x = 55 + i * 51

            y = 45 + math.sin(i * 0.8) * 8

            cr.line_to(
                x,
                y
            )

        cr.stroke()

        for i, light in enumerate(self.lights):

            x = light["x"]

            y = 45 + math.sin(i * 0.8) * 8

            # Плавное поочерёдное включение
            wave = (
                math.sin(
                    self.garland_time * 2.2 +
                    light["phase"]
                ) + 1
            ) / 2

            brightness = (
                0.15 +
                wave * 0.85
            )

            if i % 3 == 0:

                r, g, b = (
                    1.0,
                    0.12,
                    0.12
                )

            elif i % 3 == 1:

                r, g, b = (
                    1.0,
                    0.80,
                    0.08
                )

            else:

                r, g, b = (
                    0.15,
                    0.65,
                    1.0
                )

            # glow

            cr.set_source_rgba(
                r,
                g,
                b,
                0.15 * brightness
            )

            cr.arc(
                x,
                y,
                11,
                0,
                math.pi * 2
            )

            cr.fill()

            # lamp

            cr.set_source_rgba(
                r,
                g,
                b,
                brightness
            )

            cr.arc(
                x,
                y,
                4.5,
                0,
                math.pi * 2
            )

            cr.fill()

    # ========================================================
    # SNOW DRAW
    # ========================================================

    def draw_snow(self, cr):

        cr.set_line_width(0.8)

        for flake in self.snow:

            cr.save()

            cr.translate(
                flake.x,
                flake.y
            )

            cr.set_source_rgba(
                1,
                1,
                1,
                flake.opacity
            )

            for angle in range(
                0,
                360,
                60
            ):

                a = math.radians(angle)

                x = math.cos(a) * flake.size
                y = math.sin(a) * flake.size

                cr.move_to(
                    0,
                    0
                )

                cr.line_to(
                    x,
                    y
                )

                cr.stroke()

            cr.restore()

    # ========================================================
    # TREE
    # ========================================================

    def draw_tree(self, cr, x, y, scale):

        cr.save()

        cr.translate(
            x,
            y
        )

        cr.scale(
            scale,
            scale
        )

        # trunk

        cr.set_source_rgb(
            0.35,
            0.18,
            0.08
        )

        cr.rectangle(
            -7,
            0,
            14,
            25
        )

        cr.fill()

        # tree

        cr.set_source_rgb(
            0.05,
            0.45,
            0.18
        )

        self.triangle(
            cr,
            0,
            -85,
            -45,
            5,
            45,
            5
        )

        cr.fill()

        cr.set_source_rgb(
            0.06,
            0.55,
            0.22
        )

        self.triangle(
            cr,
            0,
            -60,
            -35,
            20,
            35,
            20
        )

        cr.fill()

        cr.set_source_rgb(
            0.08,
            0.65,
            0.26
        )

        self.triangle(
            cr,
            0,
            -40,
            -25,
            35,
            25,
            35
        )

        cr.fill()

        # star

        cr.set_source_rgb(
            1.0,
            0.80,
            0.10
        )

        cr.arc(
            0,
            -88,
            5,
            0,
            math.pi * 2
        )

        cr.fill()

        cr.restore()

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def triangle(
        cr,
        x1,
        y1,
        x2,
        y2,
        x3,
        y3
    ):

        cr.move_to(x1, y1)
        cr.line_to(x2, y2)
        cr.line_to(x3, y3)
        cr.close_path()

    @staticmethod
    def rounded_rectangle(
        cr,
        x,
        y,
        width,
        height,
        radius
    ):

        cr.new_sub_path()

        cr.arc(
            x + width - radius,
            y + radius,
            radius,
            -math.pi / 2,
            0
        )

        cr.arc(
            x + width - radius,
            y + height - radius,
            radius,
            0,
            math.pi / 2
        )

        cr.arc(
            x + radius,
            y + height - radius,
            radius,
            math.pi / 2,
            math.pi
        )

        cr.arc(
            x + radius,
            y + radius,
            radius,
            math.pi,
            math.pi * 1.5
        )

        cr.close_path()


# ============================================================
# START
# ============================================================

Gtk.init(None)

window = NewYearWidget()

Gtk.main()
