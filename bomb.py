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
- Distinguish between flagging and revealing cell (double dropdown/toggle button)
- Reveal Cell when clicked
- Flag Cell when clicked
- Display surrounding Bomb Count and change background color
- Display Bomb Icon
- Display Flag Icon
- Game over when revealing Bomb
- Reveal surrounding Cells when revealing clear Cell
- Win once only all bombs are flagged
- Regenerate Board on Game End
- maybe also Timer and Highscores

"""


class GameBoard(GridLayout):
    """Holds all Cells"""
    def __init__(self, width : int, height : int, bomb_count : int, **kwargs):
        """Game Board Init"""
        super(GameBoard, self).__init__(**kwargs)
        self.rows = height
        self.cols = width
        self.field = np.zeros((height,width), dtype=bool)
        print(self.field)

        # Adjusts bomb count if ist less than zero or more than the amount of cells
        if bomb_count < 0:
            bomb_count = 0
        if bomb_count > width*height:
            bomb_count = width*height

        # if bomb count is more than half of the cells, randomly removes bombs until bomb count is reached
        # else randomly adds bombs until bomb count is reached
        if bomb_count > 1/2 * width*height:
            self.field = 1- self.field
            cell_value = False
        else:
            cell_value = True
        
        while self.field.sum() != bomb_count:
            self.field[random.randint(0,height-1)][random.randint(0,width-1)] = cell_value

        # adds cells
        for i in range(height):
            for j in range(width):
                self.add_widget(Cell(self.field[i,j], (j,i), self))

    
class Cell(Button):
    """Minesweeper Cell"""
    def __init__(self, is_bomb : bool, index : "tuple[int, int]", board : GameBoard, **kwargs):
        """Minesweeper Cell init"""
        super(Cell, self).__init__(**kwargs)
        
        # Sets bomb-indicator and xy-position
        self.is_bomb = is_bomb
        self.x_index = index[0]
        self.y_index = index[1]
        self.game_board = board
        self.text = f"{self.x_index} {self.y_index}"
        self.bind(on_release = self.pressed)
    
    def pressed(self, instance: Button):
        """Callback for the Cell"""
        index = (self.x_index, self.y_index)
        print("Index is: %s "% instance.text + "Bomb? " + str(self.is_bomb))
        self.around(int(index[0]), int(index[1]))

    def around(self, x_index: int, y_index: int):
        """Gets Surrounding Cell Values and counts Bombs"""
        temp_list = [[],[],[]]
        width = self.game_board.cols -1 
        height = self.game_board.rows -1

        temp_list[0].append(self.getval(y_index - 1, x_index - 1) if x_index > 0 and y_index > 0 else None)
        temp_list[0].append(self.getval(y_index - 1, x_index) if y_index > 0 else None)
        temp_list[0].append(self.getval(y_index - 1, x_index + 1) if x_index < width and y_index > 0 else None)

        temp_list[1].append(self.getval(y_index, x_index - 1) if x_index > 0 else None)
        temp_list[1].append(self.is_bomb)
        temp_list[1].append(self.getval(y_index, x_index + 1) if x_index < width else None)
        
        temp_list[2].append(self.getval(y_index + 1, x_index - 1) if x_index > 0 and y_index < height else None)
        temp_list[2].append(self.getval(y_index + 1, x_index) if y_index < height else None)
        temp_list[2].append(self.getval(y_index + 1, x_index + 1) if x_index < width and y_index < height else None)

        temp_list = np.array(temp_list)
        print(temp_list)
        print("Amount of Bombs near me: " + str(self.fieldsum(temp_list)-self.is_bomb))
    
    def getval(self, y_index : int, x_index : int):
        """Gets field value"""
        return self.game_board.field[y_index][x_index]

    def fieldsum(self, field : np.array):
        """Sums the amount of bombs in a given field"""
        amount = 0
        for i in field:
            for j in i:
                if j:
                    amount += 1
        return amount
        

class MainMenu(BoxLayout):
    """Main Menu for the Minesweeper App"""
    def __init__(self, **kwargs):
        """Constructing Main Menu"""
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # Adding Widgets
        width_input = TextInput(hint_text = "Insert Board Width", text = "20")
        height_input = TextInput(hint_text = "Insert Board height", text = "10")
        bomb_input = TextInput(hint_text = "Insert Bomb Count", text = "20")
        startbutton = Button(text = "start")
        startbutton.bind(on_release = lambda x: self.startGame(width_input.text, height_input.text, bomb_input.text))

        self.add_widget(width_input)
        self.add_widget(height_input)
        self.add_widget(bomb_input)
        self.add_widget(startbutton)
    
    def startGame(self, width : str, height : str, bomb_count : str):
        """Opens Popup and starts Minesweeper Game"""
        try:
            width = int(width)
        except:
            width = 10
        try:
            height = int(height)
        except:
            height = 10
        try:
            bomb_count = int(bomb_count)
        except:
            bomb_count = 30
        
        layout = BoxLayout(orientation = "vertical")
        game = Popup(title = "Game", content = layout)

        back = Button(text = "Back", size_hint_y = 0.1)
        back.bind(on_release = game.dismiss)

        layout.add_widget(GameBoard(width, height, bomb_count))
        layout.add_widget(back)

        game.open()


class MinesweeperApp(App):
    def build(self):
        return MainMenu()

if __name__ == "__main__":
    MinesweeperApp().run()







