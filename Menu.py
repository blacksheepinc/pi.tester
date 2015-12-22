#!/usr/bin/python
##
## Menu system
## 
## Menu is list of menu items with following format :
## [reference to parent entry identifier,
##  menu entry display title, 
##  positive integer identifier (free choice) if entry goes to submenu if selected OR
##  string with action to be returned when entry is selected]
##
##

## Pin config , GPIO layout ##
#INPUTS
upbutton = 1 #Gpioxx Digital
downbutton = 1 #Gpioxx Digital
selectbutton = 1 #Gpioxx Digital
raw_press_signal = 1 #Gpioxx Analog
raw_wideband_signal = 1 #Gpioxx Analog
#OUTPUTS

# Definition for replace lines in settting file
def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close() 

#Measuring units
displayformat= ["kPa", "bar", "AFR", "lambda"]
o_format= 0 #default  0 means kPa
w_format= 2 #default 2 means AFR

#Get the units from settings file
file_path = 'settings.dat' 
import os
if os.path.exists(file_path):
    a1 = []
    with open(file_path, 'r+') as file:
        for line in file:
            data = line.split()
            a1.append(int(data[0]))
    o_format= a1[0]
    w_format= a1[1]
else:
    with open(file_path, 'w+') as file:
        file.write(str(o_format)+" <--Wideband format:"+displayformat[o_format]) #default kPa
        file.write("\n")
        file.write(str(w_format)+" <--Compression format:"+displayformat[w_format]) #default AFR
        file.write("\n")
        file.close()

#Menu system
Menu =  [
    [0,"Menu Top",1],
    
    [1,"Compression tester",2],
    [1,"O2 tester",3],

    [2,"Run the tester", "comprtester"],
    [2,"Show current value","show_value"],
    [2,"Display format:","pressureformat"],

    [3,"Show current value","widetester"],
    [3,"Display format:","wideformat"],

    ]
    
def getch():
    """
    Reads one character from keyboard without need for pressing RETURN.
    Only works on POSIX/LINUX systems
    """
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


class menu :

    """
    Menu System typically for 2 line LCD and 2 button navigation.
    structure is list of menu items with following format :
    [reference to parent entry identifier,
    menu entry display title, 
    positive integer identifier (free choice) if entry goes to submenu if selected OR
    string with action to be returned when entry is selected]
    """
        
    def __init__(self,structure,ExitLabel = "Back"):

        # Initialize internal variables
        self._menu = []
        i=0
        r={0:0}

        # Copy menu adding indexes
        for item in structure:
            if isinstance(item[2],int): r[item[2]]=i
            self._menu.append([i,r[item[0]],item[1],item[2]])
            i+=1
        self.key = 1
        self.niveau = 1

        # Build internal dictionnary representing menu structure
        self.struct={}
        for item in self._menu:
            if item[0] != 0 :
                if item[1] not in self.struct : self.struct[item[1]] = []
                self.struct[item[1]].append(item[0])

        # Add BACK entry for each level
        for key in self.struct:
            index=len(self._menu)
            self._menu.append([index,key,ExitLabel,-1])
            self.struct[key].append(index)

    def display(self,pos=None):
        """
        Displays the current menu entry as :
        1st line : parent entry
        2nd line : current selected item
        """
        if pos is None : pos = self.key
        self.key = pos
        parent = self._menu[pos][1]
        print str(self.niveau)+":"+self._menu[parent][2]
        print self._menu[pos][2],
        if self._menu[pos][3] == "pressureformat":
            print displayformat[o_format]
        if self._menu[pos][3] == "wideformat":
            print displayformat[w_format]

    def action(self,pos=None):
        """
        Returns action associated with current selected menu item
        None if selected item refers to submenu
        """
        if pos is None : pos = self.key
        self.key=pos
        if isinstance(self._menu[pos][3],str): return self._menu[pos][3]
        return None

    def next(self,pos=None):
        """
        Advances selection to next menu item in same level.
        Rotates to first item when at end of menu level.
        """
        if pos is None : pos = self.key
        self.key=pos
        level = self.struct[self._menu[pos][1]]
        i=level.index(pos)
        i=i+1
        if i >= len(level): i=0
        self.key=level[i]

    def prev(self,pos=None):
        """
        Advances selection to next menu item in same level.
        Rotates to first item when at end of menu level.
        """
        if pos is None : pos = self.key
        self.key=pos
        level = self.struct[self._menu[pos][1]]
        i=level.index(pos)
        i=i-1
        if i >= len(level): i=0
        self.key=level[i]

    def select(self,pos=None):
        """
        Advances to sub menu or parent menu then returns False, OR
        Returns True if selected menu has to be actioned.
        Returns -1 if selected item is EXIT from first level, i.e. quit the menu
        """
        if pos is None : pos = self.key
        self.key=pos
        if self._menu[pos][3] == "pressureformat" : 
            return "changepressure"
        if self._menu[pos][3] == "wideformat" : 
            return "changewideband"
        if isinstance(self._menu[pos][3],str): return True
        if self._menu[pos][3] > 0:
            self.key = self.struct[self._menu[pos][0]][0]
            self.niveau +=1
            return False
        if self._menu[pos][3] == -1:
            self.key = self._menu[pos][1]
            self.niveau -=1
            if self.key == 0 : return -1
            return False

    def up(self,pos=None):
        """
        Goes up one level and returns True
        Returns False if already on top/first level
        Can typically be used after actionning a selection to return to previous menu item
        """
        if pos is None : pos = self.key
        self.key=pos
        if self.niveau == 1 : return False
        self.key = self._menu[pos][1]
        self.niveau -=1
        return True
     
   
import time
def signaltester(test_type):
    if test_type== "pressure":
        signal= raw_press_signal
    if test_type=="wideband":
        signal= raw_wideband_signal
    signal= 1 #csak szimulacio majd torold
    count=0
    while count<5:
        if signal <= 0:
            os.system("clear")
            print "Waiting for "+test_type+" sensor"
            time.sleep(2)
            count= count+1
        else:
            os.system("clear")
            print test_type+" sensor is connected"
            time.sleep(2)
            os.system("clear")
            return None
    os.system("clear")
    print "Sensor not found"
    time.sleep(2)
    return None
    
def pressurecalibration():
    reference_pressure= 0.222 #equals to air pressure
    signal= "idejonjel"
    
if __name__ == "__main__":

    m=menu(Menu)

    while True:
        action=""
        os.system("clear")
        m.display()
        #print MyMenu[6][1]
        c=getch()
        if c == "x" : break
        if c == "n": m.next()  # Simulate NEXT button
        if c == "p" : m.prev()  # Simulate PREV button
        if c == "s":            # Simulate SELECT button
            s=m.select()
            if s :
                if s == -1 : break
                if s == "changepressure" and o_format == 0:
                    o_format= 1
                    replace_line(file_path, 0, str(o_format)+" <--Wideband format:"+displayformat[o_format]+"\n")
                elif s == "changepressure" and o_format == 1:
                    o_format= 0
                    replace_line(file_path, 0, str(o_format)+" <--Wideband format:"+displayformat[o_format]+"\n")
                if s == "changewideband" and w_format == 2:
                    w_format= 3
                    replace_line(file_path, 1, str(w_format)+" <--Compression format:"+displayformat[w_format]+"\n")
                elif s == "changewideband" and w_format == 3:
                    w_format= 2
                    replace_line(file_path, 1, str(w_format)+" <--Compression format:"+displayformat[w_format]+"\n")
                action=m.action()
        if action== Menu[3][2]:#Run the tester
            signaltester("pressure")
            pressurecalibration()
        if action== Menu[4][2]:#Show current compression value
            signaltester("pressure")
            pressurecalibration()
        if action== Menu[6][2]:#Show current wideband value
            signaltester("wideband")
