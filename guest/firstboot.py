#!/usr/bin/env python3
"""Tomato OS account setup shown only on first boot."""
import getpass
import json
import subprocess
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

if getpass.getuser() != "tomato-setup":
    raise SystemExit(0)

CSS = b"""
window { background: #152421; color: #f7f7f2; }
label { color: #f7f7f2; }
entry { min-height: 36px; border-radius: 8px; }
button.suggested-action { background: #dc4a40; color: white; min-height: 38px;
                           border-radius: 8px; font-weight: bold; }
"""
provider = Gtk.CssProvider()
provider.load_from_data(CSS)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

window = Gtk.Window(title="Tomato OS einrichten")
window.set_default_size(460, 410)
window.set_position(Gtk.WindowPosition.CENTER)
window.set_resizable(False)
window.connect("delete-event", lambda *_: True)
box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
box.set_border_width(34)
window.add(box)
title = Gtk.Label()
title.set_markup('<span size="xx-large" weight="bold">Willkommen bei Tomato OS</span>')
title.set_xalign(0)
box.pack_start(title, False, False, 0)
intro = Gtk.Label(label="Erstelle dein persönliches Konto. Danach startet Tomato OS neu.")
intro.set_xalign(0)
intro.set_line_wrap(True)
box.pack_start(intro, False, False, 0)

def field(label, secret=False):
    heading = Gtk.Label(label=label)
    heading.set_xalign(0)
    box.pack_start(heading, False, False, 0)
    entry = Gtk.Entry()
    entry.set_visibility(not secret)
    box.pack_start(entry, False, False, 0)
    return entry

username = field("Benutzername (kleine Buchstaben, mindestens 3 Zeichen)")
password = field("Passwort (mindestens 8 Zeichen)", True)
repeat = field("Passwort wiederholen", True)
message = Gtk.Label()
message.set_xalign(0)
message.set_line_wrap(True)
box.pack_start(message, False, False, 0)
button = Gtk.Button(label="Konto erstellen und neu starten")
button.get_style_context().add_class("suggested-action")
box.pack_start(button, False, False, 0)

def submit(_button):
    if password.get_text() != repeat.get_text():
        message.set_text("Die Passwörter stimmen nicht überein.")
        return
    button.set_sensitive(False)
    result = subprocess.run(
        ["sudo", "-n", "/usr/local/sbin/tomato-finish-setup"],
        input=json.dumps({"username": username.get_text(), "password": password.get_text()}),
        text=True, capture_output=True, check=False)
    if result.returncode:
        message.set_text(result.stderr.strip() or "Einrichtung fehlgeschlagen.")
        button.set_sensitive(True)
    else:
        message.set_text("Konto erstellt. Tomato OS startet neu.")

button.connect("clicked", submit)
window.show_all()
Gtk.main()