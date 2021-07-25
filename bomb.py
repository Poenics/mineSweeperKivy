from os import stat
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
from kivy.uix.togglebutton import ToggleButton

"""
TODO
- DONE: Distinguish between flagging and revealing cell (double dropdown/toggle button)
- DONE: Reveal Cell when clicked
- DONE: Flag Cell when clicked
- DONE: Display surrounding Bomb Count and change background color
- DONE: Display Bomb Icon
- DONE: Display Flag Icon
- WIP: Game over when revealing Bomb
- Reveal surrounding Cells when revealing clear Cell
- Win once only all bombs are flagged
- Regenerate Board on Game End
- maybe also Timer and Highscores
- Bild Lizensen?
"""

shovel_icon = ""
flag_icon = ""
flag_color = (1, 0, 0, 1)
bomb_icon = ""
bomb_color = (0, 0, 0, 1)
one_color = (0, 0, 1, 1)
two_color = (0, 0.5, 0, 1)
three_color = (1, 0, 0, 1)
four_color = (0, 0, 0.5, 1)
five_color = (0.5, 0, 0, 1)
six_color = (0, 0.5, 0.5, 1)
seven_color = (0, 0, 0, 1)
eight_color = (0.5, 0.5, 0.5, 1)

class ToolBar(BoxLayout):
    """Tool Bar for switching cell modes or displaying information"""
    def __init__(self, **kwargs):
        """Init for ToolBar"""
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.reveal = ToggleButton(text = shovel_icon, group = "tool", state = "down")
        self.reveal.font_name = "celltext.ttf"
        self.reveal.background_normal = "normal.png"
        self.reveal.background_down = "down.png"
        self.reveal.color = (0,0,0,1)
        self.add_widget(self.reveal)
        self.flag = ToggleButton(text = flag_icon, group = "tool")
        self.flag.font_name = "celltext.ttf"
        self.flag.background_normal = "normal.png"
        self.flag.background_down = "down.png"
        self.flag.color = (0,0,0,1)
        self.add_widget(self.flag)
        self.size_hint_y = 0.05

    def isFlaggingEnabled(self) -> bool:
        """Returns if the Flag Button is enabled or not"""
        if self.reveal.state == "down":
            return False
        elif self.flag.state == "down":
            return True

class GameBoard(GridLayout):
    """Holds all Cells"""
    def __init__(self, width : int, height : int, bomb_count : int, tool_bar: ToolBar, **kwargs):
        """Game Board Init"""
        super(GameBoard, self).__init__(**kwargs)
        self.tool_bar = tool_bar
        self.rows = height
        self.cols = width
        self.field = np.zeros((height,width), dtype=bool)
        self.first_reveal = True

        # Adjusts bomb count if ist less than zero or more than the amount of cells
        if bomb_count < 0:
            bomb_count = 0
        if bomb_count > width*height:
            bomb_count = width*height
        self.bomb_count = bomb_count

        # if bomb count is more than half of the cells, randomly removes bombs until bomb count is reached
        # else randomly adds bombs until bomb count is reached
        if bomb_count > 1/2 * width*height:
            self.field = 1- self.field
            cell_value = False
        else:
            cell_value = True
        
        while self.field.sum() != bomb_count:
            self.field[random.randint(0,height-1)][random.randint(0,width-1)] = cell_value

        self.field = list(map(lambda x: list(x), self.field))
        # adds cells
        for i in range(height):
            for j in range(width):
                cell = Cell(self.field[i][j], (j,i), self)
                self.add_widget(cell)
                self.field[i][j] = cell

        for i in self.children:
            i.conceal()
    def lose(self):
        for i in self.children:
            i.disabled = True
            i.updateDisplay()
    

    
class Cell(Button):
    """Minesweeper Cell"""
    def __init__(self, is_bomb : bool, index : "tuple[int, int]", board : GameBoard, **kwargs):
        """Minesweeper Cell init"""
        super(Cell, self).__init__(**kwargs)
        
        # Sets bomb-indicator and xy-position
        self.is_bomb = is_bomb
        self.is_flagged = False
        self.x_index = index[0]
        self.y_index = index[1]
        self.game_board = board
        self.text = f"{self.x_index} {self.y_index}"
        self.bind(on_release = self.pressed)
        self.font_name = "celltext.ttf"
        # random.choice([lambda : [setattr(self, "text", flag_icon), setattr(self, "color", (150,1,1,1))], lambda : [setattr(self, "text", bomb_icon), setattr(self, "color", (1,1,1,1))], ])()
        if self.is_bomb:
            self.display_bomb()
        else:
            self.display_flag()
        self.background_down = "down.png"
        self.background_disabled_down = "down.png"
        self.background_disabled_normal = "down.png"

    
    def pressed(self, instance: Button):
        """Callback for the Cell"""
        # index = (self.x_index, self.y_index)
        # print("Index is: %s "% str(index) + "Bomb? " + str(self.is_bomb))
        # self.around(int(index[0]), int(index[1]))
        flagging_enabled = self.game_board.tool_bar.isFlaggingEnabled()
        if self.game_board.first_reveal and not flagging_enabled:
            self.game_board.bomb_count -= self.is_bomb
            self.is_bomb = False
            self.game_board.first_reveal = False
        
        if not flagging_enabled and self.is_bomb:
            self.game_board.lose()
        elif not flagging_enabled and not self.is_flagged:
            self.updateDisplay()
        elif flagging_enabled and not self.is_flagged:
            self.is_flagged = True
            self.display_flag()
        elif flagging_enabled:
            self.conceal()
            self.is_flagged = False
        

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
    
    def getNeighbours(self, x_index: int = -1, y_index: int = -1):
        """Gets Surrounding Cells and returns them"""
        temp_list = [[],[],[]]
        width = self.game_board.cols -1 
        height = self.game_board.rows -1
        y_index = self.y_index if y_index == -1 else y_index
        x_index = self.x_index if x_index == -1 else x_index

        temp_list[0].append(self.getval(y_index - 1, x_index - 1) if x_index > 0 and y_index > 0 else None)
        temp_list[0].append(self.getval(y_index - 1, x_index) if y_index > 0 else None)
        temp_list[0].append(self.getval(y_index - 1, x_index + 1) if x_index < width and y_index > 0 else None)

        temp_list[1].append(self.getval(y_index, x_index - 1) if x_index > 0 else None)
        temp_list[1].append(self)
        temp_list[1].append(self.getval(y_index, x_index + 1) if x_index < width else None)
        
        temp_list[2].append(self.getval(y_index + 1, x_index - 1) if x_index > 0 and y_index < height else None)
        temp_list[2].append(self.getval(y_index + 1, x_index) if y_index < height else None)
        temp_list[2].append(self.getval(y_index + 1, x_index + 1) if x_index < width and y_index < height else None)

        temp_list = np.array(temp_list)
        return temp_list
    
    def getBombNeighbours(self):
        """Returns the amount of Bomb Neighbours"""
        return self.fieldsum(self.getNeighbours()) - self.is_bomb
    
    def getval(self, y_index : int, x_index : int):
        """Gets field value"""
        return self.game_board.field[y_index][x_index]

    @staticmethod
    def fieldsum(field):
        """Sums the amount of bombs in a given field"""
        amount = 0
        for i in field:
            for j in i:
                if j is None:
                    continue
                else:
                    amount += j.is_bomb
        return amount

    @staticmethod
    def flagsum(field):
        """Sums the amount of flagged cells in a given field"""
        amount = 0
        for i in field:
            for j in i:
                if j is None:
                    continue
                else:
                    amount += j.is_flagged
        return amount

    def display_flag(self):
        """Displays the Flag"""
        self.font_name = "celltext.ttf"
        self.text = flag_icon
        self.color = flag_color
        self.background_normal = "normal.png"

    def display_bomb(self):
        """Displays the Bomb"""
        self.disabled = True
        self.font_name = "celltext.ttf"
        self.text = bomb_icon
        self.disabled_color = bomb_color
        self.background_disabled_normal = "normal.png"
        self.background_normal = "normal.png"

    def display_zero(self):
        """Displays the Zero"""
        self.disabled = True
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = ""
        self.color = (0,0,0,1)
        self.background_normal = "down.png"

    def display_one(self):
        """Displays the One"""
        self.disabled = True
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = "1"
        self.disabled_color = one_color
        self.bold = True
        self.background_normal = "down.png"

    def display_two(self):
        """Displays the Two"""
        self.disabled = True
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = "2"
        self.disabled_color = two_color
        self.background_normal = "down.png"

    def display_three(self):
        """Displays the Three"""
        self.disabled = True
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = "3"
        self.disabled_color = three_color
        self.background_normal = "down.png"

    def display_four(self):
        """Displays the Four"""
        self.disabled = True
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = "4"
        self.disabled_color = four_color
        self.background_normal = "down.png"
    
    def display_five(self):
        """Displays the Five"""
        self.disabled = True
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = "5"
        self.disabled_color = five_color
        self.background_normal = "down.png"

    def display_six(self):
        """Displays the Six"""
        self.disabled = True
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = "6"
        self.disabled_color = six_color
        self.background_normal = "down.png"

    def display_seven(self):
        """Displays the Seven"""
        self.disabled = True
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = "7"
        self.disabled_color = seven_color
        self.background_normal = "down.png"

    def display_eight(self):
        """Displays the Eight"""
        self.disabled = True
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = "8"
        self.disabled_color = eight_color
        self.background_normal = "down.png"
    
    def conceal(self):
        """Makes the Cell text blank"""
        self.display_zero()
        self.disabled = False
        self.background_normal = "normal.png"
    
    def updateDisplay(self):
        """Updates Display based on Neighbours and bomb status"""
        display_list = [self.display_zero, self.display_one, self.display_two, self.display_three, self.display_four, self.display_five, self.display_six, self.display_seven, self.display_eight ]
        bomb_neighbours = self.getBombNeighbours()

        # Prevents a 3x3 square of bombs
        if bomb_neighbours == 8 and self.is_bomb:
            self.is_bomb = False
        
        if self.is_bomb:
            self.display_bomb()
        else:
            display_list[bomb_neighbours]()
        
class MainMenu(BoxLayout):
    """Main Menu for the Minesweeper App"""
    def __init__(self, **kwargs):
        """Constructing Main Menu"""
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # Adding Widgets
        width_input = TextInput(hint_text = "Insert Board Width", text = "20")
        width_input.background_normal = "normal.png"
        width_input.background_active = "normal.png"
        width_input.background_color = (1.1,1.1,1.1,1)
        width_input.halign = "center"
        width_input.valign = "middle"
        height_input = TextInput(hint_text = "Insert Board height", text = "20")
        height_input.background_normal = "normal.png"
        height_input.background_active = "normal.png"
        height_input.background_color = (1.1,1.1,1.1,1)
        height_input.halign = "center"
        bomb_input = TextInput(hint_text = "Insert Bomb Count", text = "99")
        bomb_input.background_normal = "normal.png"
        bomb_input.background_active = "normal.png"
        bomb_input.background_color = (1.1,1.1,1.1,1)
        bomb_input.halign = "center"
        startbutton = Button(text = "start")
        startbutton.bind(on_release = lambda x: self.startGame(width_input.text, height_input.text, bomb_input.text))
        startbutton.background_normal = "normal.png"
        startbutton.background_down = "down.png"
        startbutton.background_color = (.8,.8,.8,1)
        startbutton.color = (0,0,0,1)

        self.add_widget(width_input)
        self.add_widget(height_input)
        self.add_widget(bomb_input)
        self.add_widget(startbutton)
    
    def startGame(self, width : str, height : str, bomb_count : str):
        """Opens Popup and starts Minesweeper Game"""
        try:
            width = int(width)
        except:
            width = 20
        try:
            height = int(height)
        except:
            height = 20
        try:
            bomb_count = int(bomb_count)
        except:
            bomb_count = 99
        
        layout = BoxLayout(orientation = "vertical")
        game = Popup(title = "Game", content = layout)

        tool_bar = ToolBar()
        layout.add_widget(tool_bar)
        back = Button(text = "Back", size_hint_y = 0.1)
        back.bind(on_release = game.dismiss)
        back.background_normal = "normal.png"
        back.background_down = "down.png"
        back.color = (0,0,0,1)
        back.background_color = (.8,.8,.8,1)

        layout.add_widget(GameBoard(width, height, bomb_count, tool_bar))
        layout.add_widget(back)

        game.open()


class MinesweeperApp(App):
    def build(self):
        return MainMenu()

if __name__ == "__main__":
    MinesweeperApp().run()







