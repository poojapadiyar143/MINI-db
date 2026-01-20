"""
main.py
Main entry point for StructDB application
"""

import tkinter as tk
import gui


def main():
    """Main function to start the application"""
    root = tk.Tk()
    app = gui.StructDBGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()