import random
import numpy as np
import kivy
from kivy.app import App
from kivy.core import text
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

"""
TODO
- Distinguish between flagging and revealing cell (double dropdown/ toggle button)
- Reveal Cell when clicked
- Flag Cell when clicked
- Display surrounding Bomb Count
- Display Bomb Icon
- Display Flag Icon
- Game over when revealing Bomb
- Reveal surrounding Cells when revealing clear Cell
- Win when only all bombs are flagged
- Regenerate Board on Game End

"""

class Cell(Button):
    """Minesweeper Cell"""
    def __init__(self, bomb, index, board, **kwargs):
        """Minesweeper Cell init"""
        super(Cell, self).__init__(**kwargs)
        
        #Sets bomb-indicator and xy-position
        self.is_bomb = bomb
        self.xpos = index[0]
        self.ypos = index[1]
        self.board = board
        self.text = f"{self.xpos} {self.ypos}"
        self.bind(on_release = self.pressed)
    
    def pressed(self, instance):
        """Callback for the Cell"""
        ind = (self.xpos, self.ypos)
        print("Index is: %s "% instance.text + "Bomb? " + str(self.is_bomb))
        self.around(int(ind[0]), int(ind[1]))

    def around(self, x, y):
        """Gets Surrounding Cell Values and counts Bombs"""
        temp = [[],[],[]]
        width = self.board.cols -1 
        height = self.board.rows -1

        temp[0].append(self.getval(y-1,x-1) if x>0 and y>0 else None)
        print(temp[0][0])
        temp[0].append(self.getval(y-1, x) if y>0 else None)
        temp[0].append(self.getval(y-1, x+1) if x<width and y>0 else None)

        temp[1].append(self.getval(y,x-1) if x>0 else None)
        temp[1].append(self.is_bomb)
        temp[1].append(self.getval(y,x+1) if x<width else None)
        
        temp[2].append(self.getval(y+1,x-1) if x > 0 and y<height else None)
        temp[2].append(self.getval(y+1,x) if y<height else None)
        temp[2].append(self.getval(y+1,x+1) if x<width and y<height else None)

        temp = np.array(temp)
        print(temp)
        print("Amount of Bombs near me: " + str(self.fieldsum(temp)-self.is_bomb))
    
    def getval(self, y,x):
        """Gets field value"""
        return self.board.field[y][x]

    def fieldsum(self, field):
        """Sums the amount of bombs in a given field"""
        num = 0
        for i in field:
            for j in i:
                if j:
                    num += 1
        return num

class GameBoard(GridLayout):
    """Holds all Cells"""
    def __init__(self, x, y, bombs, **kwargs):
        """Game Board Init"""
        super(GameBoard, self).__init__(**kwargs)
        self.rows = y
        self.cols = x
        self.field = np.zeros((y,x), dtype=bool)
        print(self.field)

        # Adjusts bomb count if ist less than zero or more than the amount of cells
        if bombs < 0:
            bombs = 0
        if bombs > x*y:
            bombs = x*y-1

        # if bomb count is more than half of the cells, randomly removes bombs until bomb count is reached
        # else randomly adds bombs until bomb count is reached
        if bombs > 1/2 * x*y:
            self.field = 1- self.field
            reverse = False
        else:
            reverse = True
        
        while self.field.sum() != bombs:
            self.field[random.randint(0,y-1)][random.randint(0,x-1)] = reverse

        # adds cells
        for i in range(y):
            for j in range(x):
                self.add_widget(Cell(self.field[i,j], (j,i), self))

    
        

class MainMenu(BoxLayout):
    """Main Menu for the Minesweeper App"""
    def __init__(self, **kwargs):
        """Constructing Main Menu"""
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # Adding Widgets
        xinput = TextInput(hint_text = "Insert Board Width", text = "20")
        yinput = TextInput(hint_text = "Insert Board height", text = "10")
        binput = TextInput(hint_text = "Insert Bomb Count", text = "20")
        startbutton = Button(text = "start")
        startbutton.bind(on_release = lambda x: self.startGame(int(xinput.text), int(yinput.text), int(binput.text)))

        self.add_widget(xinput)
        self.add_widget(yinput)
        self.add_widget(binput)
        self.add_widget(startbutton)
    
    def startGame(self, x, y, bombs):
        """Opens Popup and starts Minesweeper Game"""
        layout = BoxLayout(orientation = "vertical")
        game = Popup(title = "Game", content = layout)

        back = Button(text = "Back", size_hint_y = 0.1)
        back.bind(on_release = game.dismiss)

        layout.add_widget(GameBoard(x, y, bombs))
        layout.add_widget(back)

        game.open()


class MyApp(App):
    def build(self):
        return MainMenu()

if __name__ == "__main__":
    MyApp().run()







