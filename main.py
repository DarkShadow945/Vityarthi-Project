import tkinter as tk
from gui import ScreenDistanceApp


def main():
    root = tk.Tk()
    app = ScreenDistanceApp(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()


if __name__ == "__main__":
    main()