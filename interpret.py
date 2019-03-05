import sys, re
import xml.etree.ElementTree as ET

class Nil:
    def __init__(self):
        self._nil = "nil"

class Stack:
    
    def __init__(self):
        self.__stack = []

    def push(self, item):
        self.__stack.append(item)

    def pop(self):
        return self.__stack.pop()
    
    def head(self):
        return self.__stack[len(self.__stack) - 1]

    def is_empty(self):
        return self.__stack == []

    def get_stack(self):
        return self.__stack
    
    def size(self):
        return len(self.__stack)

class Instruction:
    def __init__(self):
        self.opcode = None
        self.arg1 = []
        self.arg2 = []
        self.arg3 = []
        self.order = 0

    def argc(self):
        count = 0
        if self.arg1:
            count += 1
        if self.arg2:
            count += 1
        if self.arg3:
            count += 1
        
        return count

class Interpret:
    
    def __init__(self):
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
        self.__input = "STDIN"

        self.__order = 0

        self.__instruction = None
        self.__instrCount = 0


    """ Function prints out given error message and exits with given number. """
    def print_error(self, message, number):
        print(message, file=sys.stderr)
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

        if is_input and len(is_input) == 1:
            argc+= 1
            path = is_input[0].split("=", 1)
            self.__input = path[1]
        elif is_input:
            self.print_error("Error, repeating --input argument!\n", 10)
        
        if argc != len(sys.argv):
            self.print_error("Error, unknown parameters used!\n", 10)
        elif self.__source == self.__input:
            self.print_error("Error, at least 1 argument (source/file) must be used!\n", 10)
    
    def set_up(self):
        """ Method allocates stacks and opens the files for input and source. """
        self.__dataStack = Stack()
        self.__frameStack = Stack()
        self.__callStack = Stack()

        try:
            self.__source = open(self.__source, "r")
            backup = self.__source
            self.__source = self.__source.read()
            backup.close()

            if self.__input != "STDIN":
                self.__input = open(self.__input, "r")
        except:
            self.print_error("Error, couldnt open source/input file!\n", 11)
    
    def check_xml(self):
        """ Method parses source XML file, checks if its well-formed and checks the required head. """
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
        instr.opcode = instr.opcode.upper()

        instr.order = int(part.get("order"))

        arg1 = part.find("arg1")
        if arg1 != None:
            instr.arg1.append(arg1.get("type"))
            instr.arg1.append(arg1.text)
            if instr.arg1[1] == None:
                instr.arg1[1] = ""
        
        arg2 = part.find("arg2")
        if arg2 != None:
            instr.arg2.append(arg2.get("type"))
            instr.arg2.append(arg2.text)
            if instr.arg2[1] == None:
                instr.arg2[1] = ""
        if len(instr.arg1) == 0 and len(instr.arg2) != 0:
            self.print_error("Error, wrong arguments of function!\n", 32)

        arg3 = part.find("arg3")
        if arg3 != None:
            instr.arg3.append(arg3.get("type"))
            instr.arg3.append(arg3.text)
            if instr.arg3[1] == None:
                instr.arg3[1] = ""
        if len(instr.arg2) == 0 and len(instr.arg3) != 0:
            self.print_error("Error, wrong arguments of function!\n", 32)

        self.__order += 1
        self.__instruction = instr

    def get_labels(self):
        for instr in self.__source:
            opcode = instr.get("opcode")
            opcode = opcode.upper()

            if opcode == "LABEL":
                
                opcode = instr.get("order")
                
                if not opcode.isdigit():
                   self.print_error("Error, wrong LABEL format!\n", 32)

                args = instr.findall("*")

                if len(args) != 1:
                    self.print_error("Error, wrong LABEL format!\n", 32)

                args = instr.findall("arg1")
                
                if len(args) != 1:
                    self.print_error("Error, wrong LABEL format!\n", 32)

                label = instr[0].get("type")

                if label != "label":
                    self.print_error("Error, wrong LABEL format!\n", 32)

                opcode = int(opcode)
                labName = args[0].text
                if labName in self.__labels:
                    self.print_error("Error, redeclaring LABEL!\n", 52)

                self.__labels[labName] = opcode

    def parse_var(self, arg):
        if len(arg) != 2:
            self.print_error("Error, expecting <var>!\n", 32)

        type_ = arg[0]

        if type_ != "var":
            self.print_error("Error, expecting <var>!\n", 32)

        var = arg[1]

        regex = re.compile(r"^TF@[a-zA-Z_\-$&%*!?]{1}[a-zA-Z0-9_\-$&%*!?]*$|^LF@[a-zA-Z_\-$&%*!?]{1}[a-zA-Z0-9_\-$&%*!?]*$|^GF@[a-zA-Z_\-$&%*!?]{1}[a-zA-Z0-9_\-$&%*!?]*$")
        result = regex.search(var)

        if result == None:
            self.print_error("Error, expencting <var>!\n", 32)

        split = var.split("@", 1)

        if split[0] == "LF":
            frame = self.__lf
        elif split[0] == "TF":
            frame = self.__tf
        elif split[0] == "GF":
            frame = self.__gf

        return frame, split[1]

    def parse_symb(self, arg):
        if len(arg) != 2:
            self.print_error("Error, expecting <symb>!\n", 32)

        if arg[0] == "var":
            frame, dest = self.parse_var(arg)
            return frame, dest, "var"
        
        symb = "@".join(arg)
        regex = re.compile(r"^int@[-+]?[0-9]+$|^bool@true$|^bool@false$|^string@.*|^nil@nil$")

        result = regex.search(symb)

        if result == None:
            self.print_error("Error, expecting <symb>!\n", 32)
        
        split = symb.split("@", 1)
        
        return split[0], split[1], "const"

    def parse_label(self, arg):
        if len(arg) != 2:
            self.print_error("Error, expecting <label>!\n", 32)

        return arg[1]

    def parse_type(self, arg):
        if len(arg) != 2:
            self.print_error("Error, expecting <type>!\n", 32)
        
        if arg[0] != "type":
            self.print_error("Error, expecting <type>!\n", 32)
         
        regex = re.compile(r"^int$|^bool$|^string$")
        result = regex.search(arg[1])

        if result == None:
            self.print_error("Error, expecing <type>!\n", 32)
        
        return arg[1]

    def get_value(self, type_, src):
        if type_ == "int":
            try:
                value = int(src)
            except:
                self.print_error("Error, constant has wrong data type!\n", 57)
        elif type_ == "string":
            if src == None:
                value = ""
            else:
                value = self.format_string(src)
        elif type_ == "bool":
            try:
                srcBool = src.lower()
                if src == "true" or src == "true\n":
                    value = True
                else:
                    value = False
            except:
                self.print_error("Error, constant has wrong data type!\n", 57)
        elif type_ == "nil":
            value = Nil()
        else:
            self.print_error("Error, wrong type attribute!\n", 32)
        
        return value

    def check_if_exists(self, frame, var, op):
        if frame == None:
            self.print_error("Error, " + op + " destination variable frame is not initiliazed!\n", 55)
        elif not var in frame:
            self.print_error("Error, " + op + " destination variable does not exist!\n", 54)

    def check_if_label_exists(self, label, op):
        if label not in self.__labels:
            self.print_error("Error, " + op + " label does not exist!\n", 52)

    def move(self):
        argc = self.__instruction.argc()

        if argc != 2:
            self.print_error("Error, wrong arguments on MOVE instructions!\n", 32)

        frame, dest = self.parse_var(self.__instruction.arg1)

        self.check_if_exists(frame, dest, "MOVE")

        type_, src, whatIsIt = self.parse_symb(self.__instruction.arg2)

        if whatIsIt == "var":
            self.check_if_exists(type_, src, "MOVE")
            
            frame[dest] = type_[src]

        elif whatIsIt == "const":
            value = self.get_value(type_, src)

            frame[dest] = value
        
    def createframe(self):
        self._tf = {}

    def pushframe(self):
        if self._tf == None:
            self.print_error("Error, trying to push undefined TF!\n", 55)
        
        if self._lf != None:
            self.__frameStack.push(self.__lf)
        
        self._lf = self._tf
        self._tf = None

    def popframe(self):
        if self._lf == None:
            self.print_error("Error, no frame to pop!\n", 55)
        
        self._tf = self._lf

        if not self.__frameStack.is_empty:
            self._lf = self.__frameStack.pop()
        else:
            self._lf = None

    def defvar(self):
        argc = self.__instruction.argc()

        if argc != 1:
            self.print_error("Error, wrong arguments on DEFVAR instruction!\n", 32)

        frame, dest = self.parse_var(self.__instruction.arg1)
        
        if frame == None:
            self.print_error("Error, DEFVAR frame does not exit!\n", 55)
        elif dest in frame:
            self.print_error("Error, DEFVAR redefining variable!\n", 52) # pozriet navratovu hodnotu na redefiniciu
        
        frame[dest] = None
        
    def call(self):
        labName = self.parse_label(self.__instruction.arg1)

        if not labName in self.__labels:
            self.print_error("Error, CALL label does not exist!\n", 52)
        
        order = self.__labels[labName]

        self.__callStack.push(self.__order)
        self.__order = order

    def return_(self):
        if self.__callStack.is_empty():
            self.print_error("Error, RETURN there is nowhere to return!\n", 56)
        
        self.__order = self.__callStack.pop()

    def pushs(self):
        argc = self.__instruction.argc()

        if argc != 1:
            self.print_error("Error, wrong arguments on PUSHS instruction!\n", 32)
        
        type_, src, whatIsIt = self.parse_symb(self.__instruction.arg1)

        if whatIsIt == "var":
            self.check_if_exists(type_, src, "PUSHS")

            self.__dataStack.push(type_[src])

        elif whatIsIt == "const":
            value = self.get_value(type_, src)

            self.__dataStack.push(value)

    def pops(self):
        argc = self.__instruction.argc()

        if argc != 1:
            self.print_error("Error, wrong arguments on POPS instruction!\n", 32)

        if self.__dataStack.is_empty():
            self.print_error("Error, POPS data stack is empty!\n", 56)

        frame, dest = self.parse_var(self.__instruction.arg1)

        self.check_if_exists(frame, dest, "POPS")
        
        frame[dest] = self.__dataStack.pop()

    def arithmetic(self, op):
        argc = self.__instruction.argc()

        if argc != 3:
            self.print_error("Error, wrong arguments on " + op + " instruction!\n", 32)

        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, op)

        type_1, src1, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_1, src1, op)
            src1 = type_1[src1]
        else:
            src1 = self.get_value(type_1, src1)

        type_2, src2, whatIsIt = self.parse_symb(self.__instruction.arg3)
        if whatIsIt == "var":
            self.check_if_exists(type_2, src2, op)
            src2 = type_2[src2]
        else:
            src2 = self.get_value(type_2, src2)

        try:
            if op == "ADD":
                frame[dst] = src1 + src2
            elif op == "SUB":
                frame[dst] = src1 - src2
            elif op == "MUL":
                frame[dst] = src1 * src2
            elif op == "IDIV":
                frame[dst] = src1 // src2

        except ZeroDivisionError:
            self.print_error("Error, IDIV division by zero!\n", 57)
        except:
            self.print_error("Error, " + op + " incorrect data types!\n", 53)
                
    def logical(self, op):
        argc = self.__instruction.argc()

        if argc != 3 and op != "NOT":
            self.print_error("Error, wrong arguments on " + op + " instruction!\n", 32)
        elif argc != 2 and op == "NOT":
            self.print_error("Error, wrong arguments on " + op + " instruction!\n", 32)

        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, op)

        type_1, src1, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_1, src1, op)
            src1 = type_1[src1]
        else:
            src1 = self.get_value(type_1, src1)
        
        if op != "NOT":
            type_2, src2, whatIsIt = self.parse_symb(self.__instruction.arg3)
            if whatIsIt == "var":
                self.check_if_exists(type_2, src2, op)
                src2 = type_2[src2]
            else:
                src2 = self.get_value(type_2, src2)

            if type(src1) is not bool or type(src2) is not bool:
                self.print_error("Error, " + op + "operand is not bool!\n", 53)
        
        if op == "AND":
            frame[dst] = (src1 and src2)
        elif op == "OR":
            frame[dst] = (src1 or src2)
        elif op == "NOT":
            frame[dst] = (not src1)

    def int2char(self):
        argc = self.__instruction.argc()

        if argc != 2:
            self.print_error("Error, wrong arguments on INT2CHAR instruction!\n", 32)
        
        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, "INT2CHAR")

        type_, src, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_, src, "INT2CHAR")
            try:
                source = chr(type_[src])
            except:
                self.print_error("Error, INT2CHAR wrong value to change char to!\n.", 58)

        else:
            src = self.get_value(type_, src)
            try:
                source = chr(src)
            except:
                self.print_error("Error, INT2CHAR wrong value to change char to!\n.", 58)

        frame[dst] = source

    def stri2int(self):
        argc = self.__instruction.argc()

        if argc != 3:
            self.print_error("Error, wrong arguments on STRI2INT instruction!\n", 32)

        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, "STRI2INT")

        type_1, src1, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_1, src1, "STRI2INT")
            src1 = type_1[src1]
        else:
            src1 = self.get_value(type_1, src1)

        if type(src1) is not str:
            self.print_error("Error, STRI2INT <symb1> is not string!\n", 57)

        type_2, index, whatIsIt = self.parse_symb(self.__instruction.arg3)
        if whatIsIt == "var":
            self.check_if_exists(type_2, index, "STRI2INT")
            index = type_2[index]
        else:
            index = self.get_value(type_2, index)

        if type(index) is not int:
            self.print_error("Error, STRI2INT <symb2> is not int(index)!\n", 57)

        if index >= len(src1) or index < 0:
            self.print_error("Error, STRI2INT index is out of range!\n", 58)

        frame[dst] = ord(src1[index]) 

    def read(self):
        argc = self.__instruction.argc()

        if argc != 2:
            self.print_error("Error, wrong arguments on READ instruction!\n", 32)

        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, "READ")

        dataType = self.parse_type(self.__instruction.arg2)

        if self.__input == "STDIN":
            value = input()
        else:
            value = self.__input.readline()
            value = value[:-1]

        if dataType == "int":
            try:
                value = int(value)
            except:
                value = 0
        elif dataType == "string":
            try:
                value = str(value)
            except:
                value = ""
        elif dataType == "bool":
            value = value.toupper()
            if value is "TRUE":
                value = True
            else:
                value = False
        
        frame[dst] = value
    
    def format_string(self, string):
        return re.sub(r"\\(\d\d\d)", lambda x: chr(int(x.group(1), 10)), string)

    def write(self):
        argc = self.__instruction.argc()

        if argc != 1:
            self.print_error("Error, wrong arguments on WRITE instruction!\n", 32)

        type_1, src, whatIsIt = self.parse_symb(self.__instruction.arg1)
        if whatIsIt == "var":
            self.check_if_exists(type_1, src, "WRITE")
            src = type_1[src]
        else:
            src = self.get_value(type_1, src)
        if type_1 == "string" or type(src) is str:
            src = self.format_string(src)
        if type(src) is bool:
            if src == True:
                src = "true"
            else:
                src = "false"
        
        print(str(src), end="")

    def concat(self):
        argc = self.__instruction.argc()

        if argc != 3:
            self.print_error("Error, wrong arguments on CONCAT instruction!\n", 32)
        
        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, "CONCAT")

        type_1, src1, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_1, src1, "CONCAT")
            src1 = type_1[src1]
        else:
            src1 = self.get_value(type_1, src1)
        
        type_2, src2, whatIsIt = self.parse_symb(self.__instruction.arg3)
        if whatIsIt == "var":
            self.check_if_exists(type_2, src2, "CONCAT")
            src2 = type_2[src2]
        else:
            src2 = self.get_value(type_2, src2)

        if type(src1) is not str or type(src2) is not str:
            self.print_error("Error, CONCAT not concatinating strings!\n", 53)
        
        frame[dst] = src1 + src2

    def strlen(self):
        argc = self.__instruction.argc()

        if argc != 2:
            self.print_error("Error, wrong arguments on STRLEN instruction!\n", 32)
        
        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, "STRLEN")

        type_1, src1, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_1, src1, "STRLEN")
            src1 = type_1[src1]
        else:
            src1 = self.get_value(type_1, src1)
        
        if type(src1) is not str:
            self.print_error("Error, STRLEN must be string!\n", 53)
        
        frame[dst] = len(src1)

    def getchar(self):
        argc = self.__instruction.argc()

        if argc != 3:
            self.print_error("Error, wrong arguments on GETCHAR instruction!\n", 32)

        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, "GETCHAR")

        type_1, src1, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_1, src1, "GETCHAR")
            src1 = type_1[src1]
        else:
            src1 = self.get_value(type_1, src1)

        if type(src1) is not str:
            self.print_error("Error, GETCHAR <symb1> is not string!\n", 57)

        type_2, index, whatIsIt = self.parse_symb(self.__instruction.arg3)
        if whatIsIt == "var":
            self.check_if_exists(type_2, index, "GETCHAR")
            index = type_2[index]
        else:
            index = self.get_value(type_2, index)

        if type(index) is not int:
            self.print_error("Error, GETCHAR <symb2> is not int(index)!\n", 57)

        if index >= len(src1) or index < 0:
            self.print_error("Error, GETCHAR index is out of range!\n", 58)

        frame[dst] = src1[index]

    def setchar(self):
        argc = self.__instruction.argc()

        if argc != 3:
            self.print_error("Error, wrong arguments on SETCHAR instruction!\n", 32)

        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, "SETCHAR")

        if type(frame[dst]) is not str:
            self.print_error("Error, SETCHAR <var> is not string!\n", 57)

        type_1, index, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_1, index, "SETCHAR")
            index = type_1[index]
        else:
            index = self.get_value(type_1, index)

        if type(index) is not int:
            self.print_error("Error, SETCHAR <symb1> is not int!\n", 57)

        type_2, src, whatIsIt = self.parse_symb(self.__instruction.arg3)
        if whatIsIt == "var":
            self.check_if_exists(type_2, src, "SETCHAR")
            src = type_2[src]
        else:
            src = self.get_value(type_2, src)

        if type(index) is not int:
            self.print_error("Error, SETCHAR <symb2> is not int(index)!\n", 57)

        if index >= len(frame[dst]) or index < 0 or src == "":
            self.print_error("Error, SETCHAR index is out of range!\n", 58)
        
        string = list(frame[dst])
        string[index] = src[0]
        string = "".join(string)
        frame[dst] = string

    def type_(self):
        argc = self.__instruction.argc()

        if argc != 2:
            self.print_error("Error, wrong arguments on TYPE instruction!\n", 32)

        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, "TYPE")

        type_, src, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_, src, "TYPE")
            src = type_[src]
        else:
            src = self.get_value(type_, src)

        if type(src) is int:
            frame[dst] = "int"
        elif type(src) is bool:
            frame[dst] = "bool"
        elif type(src) is str:
            frame[dst] = "string"
        elif type(src) is Nil:
            frame[dst] = "nil"
        elif src is None:
            frame[dst] = ""
        else:
            self.print_error("Error, TYPE error.", 53)

    def jump(self):
        argc = self.__instruction.argc()

        if argc != 1:
            self.print_error("Error, wrong arguments on JUMP instruction!\n", 32)

        label = self.parse_label(self.__instruction.arg1)
        if label not in self.__labels:
            self.print_error("Error, label does not exist!\n", 52)

        self.__order = self.__labels[label]

    def jumpeq(self, type_):
        argc = self.__instruction.argc()

        if argc != 3:
            self.print_error("Error, wrong arguments on JUMPIFEQ or JUMPIFNEQ instruction!\n", 32)

        label = self.parse_label(self.__instruction.arg1)
        self.check_if_label_exists(label, type_)

        type_1, src1, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_1, src1, "JUMPIFEQ")
            src1 = type_1[src1]
        else:
            src1 = self.get_value(type_1, src1)
        
        type_2, src2, whatIsIt = self.parse_symb(self.__instruction.arg3)
        if whatIsIt == "var":
            self.check_if_exists(type_2, src2, "JUMPIFEQ")
            src2 = type_2[src2]
        else:
            src2 = self.get_value(type_2, src2)

        if type(src1) != type(src2):
            self.print_error("Error, JUMPIFEQ are not the same type!\n", 53)
        
        if type_ == "JUMPIFEQ":
            if src1 == src2 or (type(src1) is Nil and type(src2) is Nil):
                self.__order = self.__labels[label]
        elif type_ == "JUMPIFNEQ":
            if src1 != src2 and (type(src1) is not Nil or type(src2) is not Nil):
                self.__order = self.__labels[label]

    def exit_(self):
        argc = self.__instruction.argc()

        if argc != 1:
            self.print_error("Error, wrong arguments on EXIT instruction!\n", 32)
        
        type_, src, whatIsIt = self.parse_symb(self.__instruction.arg1)

        if whatIsIt == "var":
            self.check_if_exists(type_, src, "EXIT")
            source = type_[src]
        
        else:
            source = self.get_value(type_, src)

        if type(source) is not int or not source >= 0 or not source <= 49:
            self.print_error("Error, EXIT wrong exit number!\n", 57)
        
        sys.exit(source)

    def dprint(self):
        argc = self.__instruction.argc()

        if argc != 1:
            self.print_error("Error, wrong arguments on DPRINT instruction!\n", 32)

        frame, src = self.parse_var(self.__instruction.arg1)

        self.check_if_exists(frame, src, "DPRINT")

        sys.stderr.write(frame[src])

    def break_(self):
        argc = self.__instruction.argc()
        if argc != 0:
            self.print_error("Error, wrong arguments on BREAK instruction!\n", 32)

        sys.stderr.write("DEBUG INFO:\n")
        sys.stderr.write("order = " + str(self.__order) + "\n")
        sys.stderr.write("GF = " + str(self.__gf) + "\n")
        sys.stderr.write("LF = " + str(self.__lf) + "\n")
        sys.stderr.write("TF = " + str(self.__tf) + "\n")
        sys.stderr.write("dataStack = " + str(self.__dataStack.get_stack()) + "\n")
        sys.stderr.write("callStack = " + str(self.__callStack.get_stack()) + " (These are order numbers, to which instruction will interpret RETURN)" + "\n\n")

    """ STACK """
    def clears(self):
        argc = self.__instruction.argc()
        if argc != 0:
            self.print_error("Error, wrong arguments on CLEARS instruction!\n", 32)

        self.__dataStack = Stack()
    
    def arithmetics(self, op):
        argc = self.__instruction.argc()

        if argc != 0:
            self.print_error("Error, wrong arguments on" + op + " instruction!\n", 32)
        
        if self.__dataStack.size() < 2:
            self.print_error("Error, " + op + " not enough vars on stack!\n", 56)
        
        src2 = self.__dataStack.pop()
        src1 = self.__dataStack.pop()

        if type(src1) is not int or type(src2) is not int:
            self.print_error("Error, " + op + " not int types!\n", 53)
        
        try:
            if op == "ADDS":
                self.__dataStack.push(src1 + src2)
            elif op == "SUBS":
                self.__dataStack.push(src1 - src2)
            elif op == "MULS":
                self.__dataStack.push(src1 * src2)
            elif op == "IDIVS":
                self.__dataStack.push(src1 // src2)
        except ZeroDivisionError:
            self.print_error("Error, IDIVS division by zero!\n", 57)
        
    def compares(self, op):
        argc = self.__instruction.argc()

        if argc != 0:
            self.print_error("Error, wrong arguments on" + op + " instruction!\n", 32)
        
        if self.__dataStack.size() < 2:
            self.print_error("Error, " + op + " not enough vars on stack!\n", 56)
        
        src2 = self.__dataStack.pop()
        src1 = self.__dataStack.pop()

        if type(src1) is Nil and op != "EQS":
            self.print_error("Error, " + op + " wrong data type!\n", 53)
        elif type(src2) is Nil and op != "EQS":
            self.print_error("Error, " + op + " wrong data type!\n", 53)
        elif type(src1) != type(src2):
            self.print_error("Error, " + op + " not same data types!\n", 53)

        if op == "LTS":
            self.__dataStack.push((src1 < src2))
        elif op == "GTS":
            self.__dataStack.push((src1 > src2))
        elif op == "EQS":
            if type(src1) == Nil and type(src2) == Nil:
                self.__dataStack.push(True)
                return

            self.__dataStack.push((src1 == src2))

    def logicals(self, op):
        argc = self.__instruction.argc()
        if argc != 0:
            self.print_error("Error, wrong arguments on " + op + " instruction!\n", 32)
        
        if self.__dataStack.size() < 2 and op != "NOTS":
            self.print_error("Error, " + op + " not enough vars on stack!\n", 56)
        elif self.__dataStack.size() < 1:
            self.print_error("Error, " + op + " not enough vars on stack!\n", 56)
        
        src2 = self.__dataStack.pop()
        if op != "NOTS":
            src1 = self.__dataStack.pop()

        if type(src2) is not bool:
            self.print_error("Error, " + op + " not bool types!\n", 53)
        if op != "NOTS":
            if type(src1) is not bool:
                self.print_error("Error, " + op + " not bool types!\n", 53)
    
        if op == "ANDS":
            self.__dataStack.push(src1 and src2)
        elif op == "ORS":
            self.__dataStack.push(src1 or src2)
        elif op == "NOTS":
            self.__dataStack.push(not src2)

    def int2chars(self):
        argc = self.__instruction.argc()
        if argc != 0:
            self.print_error("Error, wrong arguments on INT2CHARS instruction!\n", 32)

        if self.__dataStack.size() < 1:
            self.print_error("Error, INT2CHARS not enough vars on stack!\n", 56)
        
        src1 = self.__dataStack.pop()

        if type(src1) is not int:
            self.print_error("Error, INT2CHARS not int!\n", 53)
        
        try:
            self.__dataStack.push(chr(src1))
        except:
            self.print_error("Error, INT2CHARS int is out of range!\n", 58)
    
    def stri2ints(self):
        argc = self.__instruction.argc()
        if argc != 0:
            self.print_error("Error, wrong arguments on STRI2INTS instruction!\n", 32)

        if self.__dataStack.size() < 2:
            self.print_error("Error, STRI2INTS not enough vars on stack!\n", 56)
        
        index = self.__dataStack.pop()
        src = self.__dataStack.pop()

        if type(src) is not str or type(index) is not int:
            self.print_error("Error, STRI2INTS wrong data types!\n", 53)
        
        if index >= len(src) or index < 0:
            self.print_error("Error, STRI2INTS index out of range!\n", 58)
        
        self.__dataStack.push(ord(src[index]))

    def jumpeqs(self, op):
        argc = self.__instruction.argc()
        if argc != 1:
            self.print_error("Error, wrong arguments on" + op + " instruction!\n", 32)
        
        if self.__dataStack.size() < 2:
            self.print_error("Error, " + op + " not enough vars on stack!\n", 56)
        
        label = self.parse_label(self.__instruction.arg1)
        self.check_if_label_exists(label, op)
        
        src2 = self.__dataStack.pop()
        src1 = self.__dataStack.pop()

        if type(src1) != type(src2):
            self.print_error("Error, " + op + " parameters are not the same data type!\n" , 53)
        
        if op == "JUMPIFEQS":
            if src1 == src2 or (type(src1) is Nil and type(src2) is Nil):
                self.__order = self.__labels[label]
        elif op == "JUMPIFNEQS":
            if src1 != src2 and (type(src2) is not Nil and type(src1) is not Nil):
                self.__order = self.__labels[label]

    def execute(self):
        self.get_instruction()
        while self.__instruction.opcode != "EOF":   

            if self.__instruction.opcode == "MOVE":
                self.move()
            elif self.__instruction.opcode == "CREATEFRAME":
                self.createframe()
            elif self.__instruction.opcode == "PUSHFRAME":
                self.pushframe()
            elif self.__instruction.opcode == "POPFRAME":
                self.popframe()
            elif self.__instruction.opcode == "DEFVAR":
                self.defvar()
            elif self.__instruction.opcode == "CALL":
                self.call()
            elif self.__instruction.opcode == "RETURN":
                self.return_()
            elif self.__instruction.opcode == "PUSHS":
                self.pushs()
            elif self.__instruction.opcode == "POPS":
                self.pops()
            elif self.__instruction.opcode == "ADD":
                self.arithmetic("ADD")
            elif self.__instruction.opcode == "SUB":
                self.arithmetic("SUB")
            elif self.__instruction.opcode == "MUL":
                self.arithmetic("MUL")
            elif self.__instruction.opcode == "IDIV":
                self.arithmetic("IDIV")
            elif self.__instruction.opcode == "LT":
                self.logical("LT")
            elif self.__instruction.opcode == "GT":
                self.logical("GT")
            elif self.__instruction.opcode == "EQ":
                self.logical("EQ")
            elif self.__instruction.opcode == "AND":
                self.logical("AND")
            elif self.__instruction.opcode == "OR":
                self.logical("OR")
            elif self.__instruction.opcode == "NOT":
                self.logical("NOT")
            elif self.__instruction.opcode == "INT2CHAR":
                self.int2char()
            elif self.__instruction.opcode == "STRI2INT":
                self.stri2int()
            elif self.__instruction.opcode == "READ":
                self.read()
            elif self.__instruction.opcode == "WRITE":
                self.write()
            elif self.__instruction.opcode == "CONCAT":
                self.concat()
            elif self.__instruction.opcode == "STRLEN":
                self.strlen()
            elif self.__instruction.opcode == "GETCHAR":
                self.getchar()
            elif self.__instruction.opcode == "SETCHAR":
                self.setchar()
            elif self.__instruction.opcode == "TYPE":
                self.type_()
            elif self.__instruction.opcode == "JUMP":
                self.jump()
            elif self.__instruction.opcode == "JUMPIFEQ":
                self.jumpeq("JUMPIFEQ")
            elif self.__instruction.opcode == "JUMPIFNEQ":
                self.jumpeq("JUMPIFNEQ")
            elif self.__instruction.opcode == "EXIT":
                self.exit_()
            elif self.__instruction.opcode == "DPRINT":
                self.dprint()
            elif self.__instruction.opcode == "BREAK":
                self.break_()
            elif self.__instruction.opcode == "CLEARS":
                self.clears()
            elif self.__instruction.opcode == "ADDS":
                self.arithmetics("ADDS")
            elif self.__instruction.opcode == "SUBS":
                self.arithmetics("SUBS")
            elif self.__instruction.opcode == "MULS":
                self.arithmetics("MULS")
            elif self.__instruction.opcode == "IDIVS":
                self.arithmetics("IDIVS")
            elif self.__instruction.opcode == "LTS":
                self.compares("LTS")
            elif self.__instruction.opcode == "GTS":
                self.compares("GTS")
            elif self.__instruction.opcode == "EQS":
                self.compares("EQS")
            elif self.__instruction.opcode == "ANDS":
                self.logicals("ANDS")
            elif self.__instruction.opcode == "ORS":
                self.logicals("ORS")
            elif self.__instruction.opcode == "NOTS":
                self.logicals("NOTS")
            elif self.__instruction.opcode == "INT2CHARS":
                self.int2chars()
            elif self.__instruction.opcode == "STRI2INTS":
                self.stri2ints()
            elif self.__instruction.opcode == "JUMPIFEQS":
                self.jumpeqs("JUMPIFEQS")
            elif self.__instruction.opcode == "JUMPIFNEQS":
                self.jumpeqs("JUMPIFNEQS")
            elif self.__instruction.opcode == "LABEL":
                self.get_instruction()
                continue
            elif self.__instruction.opcode == "EOF":
                break
            else:
                self.print_error("Error, unknown instruction!\n", 32)
            
            self.get_instruction()

        
interpret = Interpret()

interpret.parse_args()
interpret.set_up()
interpret.check_xml()
interpret.get_labels()
interpret.execute()