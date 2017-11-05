class Color:
    def __init__(self):
        self.static_n = 4
        self.static_color = ['green', 'yellow', 'purple', 'red', 'blue']
    def color(self, string):
        return self.red(string) if string == 'False' else self.green(string) if  string == 'True' else self.yellow(string)
    def blue(self, string):
        return '\033[1;34m' + string + '\033[1;0m'
    def red(self, string):
        return '\033[1;31m' + string + '\033[1;0m'
    def purple(self, string):
        return '\033[1;35m' + string + '\033[1;0m'
    def green(self, string):
        return '\033[1;32m' + string + '\033[1;0m'
    def yellow(self, string):
        return '\033[1;33m' + string + '\033[1;0m'
    def white(self, string):
        return '\033[1;37m' + string + '\033[1;0m'
    def rotate(self, string):
        self.static_n += 1
        self.static_n %= 5
        foo = getattr(self, self.static_color[self.static_n])
        return foo(string)

def main():
    C = Color()
    print(C.rotate('toto'))

if __name__ == "__main__":
    main()
