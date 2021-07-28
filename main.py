import random
import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
import threading
import time

"""
TODO
- DONE: Distinguish between flagging and revealing cell (double dropdown/toggle button)
- DONE: Reveal Cell when clicked
- DONE: Flag Cell when clicked
- DONE: Display surrounding Bomb Count and change background color
- DONE: Display Bomb Icon
- DONE: Display Flag Icon
- DONE: Game over when revealing Bomb
- DONE: Reveal surrounding Cells when revealing clear Cell
- DONE Win once only all bombs are flagged
- DONE: Regenerate Board on Game End
- DONE: maybe also Timer and Highscores
- DONE: Bild Lizensen?
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

class StatusLabel(Button):
    """Label that displays a few useful informations, e.g. Timer, Bombs left,..."""
    def __init__(self, **kwargs):
        """Status Label init"""
        super().__init__(**kwargs)
        self.thread = threading.Thread(target = self.timer)
        self.running = True
        self.time = 0
        self.bomb_count = 0
        self.disabled = True
        self.background_disabled_normal = "down.png"
        self.color = (0,0,0,1)
        
    def updateText(self):
        """Updates Label text"""
        self.text = f"{self.time // 60}:{self.time % 60:02d} | Flags remaining: {self.bomb_count}"

    def timer(self):
        """Function called by Thread, maintains Timer"""
        while self.running:
            time.sleep(1)
            self.time  += 1
            self.updateText()
        self.time = 0
        
    def startTimer(self):
        """Starts the internal Thread"""
        self.running = True
        self.thread.start()

    def stopTimer(self):
        """Stops the internal Thread"""
        self.running = False

    def getScore(self, width, height, bomb_count):
        """Returns the score"""
        return int(1/(self.time+1) * width * height * bomb_count + 1)

    def reset(self):
        """Resets the Status Label"""
        self.stopTimer()
        self.thread = threading.Thread(target = self.timer)
        self.bomb_count = 0
        self.text = "0:00"
    


class ToolBar(BoxLayout):
    """Tool Bar for switching cell modes or displaying information"""
    def __init__(self, **kwargs):
        """Init for ToolBar"""
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = 0.05

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

        self.status_label = StatusLabel(text = "0:00", size_hint_x = 2)
        self.add_widget(self.status_label)

    def isFlaggingEnabled(self) -> bool:
        """Returns if the Flag Button is enabled or not"""
        if self.reveal.state == "down":
            return False
        elif self.flag.state == "down":
            return True
    
    def reset(self):
        """Resets the Toolbar"""
        self.status_label.reset()

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
        self.init_bomb_count = bomb_count

        # Adjusts bomb count if ist less than zero or more than the amount of cells
        if bomb_count < 0:
            bomb_count = 0
        if bomb_count > width*height:
            bomb_count = width*height
        self.bomb_count = bomb_count
        self.progress = bomb_count
        self.tool_bar.status_label.bomb_count = self.bomb_count

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
    
    def restart(self):
        """Restarts The Game"""
        self.clear_widgets()
        bomb_count = self.init_bomb_count
        width = self.cols
        height = self.rows
        self.tool_bar.reset()
        self.field = np.zeros((height,width), dtype=bool)
        self.first_reveal = True

        # Adjusts bomb count if ist less than zero or more than the amount of cells
        if bomb_count < 0:
            bomb_count = 0
        if bomb_count > width*height:
            bomb_count = width*height
        self.bomb_count = bomb_count
        self.progress = bomb_count
        self.tool_bar.status_label.bomb_count = self.bomb_count

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

    def winCheck(self):
        """Checks, if Progress is 0"""
        if self.progress == 0:
            self.win()

    def lose(self):
        """Game Over function"""
        for i in self.children:
            i.disabled = True
            i.reveal()
        self.tool_bar.status_label.stopTimer()
        layout = BoxLayout(orientation = "vertical")
        game = Popup(title = "Game Over", content = layout, size_hint_y = 0.2, size_hint_x = 0.35, title_align = "center")

        back = Button(text = "Restart", size_hint_y = 0.1)
        back.bind(on_release = lambda x: [game.dismiss(x), self.restart()])
        back.background_normal = "normal.png"
        back.background_down = "down.png"
        back.color = (0,0,0,1)
        back.background_color = (.8,.8,.8,1)

        layout.add_widget(back)

        game.open()

    
    def win(self):
        """Game Won function"""
        for i in self.children:
            i.disabled = True
            i.reveal()
        self.tool_bar.status_label.stopTimer()
        layout = BoxLayout(orientation = "vertical")
        game = Popup(title = f"You Won! Score: {self.tool_bar.status_label.getScore(self.cols, self.rows, self.bomb_count)}", content = layout, size_hint_y = 0.2, size_hint_x = 0.35, title_align = "center")

        back = Button(text = "Restart", size_hint_y = 0.1)
        back.bind(on_release = lambda x: [game.dismiss(x), self.restart()])
        back.background_normal = "normal.png"
        back.background_down = "down.png"
        back.color = (0,0,0,1)
        back.background_color = (.8,.8,.8,1)

        layout.add_widget(back)

        game.open()

    
class Cell(Button):
    """Minesweeper Cell"""
    def __init__(self, is_bomb : bool, index : "tuple[int, int]", board : GameBoard, **kwargs):
        """Minesweeper Cell init"""
        super(Cell, self).__init__(**kwargs)
        
        # Sets bomb-indicator and xy-position
        self.is_bomb = is_bomb
        self.is_flagged = False
        self.is_revealed = False
        self.x_index = index[0]
        self.y_index = index[1]
        self.game_board = board
        self.text = f"{self.x_index} {self.y_index}"
        self.bind(on_release = self.pressed)
        self.font_name = "celltext.ttf"
        # random.choice([lambda : [setattr(self, "text", flag_icon), setattr(self, "color", (150,1,1,1))], lambda : [setattr(self, "text", bomb_icon), setattr(self, "color", (1,1,1,1))], ])()
        if self.is_bomb:
            self.displayBomb()
        else:
            self.displayFlag()
        self.background_down = "down.png"
        self.background_disabled_down = "down.png"
        self.background_disabled_normal = "down.png"

    
    def pressed(self, instance: Button = None):
        """Callback for the Cell"""
        # index = (self.x_index, self.y_index)
        # print("Index is: %s "% str(index) + "Bomb? " + str(self.is_bomb))
        # self.around(int(index[0]), int(index[1]))
        if self.game_board.first_reveal:
            self.game_board.bomb_count -= self.is_bomb
            self.game_board.progress -= self.is_bomb
            self.game_board.tool_bar.status_label.bomb_count -= self.is_bomb
            self.is_bomb = False
            self.game_board.first_reveal = False
            self.cascade()
            self.game_board.tool_bar.status_label.startTimer()
            return
        # print("he")
        flagging_enabled = self.game_board.tool_bar.isFlaggingEnabled()
        
        if flagging_enabled:
            if self.is_revealed:
                return
            elif self.is_flagged:
                self.is_flagged = False
                self.conceal()
                self.game_board.tool_bar.status_label.bomb_count += 1
                if self.is_bomb:
                    self.game_board.progress += 1
                else:
                    self.game_board.progress -= 1
                self.game_board.winCheck()
            else:
                self.is_flagged = True
                self.displayFlag()
                self.game_board.tool_bar.status_label.bomb_count -= 1
                if self.is_bomb:
                    self.game_board.progress -= 1
                else:
                    self.game_board.progress += 1
                self.game_board.winCheck()
        else:
            if self.is_flagged:
                return
            elif self.is_revealed and self.getFlagNeighbours() == self.getBombNeighbours():
                neigbours = list(filter(lambda x: not x.is_flagged and not x.is_revealed and not x == self,self.getNeighboursFlat()))
                for i in neigbours:
                    i.cascade()
            elif self.is_revealed:
                return
            elif self.is_bomb:
                self.game_board.lose()
            else:
                self.cascade()       

    def around(self, x_index: int, y_index: int):
        """Gets Surrounding Cell Values and counts Bombs"""
        temp_list = [[],[],[]]
        width = self.game_board.cols -1 
        height = self.game_board.rows -1

        temp_list[0].append(self.getCell(y_index - 1, x_index - 1) if x_index > 0 and y_index > 0 else None)
        temp_list[0].append(self.getCell(y_index - 1, x_index) if y_index > 0 else None)
        temp_list[0].append(self.getCell(y_index - 1, x_index + 1) if x_index < width and y_index > 0 else None)

        temp_list[1].append(self.getCell(y_index, x_index - 1) if x_index > 0 else None)
        temp_list[1].append(self.is_bomb)
        temp_list[1].append(self.getCell(y_index, x_index + 1) if x_index < width else None)
        
        temp_list[2].append(self.getCell(y_index + 1, x_index - 1) if x_index > 0 and y_index < height else None)
        temp_list[2].append(self.getCell(y_index + 1, x_index) if y_index < height else None)
        temp_list[2].append(self.getCell(y_index + 1, x_index + 1) if x_index < width and y_index < height else None)

        temp_list = np.array(temp_list)
        print(temp_list)
        print("Amount of Bombs near me: " + str(self.fieldSum(temp_list)-self.is_bomb))
    
    def getNeighbours(self, x_index: int = -1, y_index: int = -1):
        """Gets Surrounding Cells and returns them"""
        temp_list = [[],[],[]]
        width = self.game_board.cols -1 
        height = self.game_board.rows -1
        y_index = self.y_index if y_index == -1 else y_index
        x_index = self.x_index if x_index == -1 else x_index

        temp_list[0].append(self.getCell(y_index - 1, x_index - 1) if x_index > 0 and y_index > 0 else None)
        temp_list[0].append(self.getCell(y_index - 1, x_index) if y_index > 0 else None)
        temp_list[0].append(self.getCell(y_index - 1, x_index + 1) if x_index < width and y_index > 0 else None)

        temp_list[1].append(self.getCell(y_index, x_index - 1) if x_index > 0 else None)
        temp_list[1].append(self)
        temp_list[1].append(self.getCell(y_index, x_index + 1) if x_index < width else None)
        
        temp_list[2].append(self.getCell(y_index + 1, x_index - 1) if x_index > 0 and y_index < height else None)
        temp_list[2].append(self.getCell(y_index + 1, x_index) if y_index < height else None)
        temp_list[2].append(self.getCell(y_index + 1, x_index + 1) if x_index < width and y_index < height else None)

        temp_list = np.array(temp_list)
        return temp_list
    
    def getNeighboursFlat(self, x_index: int = -1, y_index: int = -1):
        """Gets Surrounding Cells and returns them"""
        temp_list = []
        width = self.game_board.cols -1 
        height = self.game_board.rows -1
        y_index = self.y_index if y_index == -1 else y_index
        x_index = self.x_index if x_index == -1 else x_index
        

        temp_list.append(self.getCell(y_index - 1, x_index - 1) if x_index > 0 and y_index > 0 else None)
        temp_list.append(self.getCell(y_index - 1, x_index) if y_index > 0 else None)
        temp_list.append(self.getCell(y_index - 1, x_index + 1) if x_index < width and y_index > 0 else None)

        temp_list.append(self.getCell(y_index, x_index - 1) if x_index > 0 else None)
        temp_list.append(self)
        temp_list.append(self.getCell(y_index, x_index + 1) if x_index < width else None)
        
        temp_list.append(self.getCell(y_index + 1, x_index - 1) if x_index > 0 and y_index < height else None)
        temp_list.append(self.getCell(y_index + 1, x_index) if y_index < height else None)
        temp_list.append(self.getCell(y_index + 1, x_index + 1) if x_index < width and y_index < height else None)

        temp_list = np.array(temp_list)
        pre_proc_list = list(filter(lambda x: x is not None, temp_list))
        return pre_proc_list
    
    def getNeighboursCascade(self, x_index: int = -1, y_index: int = -1):
        """Gets Orthogonal Cells and returns them"""
        temp_list = []
        width = self.game_board.cols -1 
        height = self.game_board.rows -1
        y_index = self.y_index if y_index == -1 else y_index
        x_index = self.x_index if x_index == -1 else x_index
        

        temp_list.append(self.getCell(y_index - 1, x_index - 1) if x_index > 0 and y_index > 0 else None)
        temp_list.append(self.getCell(y_index - 1, x_index) if y_index > 0 else None)
        temp_list.append(self.getCell(y_index - 1, x_index + 1) if x_index < width and y_index > 0 else None)

        temp_list.append(self.getCell(y_index, x_index - 1) if x_index > 0 else None)
        temp_list.append(self)
        temp_list.append(self.getCell(y_index, x_index + 1) if x_index < width else None)
        
        temp_list.append(self.getCell(y_index + 1, x_index - 1) if x_index > 0 and y_index < height else None)
        temp_list.append(self.getCell(y_index + 1, x_index) if y_index < height else None)
        temp_list.append(self.getCell(y_index + 1, x_index + 1) if x_index < width and y_index < height else None)

        temp_list = np.array(temp_list)
        pre_proc_list = list(filter(lambda x: x is not None, temp_list))
        return pre_proc_list
    
    def getBombNeighbours(self):
        """Returns the amount of Bomb Neighbours"""
        return self.fieldSum(self.getNeighbours()) - self.is_bomb
        
    def getFlagNeighbours(self):
        """Returns the amount of Flag Neighbours"""
        return self.flagSum(self.getNeighbours()) - self.is_flagged
    
    def getCell(self, y_index : int, x_index : int):
        """Gets field value"""
        return self.game_board.field[y_index][x_index]

    @staticmethod
    def fieldSum(field):
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
    def flagSum(field):
        """Sums the amount of flagged cells in a given field"""
        amount = 0
        for i in field:
            for j in i:
                if j is None:
                    continue
                else:
                    amount += j.is_flagged
        return amount

    def displayFlag(self):
        """Displays the Flag"""
        self.font_name = "celltext.ttf"
        self.text = flag_icon
        self.color = flag_color
        self.disabled_color = flag_color
        self.background_disabled_normal = "normal.png"
        self.background_normal = "normal.png"

    def displayBomb(self):
        """Displays the Bomb"""
        self.disabled = True
        self.font_name = "celltext.ttf"
        self.text = bomb_icon
        self.disabled_color = bomb_color
        self.background_disabled_normal = "normal.png"
        self.background_normal = "normal.png"

    def displayZero(self):
        """Displays the Zero"""
        self.disabled = True
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = ""
        self.color = (0,0,0,1)
        self.background_normal = "down.png"

    def displayOne(self):
        """Displays the One"""
        self.disabled = False
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = "1"
        self.disabled_color = one_color
        self.color = one_color
        self.bold = True
        self.background_normal = "down.png"

    def displayTwo(self):
        """Displays the Two"""
        self.disabled = False
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = "2"
        self.disabled_color = two_color
        self.color = two_color
        self.background_normal = "down.png"

    def displayThree(self):
        """Displays the Three"""
        self.disabled = False
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = "3"
        self.disabled_color = three_color
        self.color = three_color
        self.background_normal = "down.png"

    def displayFour(self):
        """Displays the Four"""
        self.disabled = False
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = "4"
        self.disabled_color = four_color
        self.color = four_color
        self.background_normal = "down.png"
    
    def displayFive(self):
        """Displays the Five"""
        self.disabled = False
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = "5"
        self.disabled_color = five_color
        self.color = five_color
        self.background_normal = "down.png"

    def displaySix(self):
        """Displays the Six"""
        self.disabled = False
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = "6"
        self.disabled_color = six_color
        self.color = six_color
        self.background_normal = "down.png"

    def displaySeven(self):
        """Displays the Seven"""
        self.disabled = False
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = "7"
        self.disabled_color = seven_color
        self.color = seven_color
        self.background_normal = "down.png"

    def displayEight(self):
        """Displays the Eight"""
        self.disabled = False
        self.font_name = "data/fonts/Roboto-Regular.ttf"
        self.text = "8"
        self.disabled_color = eight_color
        self.color = eight_color
        self.background_normal = "down.png"
    
    def conceal(self):
        """Makes the Cell text blank"""
        self.displayZero()
        self.disabled = False
        self.background_normal = "normal.png"
    
    def updateDisplay(self):
        """Updates Display based on Neighbours and bomb status"""
        if self.is_revealed:
            return
        if self.is_flagged and self.is_bomb:
            self.displayFlag()
            return
        self.is_revealed = True
        display_list = [self.displayZero, self.displayOne, self.displayTwo, self.displayThree, self.displayFour, self.displayFive, self.displaySix, self.displaySeven, self.displayEight ]
        bomb_neighbours = self.getBombNeighbours()

        # Prevents a 3x3 square of bombs
        if bomb_neighbours == 8 and self.is_bomb:
            self.is_bomb = False
        
        if self.is_bomb:
            self.displayBomb()
        else:
            display_list[bomb_neighbours]()
    
    def reveal(self):
        """Reveals Cell"""
        self.is_revealed = True
        display_list = [self.displayZero, self.displayOne, self.displayTwo, self.displayThree, self.displayFour, self.displayFive, self.displaySix, self.displaySeven, self.displayEight ]
        bomb_neighbours = self.getBombNeighbours()

        if self.is_bomb and self.is_flagged:
            self.displayFlag()
        elif self.is_bomb:
            self.displayBomb()
        else:
            display_list[bomb_neighbours]()
    
    def cascade(self):
        """Reveals Cell and reveals orthogonal Cells"""
        if self.is_bomb:
            self.game_board.lose()
            return
        self.reveal()
        neigbours = list(filter(lambda x: not x.is_flagged and not x.is_revealed and not x == self and not x.is_bomb,self.getNeighboursCascade()))
        if self.getBombNeighbours() == 0:
            for i in neigbours:
                i.cascade()
        else:
            neigbours = list(filter(lambda x: x.getBombNeighbours() == 0, neigbours))
            for i in neigbours:
                i.cascade()

        
class MainMenu(BoxLayout):
    """Main Menu for the Minesweeper App"""
    def __init__(self, **kwargs):
        """Constructing Main Menu"""
        super().__init__(**kwargs)
        self.orientation = "vertical"
        # Adding Widgets
        width_input = TextInput(hint_text = "Insert Board Width (max 20, min 2)", text = "20", multiline=False)
        width_input.background_normal = "normal.png"
        width_input.background_active = "normal.png"
        width_input.background_color = (1.1,1.1,1.1,1)
        width_input.halign = "center"
        width_input.valign = "middle"
        height_input = TextInput(hint_text = "Insert Board height (max 20, min 2)", text = "20", multiline=False)
        height_input.background_normal = "normal.png"
        height_input.background_active = "normal.png"
        height_input.background_color = (1.1,1.1,1.1,1)
        height_input.halign = "center"
        bomb_input = TextInput(hint_text = "Insert Bomb Count", text = "99", multiline=False)
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
            if width > 20 or width < 2:
                width = 20
        except:
            width = 20
        try:
            height = int(height)
            if height > 20 or height < 2:
                height = 20
        except:
            height = 20
        try:
            bomb_count = int(bomb_count)
        except:
            bomb_count = 99
        
        layout = BoxLayout(orientation = "vertical")
        game = Popup(title = "", content = layout)
        game.separator_height = 0

        tool_bar = ToolBar()
        back = Button(text = "Back", size_hint_y = 0.1)
        back.bind(on_release = lambda x: [game.dismiss(x), tool_bar.status_label.stopTimer()])
        back.background_normal = "normal.png"
        back.background_down = "down.png"
        back.color = (0,0,0,1)
        back.background_color = (.8,.8,.8,1)
        layout.add_widget(back)
        layout.add_widget(tool_bar)

        layout.add_widget(GameBoard(width, height, bomb_count, tool_bar))

        game.open()


class MinesweeperApp(App):
    def build(self):
        return MainMenu()

if __name__ == "__main__":
    MinesweeperApp().run()







