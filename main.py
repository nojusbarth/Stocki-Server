# https://towardsdatascience.com/a-comprehensive-guide-to-downloading-stock-prices-in-python-2cd93ff821d4

import tkinter as tk
from tkinter import ttk
from windowMng import *

#
if __name__ == "__main__":
    
    # root
    root = tk.Tk()
    root.configure(bg='light steel blue')
    root.state('zoomed')
    #root.geometry(STOCKI_LAYOUT_frameGeometry)
    root.title(STOCKI_LAYOUT_AppTitle)
    
    wm = WindowMng(root)
        
    root.mainloop()
