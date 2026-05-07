"""DakBabu — Entry point.

Creates the root App window and runs the application mainloop.
Run with: python -m src.main
"""

import customtkinter as ctk

from src.ui.app import App


def main() -> None:
    """Launch the DakBabu application window.

    Creates the App (which sets up the wizard shell with NavBar,
    BottomBar, and content area), then starts the mainloop.
    """
    # Set appearance and default color theme
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
