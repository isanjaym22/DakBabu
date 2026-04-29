"""DakBabu — Entry point.

Creates the root customtkinter window and runs the application mainloop.
Run with: python -m src.main
"""

import customtkinter as ctk

from src.ui.theme import (
    COLOR_BACKGROUND,
    FONT_FAMILY,
    WINDOW_DEFAULT_HEIGHT,
    WINDOW_DEFAULT_WIDTH,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_TITLE,
)


def main() -> None:
    """Launch the DakBabu application window.

    Creates a root CTk window with the design system tokens applied,
    sets minimum and default sizes, and starts the mainloop.
    """
    # Set appearance and default color theme
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # Create root window
    root = ctk.CTk()
    root.title(WINDOW_TITLE)

    # Window sizing — from ARCHITECTURE.md §4 (Responsive / Resizable Window)
    root.geometry(f"{WINDOW_DEFAULT_WIDTH}x{WINDOW_DEFAULT_HEIGHT}")
    root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

    # Set background color to match Stitch design
    root.configure(fg_color=COLOR_BACKGROUND)

    # Set default font family for the application
    root.option_add("*Font", f"{FONT_FAMILY} 14")

    # Run the application
    root.mainloop()


if __name__ == "__main__":
    main()
