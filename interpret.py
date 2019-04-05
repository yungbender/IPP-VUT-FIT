"""
    Interpret for Principles of Programming Languages
    Author: Tomáš Sasák
    2019
"""
import sys, re
import xml.etree.ElementTree as ET

class Stats:
    """
        Class represents statistics from interpretation
    """
    def __init__(self):
        """ Instructions counter """
        self.__insts = 0
        """ Variables counter """
        self.__vars = 0
        """ True if stats were requested """
        self.__statsRequested = False
        """ True if instructions stats were requested """
        self.__instsRequested = False
        """ True if variables stats were requested """
        self.__varsRequested = False
        """ Name of file where the statistics will be printed """
        self.__file = None
    
    def add_inst(self):
        self.__insts += 1
    
    def sub_inst(self):
        self.__insts -= 1

    def add_var(self):
        self.__vars += 1
    
    def sub_var(self):
        self.__vars -= 1
    
    def args_stats(self, args):
        """ Method parses arguments meant for statistics.
        Returns number of parsed arguments. """
        argc = 0

        stats_re = re.compile(r"^--stats=.*$")
        isStats = list(filter(stats_re.search, args))

        if isStats and len(isStats) == 1:
            argc += 1
            self.__statsRequested = True

            path = isStats[0].split("=", 1)
            self.__file = path[1]
        elif isStats:
            Interpret.print_error(None, "Error, wrong arguments!\n", 10)
        
        insts_re = re.compile(r"^--insts$")
        isInsts = list(filter(insts_re.search, args))

        if isInsts and len(isInsts) == 1 and self.__statsRequested == True:
            argc += 1
            self.__instsRequested = True
        elif isInsts and (len(isInsts) != 1 or self.__statsRequested != True):
            Interpret.print_error(None, "Error, wrong arguments!\n", 10)

        vars_re = re.compile(r"^--vars$")
        isVars = list(filter(vars_re.search, args))

        if isVars and len(isVars) == 1 and self.__statsRequested == True:
            argc += 1
            self.__varsRequested = True
        elif isVars and (len(isVars) != 1 or self.__statsRequested != True):
            Interpret.print_error(None, "Error, wrong arguments!\n", 10)
        
        if self.__statsRequested and (self.__instsRequested == False and self.__varsRequested == False):
            Interpret.print_error(None, "Error, wrong arguments!\n", 10)

        return argc

    def print_results(self):
        """ Method prints out the results of statistics to file 
            if they were requested """
        if self.__statsRequested == False:
            return

        try:
            self.__file = open(self.__file, "w")
        except:
            Interpret.print_error(None, "Error, cannot open stats file!\n", 12)
    
        for argument in sys.argv:
            if argument == "--insts":
                self.__file.write(str(self.__insts))
                self.__file.write("\n")
                    
            elif argument == "--vars":
                self.__file.write(str(self.__vars))
                self.__file.write("\n")

        self.__file.close()

class Nil:
    """ Class represents Nil datatype """
    def __init__(self):
        self._nil = "nil"

class Stack:
    """ Class represents ADT stack and operations with it """
    
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
    """ Class represnts 1 instruction from XML file and its arguments """
    def __init__(self):
        self.opcode = None
        self.arg1 = []
        self.arg2 = []
        self.arg3 = []
        self.order = 0

    def argc(self):
        """ Method counts the number of argument of 1 instruction """
        count = 0
        if self.arg1:
            count += 1
        if self.arg2:
            count += 1
        if self.arg3:
            count += 1
        
        return count

class Interpret:
    """ Class represents the Interpret, which preforms the instructions
    from the XML file. """
    
    def __init__(self):
        """ Frames """
        self.__gf = {}
        self.__tf = None
        self.__lf = None
        self.__frameStack = None

        """ Data stack """
        self.__dataStack = None

        """ Call stack, for CALL/RETURN instruction """
        self.__callStack = None

        """ Labels and their number of instruction (where they are) """
        self.__labels = {}

        """ I/O """
        self.__source = 0
        self.__input = "STDIN"

        """ Current number of performed instruction
            Like EIP register in CPU """
        self.__order = 0

        """ Current instruction performed """
        self.__instruction = None

        """ Number of instructions in whole XML file """
        self.__instrCount = 0

        """ Statistics object """
        self.__stats = None


    def print_error(self, message, number):
        """ Method prints out given error message and exits with given number. """
        print(message, file=sys.stderr, end="")
        sys.exit(number)

    def parse_args(self):
        """ Method parses arguments from user, and checks if arguments are written correctly. """
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
        
        self.__stats = Stats()
        argc += self.__stats.args_stats(sys.argv)

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
            
    """ Lexer """
    def get_instruction(self):
        """ Method gets next instruction from XML file 
            Method returns 1 parsed instruction object """
        instr = Instruction()

        """ EOF """
        if self.__order == self.__instrCount:
            instr.opcode = "EOF"
            self.__instruction = instr
            return

        part = self.__source[self.__order]
        instr.opcode = part.get("opcode")
        instr.opcode = instr.opcode.upper()

        instr.order = int(part.get("order"))

        """ Parse arguments """
        arg1 = part.find("arg1")
        if arg1 != None:
            if(len(part.findall("arg1")) != 1):
                self.print_error("Error, wrong arg1!\n", 32)
            instr.arg1.append(arg1.get("type"))
            instr.arg1.append(arg1.text)
            if instr.arg1[1] == None:
                instr.arg1[1] = ""
        
        arg2 = part.find("arg2")
        if arg2 != None:
            if(len(part.findall("arg2")) != 1):
                self.print_error("Error, wrong arg2!\n", 32)
            instr.arg2.append(arg2.get("type"))
            instr.arg2.append(arg2.text)
            if instr.arg2[1] == None:
                instr.arg2[1] = ""

        if len(instr.arg1) == 0 and len(instr.arg2) != 0:
            self.print_error("Error, wrong arguments of function!\n", 32)

        arg3 = part.find("arg3")
        if arg3 != None:
            if(len(part.findall("arg3")) != 1):
                self.print_error("Error, wrong arg3!\n", 32)
            instr.arg3.append(arg3.get("type"))
            instr.arg3.append(arg3.text)
            if instr.arg3[1] == None:
                instr.arg3[1] = ""

        if len(instr.arg2) == 0 and len(instr.arg3) != 0:
            self.print_error("Error, wrong arguments of function!\n", 32)
        
        self.__order += 1
        self.__instruction = instr

    def get_labels(self):
        """ Method checks the whole XML file and look up every LABEL instruction
            and loads the labels in dictionary. """
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
        """ Method checks up, if the <var> parameter in instruction is correct
            lexically, and checks if the variable exists, if exists, method
            returns the refference to the frame where the <var> is and variable
            name """
        if len(arg) != 2:
            self.print_error("Error, expecting <var>! Wrong structure!\n", 32)

        type_ = arg[0]

        if type_ != "var":
            self.print_error("Error, expecting <var>!\n", 32)

        var = arg[1]

        regex = re.compile(r"^TF@[a-zA-Z_\-$&%*!?]{1}[a-zA-Z0-9_\-$&%*!?]*$|^LF@[a-zA-Z_\-$&%*!?]{1}[a-zA-Z0-9_\-$&%*!?]*$|^GF@[a-zA-Z_\-$&%*!?]{1}[a-zA-Z0-9_\-$&%*!?]*$")
        result = regex.search(var)

        if result == None:
            self.print_error("Error, expencting <var>! Lexically wrong!\n", 32)

        split = var.split("@", 1)

        if split[0] == "LF":
            frame = self.__lf
        elif split[0] == "TF":
            frame = self.__tf
        elif split[0] == "GF":
            frame = self.__gf
        else:
            self.print_error("Error, <var> unknown frame!\n")

        return frame, split[1]

    def parse_symb(self, arg):
        """ Method checks up, if the <symb> parameter in instruction is correct
            lexically, and checks what is it (variable or constant). If variable
            instruction is sent into parse_var method. If constant, constant is parsed
            and returned back. 
            If variable, method returns, frame refference, its name
            and "var" string which signifies it is variable. 
            If constant, method returns datatype of constant, constant, "const" string
            which signifies it is constant """
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
        """ Method checks up, if the <label> parameter in instruction is correct
        lexically 
        Method returns name of the label. """
        if len(arg) != 2:
            self.print_error("Error, expecting <label>!\n", 32)
        
        label = arg[1]
        
        regex = re.compile(r"^[a-zA-Z_\-$&%*!?]{1}[a-zA-Z0-9_\-$&%*!?]*$")
        result = regex.search(label)

        if result == None:
            self.print_error("Error, expecting <label>!\n", 32)
        
        return label

    def parse_type(self, arg):
        """ Method checks up, if the <type> parameter in instruction is correct
        leixcally
        Method returns name of the datatype """
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
        """ Method translates the constant value, from string taken from XML file
        to actual python datatype 
        Method returns translated datatype """
        if type_ == "int":
            try:
                value = int(src)
            except:
                self.print_error("Error, constant has wrong data type!\n", 53)
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
                self.print_error("Error, constant has wrong data type!\n", 53)
        elif type_ == "nil":
            value = Nil()
        else:
            self.print_error("Error, wrong type attribute!\n", 32)
        
        return value

    def check_if_exists(self, frame, var, op, checkIfNone):
        """ Method checks up, if the the given "var" variable, exists in the
        given "frame" refference. "op" signifies current performed instruction
        for easy error reporting. "checkIfNone" flag signifies the method, to check
        if the given variable is unitialized (no interpreter data type). """
        if frame == None:
            self.print_error("Error, " + op + " destination variable frame is not initiliazed!\n", 55)
        elif not var in frame:
            self.print_error("Error, " + op + " destination variable does not exist!\n", 54)
        elif checkIfNone:
            if frame[var] is None:
                self.print_error("Error, " + op + " variable is not initalized!\n", 56)

    def check_if_label_exists(self, label, op):
        """ Method checks if the given "label" name is existing in label dictionary """
        if label not in self.__labels:
            self.print_error("Error, " + op + " label does not exist!\n", 52)

    def move(self):
        """ Method emulates the "MOVE" insturction from IPPcode19 """
        argc = self.__instruction.argc()
        if argc != 2:
            self.print_error("Error, wrong arguments on MOVE instructions!\n", 32)

        frame, dest = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dest, "MOVE", False)

        type_, src, whatIsIt = self.parse_symb(self.__instruction.arg2)

        if whatIsIt == "var":
            self.check_if_exists(type_, src, "MOVE", True)
            src = type_[src]

        elif whatIsIt == "const":
            src = self.get_value(type_, src)
        
        frame[dest] = src
        
    def createframe(self):
        """ Method emulates the "CREATEFRAME" instruction from IPPcode19 """
        argc = self.__instruction.argc()
        if argc != 0:
            self.print_error("Error, wrong arguments on CREATEFRAME instructions!\n", 32)

        self.__tf = {}

    def pushframe(self):
        """ Method emulates the "PUSHFRAME" instruction from IPPcode19 """
        argc = self.__instruction.argc()
        if argc != 0:
            self.print_error("Error, wrong arguments on PUSHFRAME instructions!\n", 32)

        if self.__tf == None:
            self.print_error("Error, trying to push undefined TF!\n", 55)
        
        if self.__lf != None:
            self.__frameStack.push(self.__lf)
        
        self.__lf = self.__tf
        self.__tf = None

    def popframe(self):
        """ Method emulates the "POPFRAME" instruction from IPPcode19 """
        argc = self.__instruction.argc()
        if argc != 0:
            self.print_error("Error, wrong arguments on POPFRAME instructions!\n", 32)

        if self.__lf == None:
            self.print_error("Error, no frame to pop!\n", 55)
        
        self.__tf = self.__lf

        if not self.__frameStack.is_empty():
            self.__lf = self.__frameStack.pop()
        else:
            self.__lf = None

    def defvar(self):
        """ Method emulates the "DEFVAR" instruction from IPPcode19 """
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
        """ Method emulates the "CALL" instruction from IPPcode19 """
        argc = self.__instruction.argc()
        if argc != 1:
            self.print_error("Error, wrong arguments on CALL instruction!\n", 32)

        labName = self.parse_label(self.__instruction.arg1)
        
        if not labName in self.__labels:
            self.print_error("Error, CALL label does not exist!\n", 52)

        """ Push the number of order, where to return """
        self.__callStack.push(self.__order)
        """ Change the value of current performed instruction (EIP register) """
        self.__order = self.__labels[labName]

    def return_(self):
        """ Method emulates the "RETURN" instruction from IPPcode19 """
        argc = self.__instruction.argc()
        if argc != 0:
            self.print_error("Error, wrong arguments on RETURN instruction!\n", 32)

        if self.__callStack.is_empty():
            self.print_error("Error, RETURN there is nowhere to return!\n", 56)
        
        """ Restore order (EIP) """
        self.__order = self.__callStack.pop()

    def pushs(self):
        """ Method emulates the "PUSHS" instruction from IPPcode19 """
        argc = self.__instruction.argc()
        if argc != 1:
            self.print_error("Error, wrong arguments on PUSHS instruction!\n", 32)
        
        type_, src, whatIsIt = self.parse_symb(self.__instruction.arg1)

        if whatIsIt == "var":
            self.check_if_exists(type_, src, "PUSHS", True)

            self.__dataStack.push(type_[src])

        elif whatIsIt == "const":
            value = self.get_value(type_, src)

            self.__dataStack.push(value)

    def pops(self):
        """ Method emulates the "POPS" instruction from IPPcode19 """
        argc = self.__instruction.argc()
        if argc != 1:
            self.print_error("Error, wrong arguments on POPS instruction!\n", 32)

        if self.__dataStack.is_empty():
            self.print_error("Error, POPS data stack is empty!\n", 56)

        frame, dest = self.parse_var(self.__instruction.arg1)

        self.check_if_exists(frame, dest, "POPS", False)
        
        frame[dest] = self.__dataStack.pop()

    def arithmetic(self, op):
        """ Method emulates the arithmetic instructions (ADD, SUB, MUL, IDIV) from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 3:
            self.print_error("Error, wrong arguments on " + op + " instruction!\n", 32)

        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, op, False)

        type_1, src1, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_1, src1, op, True)
            src1 = type_1[src1]
        else:
            src1 = self.get_value(type_1, src1)

        type_2, src2, whatIsIt = self.parse_symb(self.__instruction.arg3)
        if whatIsIt == "var":
            self.check_if_exists(type_2, src2, op, True)
            src2 = type_2[src2]
        else:
            src2 = self.get_value(type_2, src2)

        if type(src1) is not int or type(src2) is not int:
            self.print_error("Error, " + op + " incorrect data types!\n", 53)

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

    def compare(self, op):
        """ Method emulates the comparision instructions (EQ, LT, GT) from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 3:
            self.print_error("Error, wrong arguments on " + op + " instruction!\n", 32)
                
        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, op, False)

        type_1, src1, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_1, src1, op, True)
            src1 = type_1[src1]
        else:
            src1 = self.get_value(type_1, src1)

        type_2, src2, whatIsIt = self.parse_symb(self.__instruction.arg3)
        if whatIsIt == "var":
            self.check_if_exists(type_2, src2, op, True)
            src2 = type_2[src2]
        else:
            src2 = self.get_value(type_2, src2)
        
        if type(src1) is Nil and type(src2) is not Nil and op == "EQ":
            frame[dst] = False
            return
        elif type(src2) is Nil and type(src1) is not Nil and op == "EQ":
            frame[dst] = False
            return
        if type(src1) != type(src2):
            self.print_error("Error, " + op + " incorrect data types!\n", 53)

        if op == "LT":
            frame[dst] = (src1 < src2)
        elif op == "GT":
            frame[dst] = (src1 > src2)
        elif op == "EQ":
            if type(src1) is Nil and type(src2) is Nil:
                frame[dst] = True
                return

            frame[dst] = (src1 == src2)

    def logical(self, op):
        """ Method emulates the logical instructions (NOT, AND, OR) from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 3 and op != "NOT":
            self.print_error("Error, wrong arguments on " + op + " instruction!\n", 32)
        elif argc != 2 and op == "NOT":
            self.print_error("Error, wrong arguments on " + op + " instruction!\n", 32)

        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, op, False)

        type_1, src1, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_1, src1, op, True)
            src1 = type_1[src1]
        else:
            src1 = self.get_value(type_1, src1)

        if type(src1) is not bool:
            self.print_error("Error, " + op + "operand is not bool!\n", 53)
        
        if op != "NOT":
            type_2, src2, whatIsIt = self.parse_symb(self.__instruction.arg3)
            if whatIsIt == "var":
                self.check_if_exists(type_2, src2, op, True)
                src2 = type_2[src2]
            else:
                src2 = self.get_value(type_2, src2)

            if type(src2) is not bool:
                self.print_error("Error, " + op + "operand is not bool!\n", 53)
        
        if op == "AND":
            frame[dst] = (src1 and src2)
        elif op == "OR":
            frame[dst] = (src1 or src2)
        elif op == "NOT":
            frame[dst] = (not src1)

    def int2char(self):
        """ Method emulates the "INT2CHAR" instruction from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 2:
            self.print_error("Error, wrong arguments on INT2CHAR instruction!\n", 32)
        
        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, "INT2CHAR", False)

        type_, src, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_, src, "INT2CHAR", True)
            src = type_[src]
        else:
            src = self.get_value(type_, src)
    
        if type(src) is not int:
            self.print_error("Error, INT2CHAR source value is not int!", 53)

        try:
            frame[dst] = chr(src)
        except:
            self.print_error("Error, INT2CHAR wrong value to change char to!\n.", 58)

    def stri2int(self):
        """ Method emulates the "STRI2INT" instruction from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 3:
            self.print_error("Error, wrong arguments on STRI2INT instruction!\n", 32)

        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, "STRI2INT", False)

        type_1, src1, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_1, src1, "STRI2INT", True)
            src1 = type_1[src1]
        else:
            src1 = self.get_value(type_1, src1)

        if type(src1) is not str:
            self.print_error("Error, STRI2INT <symb1> is not string!\n", 53)

        type_2, index, whatIsIt = self.parse_symb(self.__instruction.arg3)
        if whatIsIt == "var":
            self.check_if_exists(type_2, index, "STRI2INT", True)
            index = type_2[index]
        else:
            index = self.get_value(type_2, index)

        if type(index) is not int:
            self.print_error("Error, STRI2INT <symb2> is not int(index)!\n", 53)

        if index >= len(src1) or index < 0:
            self.print_error("Error, STRI2INT index is out of range!\n", 58)

        frame[dst] = ord(src1[index]) 

    def read(self):
        """ Method emulates the "READ" instruction from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 2:
            self.print_error("Error, wrong arguments on READ instruction!\n", 32)

        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, "READ", False)

        dataType = self.parse_type(self.__instruction.arg2)

        if self.__input == "STDIN":
            value = input()
        else:
            value = self.__input.readline()
            if value.endswith("\n"):
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
            value = value.upper()
            if value == "TRUE":
                value = True
            else:
                value = False
        
        frame[dst] = value
    
    def format_string(self, string):
        """ Method checks the escape sequences, and translates them """
        return re.sub(r"\\(\d\d\d)", lambda x: chr(int(x.group(1), 10)), string)

    def write(self):
        """ Method emulates the "WRITE" instruction from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 1:
            self.print_error("Error, wrong arguments on WRITE instruction!\n", 32)

        type_1, src, whatIsIt = self.parse_symb(self.__instruction.arg1)
        if whatIsIt == "var":
            self.check_if_exists(type_1, src, "WRITE", True)
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
        if type(src) is Nil:
            src = ""
        
        print(str(src), end="")

    def concat(self):
        """ Method emulates the "CONCAT" instruction from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 3:
            self.print_error("Error, wrong arguments on CONCAT instruction!\n", 32)
        
        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, "CONCAT", False)

        type_1, src1, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_1, src1, "CONCAT", True)
            src1 = type_1[src1]
        else:
            src1 = self.get_value(type_1, src1)
        
        type_2, src2, whatIsIt = self.parse_symb(self.__instruction.arg3)
        if whatIsIt == "var":
            self.check_if_exists(type_2, src2, "CONCAT", True)
            src2 = type_2[src2]
        else:
            src2 = self.get_value(type_2, src2)

        if type(src1) is not str or type(src2) is not str:
            self.print_error("Error, CONCAT not concatinating strings!\n", 53)
        
        frame[dst] = src1 + src2

    def strlen(self):
        """ Method emulates the "STRLEN" instruction from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 2:
            self.print_error("Error, wrong arguments on STRLEN instruction!\n", 32)
        
        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, "STRLEN", False)

        type_1, src1, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_1, src1, "STRLEN", True)
            src1 = type_1[src1]
        else:
            src1 = self.get_value(type_1, src1)
        
        if type(src1) is not str:
            self.print_error("Error, STRLEN must be string!\n", 53)
        
        frame[dst] = len(src1)

    def getchar(self):
        """ Method emulates the "GETCHAR" instruction from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 3:
            self.print_error("Error, wrong arguments on GETCHAR instruction!\n", 32)

        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, "GETCHAR", False)

        type_1, src1, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_1, src1, "GETCHAR", True)
            src1 = type_1[src1]
        else:
            src1 = self.get_value(type_1, src1)

        if type(src1) is not str:
            self.print_error("Error, GETCHAR <symb1> is not string!\n", 53)

        type_2, index, whatIsIt = self.parse_symb(self.__instruction.arg3)
        if whatIsIt == "var":
            self.check_if_exists(type_2, index, "GETCHAR", True)
            index = type_2[index]
        else:
            index = self.get_value(type_2, index)

        if type(index) is not int:
            self.print_error("Error, GETCHAR <symb2> is not int(index)!\n", 53)

        if index >= len(src1) or index < 0:
            self.print_error("Error, GETCHAR index is out of range!\n", 58)

        frame[dst] = src1[index]

    def setchar(self):
        """ Method emulates the "SETCHAR" instruction from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 3:
            self.print_error("Error, wrong arguments on SETCHAR instruction!\n", 32)

        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, "SETCHAR", True)

        if type(frame[dst]) is not str:
            self.print_error("Error, SETCHAR <var> is not string!\n", 53)

        type_1, index, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_1, index, "SETCHAR", True)
            index = type_1[index]
        else:
            index = self.get_value(type_1, index)

        if type(index) is not int:
            self.print_error("Error, SETCHAR <symb1> is not int!\n", 53)

        type_2, src, whatIsIt = self.parse_symb(self.__instruction.arg3)
        if whatIsIt == "var":
            self.check_if_exists(type_2, src, "SETCHAR", True)
            src = type_2[src]
        else:
            src = self.get_value(type_2, src)

        if type(src) is not str:
            self.print_error("Error, SETCHAR <symb2> is not string!\n", 53)

        if index >= len(frame[dst]) or index < 0 or src == "":
            self.print_error("Error, SETCHAR index is out of range!\n", 58)
        
        string = list(frame[dst])
        string[index] = src[0]
        string = "".join(string)
        frame[dst] = string

    def type_(self):
        """ Method emulates the "TYPE" instruction from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 2:
            self.print_error("Error, wrong arguments on TYPE instruction!\n", 32)

        frame, dst = self.parse_var(self.__instruction.arg1)
        self.check_if_exists(frame, dst, "TYPE", False)

        type_, src, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_, src, "TYPE", False)
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
        elif src == "" or src is None:
            frame[dst] = ""
        else:
            self.print_error("Error, TYPE error.", 53)

    def jump(self):
        """ Method emulates the "JUMP" instruction from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 1:
            self.print_error("Error, wrong arguments on JUMP instruction!\n", 32)

        label = self.parse_label(self.__instruction.arg1)
        if label not in self.__labels:
            self.print_error("Error, label does not exist!\n", 52)

        self.__order = self.__labels[label]

    def jumpeq(self, type_):
        """ Method emulates the "JUMPIFEQ/JUMPIFNEQ" instruction from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 3:
            self.print_error("Error, wrong arguments on JUMPIFEQ or JUMPIFNEQ instruction!\n", 32)

        label = self.parse_label(self.__instruction.arg1)
        self.check_if_label_exists(label, type_)

        type_1, src1, whatIsIt = self.parse_symb(self.__instruction.arg2)
        if whatIsIt == "var":
            self.check_if_exists(type_1, src1, "JUMPIFEQ", True)
            src1 = type_1[src1]
        else:
            src1 = self.get_value(type_1, src1)
        
        type_2, src2, whatIsIt = self.parse_symb(self.__instruction.arg3)
        if whatIsIt == "var":
            self.check_if_exists(type_2, src2, "JUMPIFEQ", True)
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
        """ Method emulates the "EXIT" instruction from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 1:
            self.print_error("Error, wrong arguments on EXIT instruction!\n", 32)
        
        type_, src, whatIsIt = self.parse_symb(self.__instruction.arg1)

        if whatIsIt == "var":
            self.check_if_exists(type_, src, "EXIT", True)
            source = type_[src]
        
        else:
            source = self.get_value(type_, src)

        if type(source) is not int:
            self.print_error("Error, EXIT wrong data type!\n", 53)
        elif not source >= 0 or not source <= 49:
            self.print_error("Error, EXIT wrong exit number!\n", 57)
        
        self.__stats.print_results()
        sys.exit(source)

    def dprint(self):
        """ Method emulates the "DPRINT" instruction from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 1:
            self.print_error("Error, wrong arguments on DPRINT instruction!\n", 32)

        frame, src = self.parse_var(self.__instruction.arg1)

        self.check_if_exists(frame, src, "DPRINT", False)

        print(str(frame[src]), file=sys.stderr)

    def break_(self):
        """ Method emulates the "BREAK" instruction from IPPcode19 """
        argc = self.__instruction.argc()
        if argc != 0:
            self.print_error("Error, wrong arguments on BREAK instruction!\n", 32)

        print("DEBUG INFO:", file=sys.stderr)
        print("order = " + str(self.__order), file=sys.stderr)
        print("GF = " + str(self.__gf), file=sys.stderr)
        print("LF = " + str(self.__lf), file=sys.stderr)
        print("TF = " + str(self.__tf), file=sys.stderr)
        print("dataStack = " + str(self.__dataStack.get_stack()), file=sys.stderr)
        print("callStack = " + str(self.__callStack.get_stack()) + " (These are order numbers, to which instruction will interpret RETURN)", file=sys.stderr)
        print("frameStack = " + str(self.__frameStack.get_stack()), file=sys.stderr)

    """ STACK instructions (STACKI) """
    def clears(self):
        """ Method emulates the "CLEARS" instruction from IPPcode19 """
        argc = self.__instruction.argc()
        if argc != 0:
            self.print_error("Error, wrong arguments on CLEARS instruction!\n", 32)

        self.__dataStack = Stack()
    
    def arithmetics(self, op):
        """ Method emulates the arithmethic stack instructions (ADDS, SUBS, MULS, IDIVS) from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 0:
            self.print_error("Error, wrong arguments on " + op + " instruction!\n", 32)
        
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
        """ Method emulates the comparsion stack instructions (EQS, LTS, GTS) from IPPcode19 """
        argc = self.__instruction.argc()

        if argc != 0:
            self.print_error("Error, wrong arguments on" + op + " instruction!\n", 32)
        
        if self.__dataStack.size() < 2:
            self.print_error("Error, " + op + " not enough vars on stack!\n", 56)
        
        src2 = self.__dataStack.pop()
        src1 = self.__dataStack.pop()

        if type(src1) is Nil and op == "EQS" and type(src2) is not Nil:
            self.__dataStack.push(False)
            return
        elif type(src2) is Nil and op == "EQS" and type(src1) is not Nil:
            self.__dataStack.push(False)
            return

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
        """ Method emulates the logical instructions (ANDS, ORS, NOTS) from IPPcode19 """
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
        """ Method emulates the "INT2CHARS" instruction from IPPcode19 """
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
        """ Method emulates the "STRI2INTS" instruction from IPPcode19 """
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
        """ Method emulates the "JUMPIFEQS/JUMPIFNEQS" instruction from IPPcode19 """
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
        """ Method launches the instruction execution based on the current loaded instruction
            Instructions are executed until lexer hits EOF """
        self.get_instruction()
        while self.__instruction.opcode != "EOF":

            self.__stats.add_inst()

            if self.__instruction.opcode == "MOVE":
                self.move()
            elif self.__instruction.opcode == "CREATEFRAME":
                self.createframe()
            elif self.__instruction.opcode == "PUSHFRAME":
                self.pushframe()
            elif self.__instruction.opcode == "POPFRAME":
                self.popframe()
            elif self.__instruction.opcode == "DEFVAR":
                self.__stats.add_var()
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
                self.compare("LT")
            elif self.__instruction.opcode == "GT":
                self.compare("GT")
            elif self.__instruction.opcode == "EQ":
                self.compare("EQ")
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
                self.__stats.sub_inst()
                break
            else:
                self.print_error("Error, unknown instruction!\n", 32)
            
            self.get_instruction()
    
    """ Method calls the stats method to print out the results of interpretation """
    def print_stats(self):
        self.__stats.print_results()

        
interpret = Interpret()

interpret.parse_args()
interpret.set_up()
interpret.check_xml()
interpret.get_labels()
interpret.execute()
interpret.print_stats()