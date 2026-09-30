#!/usr/bin/env python3
"""Tomaten OS desktop shell. XFWM and xfdesktop provide window management."""
from datetime import datetime
from pathlib import Path
import os
import platform
import shutil
import subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk

RED = "#f43b42"
CSS = b"""
window.tomaten-top, window.tomaten-side, window.tomaten-dock,
window.tomaten-control { background-color: rgba(12, 12, 16, 0.95);
  color: #f7f7f7; border: 1px solid #92242c; }
window.tomaten-top { border-left: 0; border-right: 0; border-top: 0; }
window.tomaten-side, window.tomaten-dock { border-radius: 8px; }
window.tomaten-control { border-radius: 10px; }
label { color: #f7f7f7; }
label.brand { font-size: 23px; font-weight: 800; letter-spacing: 1px; }
label.subtitle, label.accent { color: #f43b42; }
label.subtitle { font-size: 11px; font-weight: 700; }
label.nav-symbol { color: #f43b42; font-size: 21px; }
label.heading { color: #f43b42; font-size: 23px; font-weight: 800; }
label.stat-value { color: #f7f7f7; font-weight: 700; }
button { background: transparent; border: 0; box-shadow: none;
  color: #f7f7f7; border-radius: 6px; padding: 7px; }
button:hover { background: rgba(220, 45, 54, 0.22); }
button.action { background: #e62f38; color: #fff; font-weight: bold; }
button.action:hover { background: #ff4550; }
"""
provider = Gtk.CssProvider()
provider.load_from_data(CSS)
screen = Gdk.Screen.get_default()
Gtk.StyleContext.add_provider_for_screen(
    screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def launch(command):
    try:
        subprocess.Popen(command, start_new_session=True)
    except OSError as error:
        dialog = Gtk.MessageDialog(
            transient_for=None, flags=0, message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE, text="Programm konnte nicht starten")
        dialog.format_secondary_text(str(error))
        dialog.run()
        dialog.destroy()


def desktop_window(css_class):
    window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
    window.set_decorated(False)
    window.set_resizable(False)
    window.set_keep_above(True)
    window.set_skip_taskbar_hint(True)
    window.set_skip_pager_hint(True)
    window.set_type_hint(Gdk.WindowTypeHint.DOCK)
    visual = screen.get_rgba_visual()
    if visual:
        window.set_visual(visual)
    window.get_style_context().add_class(css_class)
    return window


def button(symbol, title, callback, compact=False):
    widget = Gtk.Button()
    widget.set_relief(Gtk.ReliefStyle.NONE)
    widget.set_tooltip_text(title)
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    icon = Gtk.Label(label=symbol)
    icon.get_style_context().add_class("nav-symbol")
    row.pack_start(icon, False, False, 0)
    if not compact:
        text = Gtk.Label(label=title)
        text.set_xalign(0)
        row.pack_start(text, True, True, 0)
    widget.add(row)
    widget.connect("clicked", lambda _widget: callback())
    return widget


class TomatenShell:
    def __init__(self):
        self.top = desktop_window("tomaten-top")
        self.side = desktop_window("tomaten-side")
        self.dock = desktop_window("tomaten-dock")
        self.control = self.make_control()
        self.make_top()
        self.make_side()
        self.make_dock()
        for window in (self.top, self.side, self.dock):
            window.show_all()
        self.place()
        screen.connect("size-changed", lambda *_: self.place())
        GLib.timeout_add_seconds(15, self.place_once)
        GLib.timeout_add_seconds(1, self.tick)
        self.tick()

    def place_once(self):
        self.place()
        return False

    def place(self):
        width, height = screen.get_width(), screen.get_height()
        self.top.resize(width, 64)
        self.top.move(0, 0)
        self.side.resize(168, 330)
        self.side.move(18, 96)
        self.dock.resize(338, 58)
        self.dock.move(max(0, (width - 338) // 2), max(80, height - 72))

    def make_top(self):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.set_border_width(9)
        self.top.add(row)
        logo = Gtk.Label(label="⬡")
        logo.get_style_context().add_class("nav-symbol")
        row.pack_start(logo, False, False, 8)
        brand = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        name = Gtk.Label(label="TOMATEN OS")
        name.set_xalign(0)
        name.get_style_context().add_class("brand")
        subtitle = Gtk.Label(label="ROT / SCHWARZ EDITION")
        subtitle.set_xalign(0)
        subtitle.get_style_context().add_class("subtitle")
        brand.pack_start(name, False, False, 0)
        brand.pack_start(subtitle, False, False, 0)
        row.pack_start(brand, False, False, 0)
        spacer = Gtk.Box()
        row.pack_start(spacer, True, True, 0)
        row.pack_start(button("◆", "Netzwerk", self.open_control, True), False, False, 0)
        self.clock = Gtk.Label()
        row.pack_start(self.clock, False, False, 12)
        row.pack_start(button("⏻", "Abmelden oder Ausschalten", self.power_menu, True),
                       False, False, 4)

    def make_side(self):
        column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        column.set_border_width(8)
        self.side.add(column)
        entries = [
            ("▣", "Dokumente", self.documents),
            ("▤", "Terminal", lambda: launch(["xfce4-terminal"])),
            ("◎", "Browser", lambda: launch(["brave-browser"])),
            ("⚙", "Einstellungen", self.open_control),
            ("▰", "Dateien", lambda: launch(["thunar"])),
        ]
        for icon, title, callback in entries:
            column.pack_start(button(icon, title, callback), True, True, 0)

    def make_dock(self):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.set_border_width(7)
        self.dock.add(row)
        entries = [
            ("▣", "Dateien", lambda: launch(["thunar"])),
            ("▤", "Terminal", lambda: launch(["xfce4-terminal"])),
            ("◎", "Brave", lambda: launch(["brave-browser"])),
            ("⚙", "System", self.open_control),
            ("▰", "Dokumente", self.documents),
        ]
        for icon, title, callback in entries:
            row.pack_start(button(icon, title, callback, True), True, True, 0)

    def documents(self):
        folder = Path.home() / "Dokumente"
        folder.mkdir(exist_ok=True)
        launch(["thunar", str(folder)])

    def tick(self):
        self.clock.set_text(datetime.now().strftime("%a, %d. %b %Y · %H:%M"))
        return True

    def make_control(self):
        window = Gtk.Window(title="Tomaten OS · System")
        window.set_default_size(550, 370)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.get_style_context().add_class("tomaten-control")
        window.connect("delete-event", lambda widget, *_: widget.hide() or True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_border_width(24)
        window.add(box)
        heading = Gtk.Label(label="Systemübersicht")
        heading.set_xalign(0)
        heading.get_style_context().add_class("heading")
        box.pack_start(heading, False, False, 0)
        intro = Gtk.Label(label="Tomaten OS · Linux-basiert · automatische Updates")
        intro.set_xalign(0)
        box.pack_start(intro, False, False, 0)
        self.stats = Gtk.Label()
        self.stats.set_xalign(0)
        self.stats.set_yalign(0)
        self.stats.get_style_context().add_class("stat-value")
        box.pack_start(self.stats, True, True, 0)
        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.pack_start(actions, False, False, 0)
        update = Gtk.Button(label="Updates prüfen")
        update.get_style_context().add_class("action")
        update.connect("clicked", lambda *_: launch([
            "xfce4-terminal", "--hold", "--execute", "bash", "-lc",
            "sudo apt-get update && sudo apt-get upgrade"]))
        actions.pack_start(update, False, False, 0)
        settings = Gtk.Button(label="Systemeinstellungen")
        settings.connect("clicked", lambda *_: launch(["xfce4-settings-manager"]))
        actions.pack_start(settings, False, False, 0)
        return window

    def open_control(self):
        total, used, free = shutil.disk_usage("/")
        self.stats.set_text(
            "Kernel: " + platform.release() + "\n"
            "Architektur: " + platform.machine() + "\n"
            "CPU-Kerne: " + str(os.cpu_count() or 1) + "\n"
            "Speicher: " + str(round(total / 1024**3)) + " GB, "
            + str(round(used / 1024**3)) + " GB belegt\n\n"
            "Sicherheits- und Browser-Updates werden regelmäßig installiert.")
        self.control.show_all()
        self.control.present()

    def power_menu(self):
        dialog = Gtk.MessageDialog(
            transient_for=self.control, flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.NONE, text="Tomaten OS")
        dialog.format_secondary_text("Was möchtest du tun?")
        dialog.add_button("Abbrechen", Gtk.ResponseType.CANCEL)
        dialog.add_button("Abmelden", 1)
        dialog.add_button("Neustart", 2)
        dialog.add_button("Ausschalten", 3)
        answer = dialog.run()
        dialog.destroy()
        if answer == 1:
            Gtk.main_quit()
        elif answer == 2:
            launch(["systemctl", "reboot"])
        elif answer == 3:
            launch(["systemctl", "poweroff"])


if __name__ == "__main__":
    TomatenShell()
    Gtk.main()