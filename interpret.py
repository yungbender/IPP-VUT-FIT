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
        instr.opcode = instr.opcode.upper()

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

        regex = re.compile(r"^TF@[a-zA-Z0-9_\-$&%*!?]+$|^LF@[a-zA-Z0-9_\-$&%*!?]+$|^GF@[a-zA-Z0-9_\-$&%*!?]+$")
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
        regex = re.compile(r"^int@[-+]?[0-9]+$|^bool@true$|^bool@false$|^string@.*")

        result = regex.search(symb)

        if result == None:
            self.print_error("Error, expecting <symb>!\n", 32)
        
        split = symb.split("@", 1)
        
        return split[0], split[1], "const"

    def parse_label(self, arg):
        if len(arg) != 2:
            self.print_error("Error, expecting <label>!\n", 32)

        return arg[1]

    def get_value(self, type_, src):
        if type_ == "int":
            value = int(src)
        elif type_ == "string":
            value = src
        elif type_ == "bool":
            if src == "true":
                value = True
            else:
                value = False
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
        
        self.execute()

    
    def createframe(self):
        self._tf = {}

        self.execute()

    def pushframe(self):
        if self._tf == None:
            self.print_error("Error, trying to push undefined TF!\n", 55)
        
        if self._lf != None:
            self.__frameStack.push(self.__lf)
        
        self._lf = self._tf
        self._tf = None

        self.execute()

    def popframe(self):
        if self._lf == None:
            self.print_error("Error, no frame to pop!\n", 55)
        
        self._tf = self._lf

        if not self.__frameStack.is_empty:
            self._lf = self.__frameStack.pop()
        else:
            self._lf = None

        self.execute()

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
        
        self.execute()
            

    def call(self):
        labName = self.parse_label(self.__instruction.arg1)

        if not labName in self.__labels:
            self.print_error("Error, CALL label does not exist!\n", 52)
        
        order = self.__labels[labName]

        self.__callStack.push(self.__order)
        self.__order = order

        self.execute()

    def return_(self):
        if self.__callStack.is_empty():
            self.print_error("Error, RETURN there is nowhere to return!\n", 56)
        
        self.__order = self.__callStack.pop()

        self.execute()

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

        self.execute()

    def pops(self):
        argc = self.__instruction.argc()

        if argc != 1:
            self.print_error("Error, wrong arguments on POPS instruction!\n", 32)

        if self.__dataStack.is_empty():
            self.print_error("Error, POPS data stack is empty!\n", 56)

        frame, dest = self.parse_var(self.__instruction.arg1)

        self.check_if_exists(frame, dest, "POPS")
        
        frame[dest] = self.__dataStack.pop()

        self.execute()

    def arithmetic(self, op):
        argc = self.__instruction.argc()

        if argc != 3:
            self.print_error("Error, wrong arguments on " + op + " instruction!\n", 32)

        frame, dest = self.parse_var(self.__instruction.arg1)

        self.check_if_exists(frame, dest, op)

        type_1, source1, whatIsIt1 = self.parse_symb(self.__instruction.arg2)
        if whatIsIt1 == "var":
            self.check_if_exists(type_1, source1, op)

        type_2, source2, whatIsIt2 = self.parse_symb(self.__instruction.arg3)
        if whatIsIt1 == "var":
            self.check_if_exists(type_2, source2, op)

        if whatIsIt1 == "const" and whatIsIt2 == "const":
            source1 = self.get_value(type_1, source1)
            source2 = self.get_value(type_2, source2)

            try:
                if op == "ADD":
                    frame[dest] = source1 + source2
                elif op == "SUB":
                    frame[dest] = source1 - source2
                elif op == "MUL":
                    frame[dest] = source1 * source2
                elif op == "IDIV":
                    frame[dest] = source1 // source2

            except ZeroDivisionError:
                self.print_error("Error, IDIV division by zero!\n", 57)
            except:
                self.print_error("Error, " + op + " incorrect data types!\n", 53)

        elif whatIsIt1 == "var" and whatIsIt2 == "var":

            try:
                if op == "ADD":
                    frame[dest] = type_1[source1] + type_2[source2]
                elif op == "SUB":
                    frame[dest] = type_1[source1] - type_2[source2]
                elif op == "MUL":
                    frame[dest] = type_1[source1] * type_2[source2]
                elif op == "IDIV":
                    frame[dest] = type_1[source1] // type_2[source2]

            except ZeroDivisionError:
                self.print_error("Error, IDIV division by zero!\n", 57)
            except:
                self.print_error("Error, " + op + " incorrect data types!\n", 53)

        elif whatIsIt1 == "var" and whatIsIt2 == "const":
            source2 = self.get_value(type_2, source2)
            try:
                if op == "ADD":
                    frame[dest] = type_1[source1] + source2
                elif op == "SUB":
                    frame[dest] = type_1[source1] - source2
                elif op == "MUL":
                    frame[dest] = type_1[source1] * source2
                elif op == "IDIV":
                    frame[dest] = type_1[source1] // source2

            except ZeroDivisionError:
                self.print_error("Error, IDIV division by zero!\n", 57)
            except:
                self.print_error("Error, " + op + " incorrect data types!\n", 53)

        else:
            source1 = self.get_value(type_1, source1)
            try:
                if op == "ADD":
                    frame[dest] = source1 + type_2[source2]
                elif op == "SUB":
                    frame[dest] = source1 - type_2[source2]
                elif op == "MUL":
                    frame[dest] = source1 * type_2[source2]
                elif op == "IDIV":
                    frame[dest] = source1 // type_2[source2]

            except ZeroDivisionError:
                self.print_error("Error, IDIV division by zero!\n", 57)
            except:
                self.print_error("Error, " + op + " incorrect data types!\n", 53)

        self.execute()

    def logical(self, op):
        argc = self.__instruction.argc()

        if argc != 3:
            self.print_error("Error, wrong arguments on " + op + " instruction!\n", 32)

        frame, dest = self.parse_var(self.__instruction.arg1)

        self.check_if_exists(frame, dest, op)

        type_1, source1, whatIsIt1 = self.parse_symb(self.__instruction.arg2)
        if whatIsIt1 == "var":
            self.check_if_exists(type_1, source1, op)

        type_2, source2, whatIsIt2 = self.parse_symb(self.__instruction.arg3)
        if whatIsIt1 == "var":
            self.check_if_exists(type_2, source2, op)

        if whatIsIt1 == "const" and whatIsIt2 == "const":
            source1 = self.get_value(type_1, source1)
            source2 = self.get_value(type_2, source2)

            try:
                if op == "LT":
                    frame[dest] = source1 < source2
                elif op == "GT":
                    frame[dest] = source1 > source2
                elif op == "EQ":
                    frame[dest] = source1 == source2
                elif op == "AND":
                    frame[dest] = source1 // source2

            except:
                self.print_error("Error, " + op + " incorrect data types!\n", 53)

        elif whatIsIt1 == "var" and whatIsIt2 == "var":

            try:
                if op == "LT":
                    frame[dest] = type_1[source1] < type_2[source2]
                elif op == "GT":
                    frame[dest] = type_1[source1] > type_2[source2]
                elif op == "EQ":
                    frame[dest] = type_1[source1] == type_2[source2]
                elif op == "IDIV":
                    frame[dest] = type_1[source1] // type_2[source2]

            except:
                self.print_error("Error, " + op + " incorrect data types!\n", 53)

        elif whatIsIt1 == "var" and whatIsIt2 == "const":
            source2 = self.get_value(type_2, source2)
            try:
                if op == "ADD":
                    frame[dest] = type_1[source1] < source2
                elif op == "SUB":
                    frame[dest] = type_1[source1] > source2
                elif op == "MUL":
                    frame[dest] = type_1[source1] == source2
                elif op == "IDIV":
                    frame[dest] = type_1[source1] // source2

            except:
                self.print_error("Error, " + op + " incorrect data types!\n", 53)

        else:
            source1 = self.get_value(type_1, source1)
            try:
                if op == "ADD":
                    frame[dest] = source1 < type_2[source2]
                elif op == "SUB":
                    frame[dest] = source1 > type_2[source2]
                elif op == "MUL":
                    frame[dest] = source1 == type_2[source2]
                elif op == "IDIV":
                    frame[dest] = source1 // type_2[source2]
            except:
                self.print_error("Error, " + op + " incorrect data types!\n", 53)

        self.execute()


    def dprint(self):
        argc = self.__instruction.argc()

        if argc != 1:
            self.print_error("Error, wrong arguments on DPRINT instruction!\n", 32)

        frame, src = self.parse_var(self.__instruction.arg1)

        self.check_if_exists(frame, src, "DPRINT")

        sys.stderr.write(frame[src])

        self.execute()

    def break_(self):
        sys.stderr.write("DEBUG INFO:\n")
        sys.stderr.write("order = " + str(self.__order) + "\n")
        sys.stderr.write("GF = " + str(self.__gf) + "\n")
        sys.stderr.write("LF = " + str(self.__lf) + "\n")
        sys.stderr.write("TF = " + str(self.__tf) + "\n")
        sys.stderr.write("dataStack = " + str(self.__dataStack.get_stack()) + "\n")
        sys.stderr.write("callStack = " + str(self.__callStack.get_stack()) + " (These are order numbers, to which instruction will interpret RETURN)" + "\n\n")
        
        self.execute()

    def execute(self):
        self.get_instruction()

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
            self.read()
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
            self.type()
        elif self.__instruction.opcode == "JUMP":
            self.jump()
        elif self.__instruction.opcode == "JUMPIFEQ":
            self.jumpifeq()
        elif self.__instruction.opcode == "JUMPIFNEQ":
            self.jumpifneq()
        elif self.__instruction.opcode == "EXIT":
            self.exit()
        elif self.__instruction.opcode == "DPRINT":
            self.dprint()
        elif self.__instruction.opcode == "BREAK":
            self.break_()
        elif self.__instruction.opcode == "LABEL":
            self.execute()
        elif self.__instruction.opcode == "EOF":
            return
        else:
            self.print_error("Error, unknown instruction!\n", 32)

        

interpret = Interpret()

interpret.parse_args()
interpret.set_up()
interpret.check_xml()
interpret.get_labels()
interpret.execute()
