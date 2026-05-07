"""DakBabu — Entry point.

Creates the root App window, registers all wizard steps,
and runs the application mainloop.
Run with: python -m src.main
"""

import customtkinter as ctk

from src.ui.app import App
from src.ui.steps.step0_welcome import Step0Welcome
from src.ui.steps.step1_credentials import Step1Credentials
from src.ui.steps.step2_files import Step2Files
from src.ui.steps.step3_preview import Step3Preview
from src.ui.steps.step4_tracker import Step4Tracker


def main() -> None:
    """Launch the DakBabu application window.

    Creates the App (which sets up the wizard shell with NavBar,
    BottomBar, and content area), registers the wizard steps, then
    starts the mainloop.
    """
    # Set appearance and default color theme
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = App()

    # -- Step 0: Welcome & System Check ------------------------------------
    step0 = Step0Welcome(
        master=app.content_frame,
        on_proceed=lambda: app.show_step(1),
    )
    app.add_step(step0)

    # -- Step 1: Credentials -----------------------------------------------
    step1 = Step1Credentials(master=app.content_frame)
    app.add_step(step1)

    # -- Step 2: Files & Email ---------------------------------------------
    step2 = Step2Files(master=app.content_frame)
    app.add_step(step2)

    # -- Step 3: Preview ---------------------------------------------------
    step3 = Step3Preview(master=app.content_frame)
    app.add_step(step3)

    # -- Step 4: Send & Track ----------------------------------------------
    step4 = Step4Tracker(master=app.content_frame)
    app.add_step(step4)

    app.mainloop()


if __name__ == "__main__":
    main()
