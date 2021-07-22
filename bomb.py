import numpy as np
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

# w = int(input("Width: "))
# h = int(input("Height: "))
w = 5
h = 5

field = np.zeros((w, h), dtype=bool)


def setBomb(y, x):
    field[y][x]=1

setBomb(0, 3)
setBomb(1, 2)



class MyGrid(GridLayout):
    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)
        self.cols = w
        for y in range(h):
            for x in range(w):
        # button:
                self.submit = Button(text=str(y)+" "+str(x))
                self.submit.bind(on_press=self.pressed)
                self.add_widget(self.submit)

    
    def pressed(self, instance):
        ind = ("%s" % instance.text).split(" ")
        print("Index is: %s "% instance.text + "Bomb? " + str(field[int(ind[0])][int(ind[1])]))
        around(int(ind[0]), int(ind[1]))
        
    


class MyApp(App):
    def build(self):
        return MyGrid()

def around(y, x):
    # i hate this but i really have to sleep now (its past 1am)
    if y != 0:
        top = y-1
    else:
        top = y
    if y != h:
        bottom = y+2
    else:
        bottom = y
    if x != 0:
        strange = x-1
    else:
        strange = x
    if x != w:
        charm = x+2
    else:
        charm = x
    # you have no idea how much i hate this
    
    temp = field[top:bottom, strange:charm]
    print(temp)
    print("Amount of Bombs near: " + str(temp.sum()))


if __name__ == "__main__":
    MyApp().run()







