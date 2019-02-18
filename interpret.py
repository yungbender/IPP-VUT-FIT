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

class Instruction:
    def __init__(self):
        self.opcode = None
        self.arg1 = []
        self.arg2 = []
        self.arg3 = []
        self.order = 0

class Lexer():

    def __init__(self):
        return

class Interpret(Lexer):
    
    def __init__(self):
        Lexer.__init__(self)

        """ Frames """
        self.__gf = {}
        self.__tf = None
        self.__lf = None
        self.__frameStack = None

        """ Data stack """
        self.__dataStack = None
        self.__callStack = None

        """ Labels """
        self.__labels = {}

        """ I/O """
        self.__source = 0
        self.__input = 0

        self.__order = 0

        self.__instruction = None
        self.__instrCount = 0


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
        self.__callStack = Stack()

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
        
        """ Get head """
        self.__source = self.__source.getroot()
        prog = self.__source.tag
        head = self.__source.get("language")

        if prog != "program" or head != "IPPcode19":
            self.print_error("Error, wrong XML root element!\n", 32)

        self.__source = self.__source.findall("instruction")
        """ Sorting the instructions by order. """
        try:
            self.__source[:] = sorted(self.__source, key=lambda child: int(child.get("order")))
        except:
            self.print_error("Error, invalid order attributes!\n", 32)

        check_len = len(self.__source)
        self.__instrCount = check_len

        """ Check if the instructions has continuos numbers. """
        for i in range(0, check_len):
            order = self.__source[i]

            if int(order.get("order")) != (i + 1):
                self.print_error("Error, opcodes does have not continous numbers!\n", 32)
            
    """ lexer """
    def get_instruction(self):
        instr = Instruction()

        if self.__order == self.__instrCount:
            instr.opcode = "EOF"
            self.__instruction = instr
            return

        part = self.__source[self.__order]
        instr.opcode = part.get("opcode")

        if instr.opcode.isupper() == False:
            self.print_error("Error, opcode not in uppercase!\n", 32)

        instr.order = int(part.get("order"))

        arg1 = part.find("arg1")
        if arg1 != None:
            instr.arg1.append(arg1.get("type"))
            instr.arg1.append(arg1.text)
        
        arg2 = part.find("arg2")
        if arg2 != None:
            instr.arg2.append(arg2.get("type"))
            instr.arg2.append(arg2.text)
        if len(instr.arg1) == 0 and len(instr.arg2) != 0:
            self.print_error("Error, wrong arguments of function!\n", 32)

        arg3 = part.find("arg3")
        if arg3 != None:
            instr.arg3.append(arg3.get("type"))
            instr.arg3.append(arg3.text)
        if len(instr.arg2) == 0 and len(instr.arg3) != 0:
            self.print_error("Error, wrong arguments of function!\n", 32)

        self.__order += 1
        self.__instruction = instr
    
    def execute(self):
        self.get_instruction()


        

interpret = Interpret()

interpret.parse_args()
interpret.set_up()
interpret.check_xml()

