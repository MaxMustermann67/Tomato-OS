#!/usr/bin/env python3
"""Account creation screen used once, without a welcome dashboard."""
import getpass
import json
import subprocess
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

if getpass.getuser() != "tomato-setup":
    raise SystemExit(0)

CSS = b"""
window { background: #0e0e12; color: #f7f7f7; border: 1px solid #9b2730; }
label { color: #f7f7f7; }
label.heading { color: #f43b42; font-size: 22px; font-weight: 800; }
entry { min-height: 36px; border-radius: 6px; }
button.suggested-action { background: #e62f38; color: white;
  min-height: 38px; border-radius: 6px; font-weight: bold; }
"""
provider = Gtk.CssProvider()
provider.load_from_data(CSS)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

window = Gtk.Window(title="Tomaten OS · Konto einrichten")
window.set_default_size(440, 370)
window.set_position(Gtk.WindowPosition.CENTER)
window.set_resizable(False)
window.connect("delete-event", lambda *_: True)
box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
box.set_border_width(28)
window.add(box)
title = Gtk.Label(label="Konto einrichten")
title.get_style_context().add_class("heading")
title.set_xalign(0)
box.pack_start(title, False, False, 0)
intro = Gtk.Label(label="Lege den Benutzer für deine Anmeldung fest.")
intro.set_xalign(0)
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
password = field("Passwort", True)
repeat = field("Passwort wiederholen", True)
message = Gtk.Label()
message.set_xalign(0)
message.set_line_wrap(True)
box.pack_start(message, False, False, 0)
submit_button = Gtk.Button(label="Konto erstellen")
submit_button.get_style_context().add_class("suggested-action")
box.pack_start(submit_button, False, False, 0)

def submit(_button):
    if password.get_text() != repeat.get_text():
        message.set_text("Die Passwörter stimmen nicht überein.")
        return
    submit_button.set_sensitive(False)
    result = subprocess.run(
        ["sudo", "-n", "/usr/local/sbin/tomato-finish-setup"],
        input=json.dumps({"username": username.get_text(), "password": password.get_text()}),
        text=True, capture_output=True, check=False)
    if result.returncode:
        message.set_text(result.stderr.strip() or "Einrichtung fehlgeschlagen.")
        submit_button.set_sensitive(True)
    else:
        message.set_text("Konto erstellt. Das System startet neu.")

submit_button.connect("clicked", submit)
window.show_all()
Gtk.main()