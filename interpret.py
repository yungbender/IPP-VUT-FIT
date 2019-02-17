import sys, re
import xml.etree.ElementTree as ET

class Stack:
    __stack = []

    def push(self, item):
        self.__stack.append(item)

    def pop(self):
        return self.__stack.pop()
    
    def head(self):
        return self.__stack[len(self.__stack) - 1]

    def is_empty(self):
        return self.items == []

class Interpret:

    """ Frames """
    __gf = {}
    __tf = None
    __lf = None
    __frameStack = None

    """ Data stack """
    __dataStack = None

    """ I/O """
    __source = 0
    __input = 0

    """ Function prints out given error message and exits with given number. """
    def print_error(self, message, number):
        sys.stderr.write(message)
        sys.exit(number)

    """ Function parses arguments from user, and checks if arguments are written correctly. """
    def parse_args(self):
        argc = 1
        help_re = re.compile(r"^--help$")
        is_help = list(filter(help_re.search, sys.argv))

        if is_help and len(sys.argv) == 2:
            sys.stdout.write("This is help message\n")
            sys.exit(0)
        elif is_help:
            self.print_error("Error, unknown combination with --help!\n", 10)
        
        source_re = re.compile(r"^--source=.+$")
        is_source = list(filter(source_re.search, sys.argv))

        if is_source and len(is_source) == 1:
            argc+= 1
            path = is_source[0].split("=", 1)
            self.__source = path[1]
        elif is_source:
            self.print_error("Error, repeating --source argument!\n", 10)
        
        input_re = re.compile(r"^--input=.+$")
        is_input = list(filter(input_re.search, sys.argv))

        if is_input and len(is_source) == 1:
            argc+= 1
            path = is_input[0].split("=", 1)
            self.__input = path[1]
        elif is_input:
            self.print_error("Error, repeating --input argument!\n", 10)
        
        if argc != len(sys.argv):
            self.print_error("Error, unknown parameters used!\n", 10)
        elif self.__source == self.__input:
            self.print_error("Error, at least 1 argument (source/file) must be used!\n", 10)
    
    """ Method allocates stacks and opens the files for input and source. """
    def set_up(self):
        self.__dataStack = Stack()
        self.__frameStack = Stack()

        try:
            self.__source = open(self.__source, "r")
            self.__source = self.__source.read()

            self.__input = open(self.__input, "r")
        except:
            self.print_error("Error, couldnt open source/input file!\n", 11)
    
    """ Method parses source XML file, checks if its well-formed and checks the required head. """
    def check_xml(self):
        try:
            self.__source = ET.ElementTree(ET.fromstring(self.__source))
        except:
            self.print_error("Error, xml is not well-formed!\n",11)
        
        root = self.__source.getroot()
        print(root.attrib["language"])
        test = root.find("instruction")
        print(test)
        #test = ET.tostring(root, encoding="utf-8", method="xml")
        #print(test.decode("utf-8"))
"""         root[:] = sorted(root, key=lambda intt: root.find("order"))
        xmlstr = ET.tostring(root, encoding="utf-8", method="xml")
        print(xmlstr.decode("utf-8")) """

interpret = Interpret()
interpret.parse_args()
interpret.set_up()
interpret.check_xml()