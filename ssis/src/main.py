import tkinter as tk
from gui import SSIS_APP

def main():
    root = tk.Tk()
    SSIS_APP(root)
    root.mainloop()

if __name__ == "__main__":
    main()