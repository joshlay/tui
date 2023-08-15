#!/usr/bin/env python3
"""Base Textual Application"""
import os
from datetime import datetime
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Grid
from textual.screen import ModalScreen
from textual.widgets import (
        Button,
        Footer,
        Header,
        Label,
        TabbedContent,
        TabPane,
        RichLog,
        )

# 'package' (script) meta
metadata = {
    'title': 'Textual Application',
    'author': 'Josh Lay <me+fedora@jlay.io>',
    'creation_date': '2023-06-29',
    'version': '1.0.0',
    'description': '''This is a basic Textual TUI application.

Used as the foundation for other projects'''
}

class QuitScreen(ModalScreen):
    """Screen with a dialog to quit. Shown when user presses keybind"""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Are you sure you want to quit?", id="question"),
            Button("Quit", variant="error", id="quit"),
            Button("Cancel", variant="primary", id="cancel"),
            id="quit_dialog",
            classes="dialog"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks, either quit or continue / return to main screen"""
        if event.button.id == "quit":
            self.app.exit()
        else:
            self.app.pop_screen()


class TextualApp(App):
    """Defines the main Textual 'app'"""

    # set the path to the stylesheet, relative is fine
    CSS_PATH = 'style.css'

    TITLE = metadata['title']

    BINDINGS = (
            # be careful with enabling priority; will steal focus from input fields
            Binding("c", "custom_dark", "Color Toggle"),
            Binding("s", "custom_screenshot", "Screenshot"),
            Binding("q", "request_quit", "Quit")
            )
    SCREENS = {"quit_screen": QuitScreen()}

    selected_path = None
    tabbed_container = None
    text_log = None

    def __init__(self, *args, **kwargs):
        """On startup of the TUI, initialize objects/vars"""
        super().__init__(*args, **kwargs)
        self.tabbed_container = TabbedContent(id="tabbed_content_main",
                                              classes='tabbed_container')
        self.text_log = RichLog(id="main_textlog",
                                markup=True,
                                highlight=True,
                                classes='logs')

    @work(exclusive=True)
    async def action_custom_dark(self) -> None:
        """An action to toggle dark mode. Wraps 'action_toggle_dark' with our logging"""
        self.app.dark = not self.app.dark
        await self.update_log(f'[bold]Dark mode: {self.dark}', notify=True)

    def action_request_quit(self) -> None:
        """When the user presses the quit keybind, show the quit confirmation screen"""
        self.push_screen('quit_screen')

    def get_screenshot_name(self) -> str:
        """Using the current date and time, return a name for the requested screenshot"""
        return f'screenshot_{datetime.now().isoformat().replace(":", "_")}.svg'

    async def action_custom_screenshot(self, screen_dir: str = '/tmp') -> None:
        """Action that fires when the user presses 's' for a screenshot"""
        # take the screenshot, recording the path for logging/notification
        outpath = self.save_screenshot(path=screen_dir, filename=self.get_screenshot_name())
        # construct the log/notification message, then show it
        await self.update_log(f"[bold]Screenshot saved: [green]'{outpath}'", notify=True)

    def compose(self) -> ComposeResult:
        """Craft the main window/widgets"""
        yield Header(show_clock=True)
        with self.tabbed_container:
            with TabPane("Main", id="tab_main"):
                yield self.text_log
            with TabPane("About", id="tab_about"):
                yield Vertical(
                        Label(f"{metadata['title']} v{metadata['version']}"),
                        Label(f"{metadata['description']}"),
                        Label(f"by [italic]{metadata['author']}[/]", markup=True)
                        )
        yield Footer()

    async def on_mount(self) -> None:
        """Fires when widget 'mounted', behaves like on-first-showing"""
        await self.update_log(f"Hello, {os.getlogin()} :)", notify=True)

    async def update_log(self, message: str, timestamp: bool = True, notify: bool = False) -> None:
        """Write to the main RichLog widget, optional timestamps and notifications"""
        if timestamp:
            self.text_log.write(datetime.now().strftime("%b %d %H:%M:%S") + ': ' + message)
        else:
            self.text_log.write(message)
        if notify:
            self.notify(message)


if __name__ == "__main__":
    app = TextualApp()
    app.run()
