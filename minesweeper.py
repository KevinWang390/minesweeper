"""
Kevin Wang
Python 3.8

start: 6/8/2022
checkpoint: 6/8/2022
    -- gameplay, lose condition, reset

basic implementation of Minesweeper

"""

import tkinter as tk
import numpy as np
from random import random, randint

"""
cell inherits from tk.Button, instances of cell have additional fields
class attributes describe game environment and progression, not individual cells
"""
class cell(tk.Button):
    frame = 0
    dimensions = 0
    num_mines = 0
    num_marked = 0
    mine_counter = 0
    #fields for start and end of game
    is_new = True
    dead = False
    source = [0,0,0,0]
    mine_list = []
    """
    overloaded tk.Button constructor
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.neighbors = [0,0,0,0,0,0,0,0]
        self.pos = (0,0)
        self.revealed = False
        self.marked = False
        self.config(command = self.reveal)
        self.bind("<Button-3>", self.mark)
    """
    functionality for behavior of individual cell triggered on left click
    includes functionality for initializing cell values, since it is better
    to have values dynamically allocated based on the position of the first click
    also includes mine behavior
    the mechanism is changing the color of the text and background to influence visibility
    """
    def reveal(self):
        #prevents further action on board if game is over
        if cell.dead:
            return
        #dynamically initialize cell value
        if cell.is_new:
            cell.is_new = False
            x,y = self.pos
            a = randint(2,3)
            b = randint(2,3)
            c = randint(2,3)
            d = randint(2,3)
            cell.source = [x-a, x+b, y-c, y+d]
            
            #set mine locations
            mc = cell.num_mines
            p = float(mc / (cell.dimensions ** 2))
            while mc > 0:
                for i in range(cell.dimensions):
                    if mc <= 0:
                        break
                    for j in range(cell.dimensions):
                        c = cell.frame[i,j]
                        if mc <= 0 or c['text'] == "*":
                            break
                        #ignore area around first click, guarantees a playable start
                        if i > cell.source[0] and i < cell.source[1] and j > cell.source[2] and j < cell.source[3]:
                            continue
                        n = random()
                        if (n < p):
                            c['text'] = "*"
                            cell.mine_list.append(c)
                            mc-=1
            
            #fill in remaining values
            for i in range(cell.dimensions):
                for j in range(cell.dimensions):
                    c = cell.frame[i,j]
                    if c['text'] == "*":
                        continue
                    count = 0
                    for a in range(i-1,i+2):
                        for b in range(j-1,j+2):
                            if a >= 0 and a < cell.dimensions and b >= 0 and b < cell.dimensions:
                                if cell.frame[a,b]['text'] == "*":
                                    count+=1
                    c.config(text = str(count))
        
        #functionality for non-initial moves
        #prevent action on already revealed cells
        if self.revealed:
            return
        #reveal the cell based on type
        self.revealed = True
        self.config(bg = "red" if self['text'] == "*" else "white")
        self.config(fg = "white" if self['text'] == "0" else "black")
        #propagate revealing when clicking on zero
        if self['text'] == "0":
            for i in self.neighbors:
                if i:
                    i.reveal()
        #mine clicked, reveal all mine locations, end game
        if self['text'] == "*":
            for m in cell.mine_list:
                m.config(bg = "red", fg = "black")
                cell.dead = True
    """
    functionality for marking potential mine locations triggered on right click
    implements a counter for player convenience
    counter is based entirely on player choices and does not indicate correctness of those choices
    """
    def mark(self, trash):
        #prevent action if game is over
        if cell.dead:
            return
        #left click both marks and unmarks cell, alternating
        if not self.revealed:
            if self.marked:
                self.marked = False
                cell.num_marked-=1
                self.config(fg = "gray", bg = "gray")
            else:
                self.marked = True
                cell.num_marked+=1
                self.config(fg = "yellow", bg = "yellow")
            cell.mine_counter.config(text = "mines left:\n" + str(cell.num_mines - cell.num_marked))
    """
    reinitalizes the game
    can be used regardless of game state
    is abbreviated version of init()
    """
    def refresh():
        cell.is_new = True
        cell.dead = False
        cell.num_marked = 0
        cell.mine_counter.config(text = "mines left:\n" + str(cell.num_mines - cell.num_marked))
        #init() has already created the board, just need to change values
        for i in cell.frame:
            for j in i:
                j.config(text = "0", bg = "gray", fg = "gray")
                j.revealed = False
                j.marked = False
                cell.mine_list = []

"""
(mostly) one-time setup of back-end functionality
intializes unchangeing class and instance attributes of cell
the game board is a graph: each cell is a vertex, connected to each neighbor, including diagonal
"""
def init(window, dim, mines):
    
    cell.is_new = True
    cell.dead = False
    
    cell.num_mines = mines
    cell.dimensions = dim
    buttons = np.empty(shape = (dim,dim), dtype = tk.Button)
    
    #create buttons
    for i in range(dim):
        for j in range(dim):
            frame = tk.Frame(master = window, relief = tk.SUNKEN, borderwidth = 2)
            frame.grid(row = i, column = j)
            c = cell(master = frame, text = "0", width = 2, fg = "gray", bg = "gray")
            c.pack()
            buttons[i,j] = c
            c.pos = (i,j)
            #link cell to neighbors, used for propagation in reveal()
            if i > 0:
                c.neighbors[0] = buttons[i-1,j]
                buttons[i-1,j].neighbors[1] = c
                if j > 0:
                    c.neighbors[2] = buttons[i-1,j-1]
                    buttons[i-1,j-1].neighbors[3] = c
                if j < dim-1:
                    c.neighbors[4] = buttons[i-1,j+1]
                    buttons[i-1,j+1].neighbors[5] = c
            if j > 0:
                c.neighbors[6] = buttons[i,j-1]
                buttons[i,j-1].neighbors[7] = c
    
    cell.frame = buttons
    
"""
sets board size and the number of mines: these values cannot be changed from within the application
calls init()
creates the reset button and non-essential user interface
"""
def run(window):
    frame = tk.Frame(master = window)
    #basic game parameters
    dim = 20
    mine_count = 80
    #calling init
    init(frame, dim, mine_count)
    #setup user interface
    menu = tk.Frame(master = window, relief = tk.RAISED)
    title = tk.Label(master = window, text = "minesweeper", height = 2, bg = "seashell3")
    mine_label = tk.Label(master = menu, text = "mines left:\n" + str(mine_count), width = 20)
    cell.mine_counter = mine_label
    title.pack(side = tk.TOP, fill = tk.BOTH)
    menu.pack(side = tk.RIGHT, fill = tk.Y)
    cell.mine_counter.pack(side = tk.TOP)
    reset = tk.Button(master = menu, text = "reset", bg = "seashell3", fg = "red", height = 3, command = cell.refresh)
    reset.pack(side = tk.BOTTOM, fill = tk.X)
    frame.pack()

"""
main window is handled in main
may be inefficient
"""
def main():
    window = tk.Tk()
    run(window)
    window.mainloop()

if __name__ == "__main__":
    main()