class TerminalColors:
    #Source:    https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-terminal-in-python
    #           https://stackoverflow.com/questions/37340049/how-do-i-print-colored-output-to-the-terminal-in-python/37340245

    PURPLE = '\033[95m'
    PURPLEBACKGROUND = '\033[45m'
    LIGHTBLUE = '\033[94m'
    DARKBLUE = '\033[34m'
    BLUEBACKGROUND = '\033[44m'
    LIGHTCYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    CYANBACKGROUND = '\033[46m'
    LIGHTGREEN = '\033[92m'
    DARKGREEN = '\033[32m'
    GREENBACKGROUND = '\033[42m'
    BLACKONGREENBACKGROUND = '\033[30m\033[42m'
    LIGHTGREY ='\033[37m'
    DARKGREY ='\033[90m'
    GREYBACKGROUND = '\033[47m'
    YELLOW = '\033[93m'
    YELLOWBACKGROUND = '\033[43m'
    BLACKONYELLOWBACKGROUND = '\033[30m\033[43m'
    ORANGE = '\033[33m'
    LIGHTRED = '\033[91m'
    DARKRED = '\033[31m'
    REDBACKGROUND = '\033[41m'
    PINK = '\033[95m'    
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    REVERSE = '\033[7m'
    ENDC = '\033[0m'

class Terminal:
    def __init__(self):
        self.indent=0
        self.space="  "
        self.newline = True

    #the name "indent" is reserved...
    def tab(self):
        self.newline = True
        self.indent+=1

    def untab(self):
        if self.indent > 0:
            self.indent-=1        

    def __write(self, text, color, end):
        indents = ""

        #only when the previous write was not inline
        if(self.newline):
            for i in range(self.indent):
                indents += self.space

        print(indents + color + text + TerminalColors.ENDC, end=end)

    def write(self, text, color=TerminalColors.ENDC):
        self.__write(text, color, "")
        self.newline = False

    def writeln(self, text, color=TerminalColors.ENDC):
        self.__write(text, color, "\n")
        self.newline = True

    def breakline(self, amount=1):
        for i in range(amount):
            print()
