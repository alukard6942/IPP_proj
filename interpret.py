#!/usr/bin/env python3

# File:     interpret.py
# Author:   Chudárek Aleš (xchuda04)
# Date:     7.4.2020
# Desc:     Interpret jazyka ippcode20
#


# Libraries
import sys
import re
import logging
import xml.etree.ElementTree as ET

#-- Main function --
def main():

    argumentCount = len(sys.argv)
    xmlPath = sys.stdin
    inPath = "/dev/stdin"

    if argumentCount != 2 and argumentCount != 3:
        Error.print(10, "Invalid number of arguments. Try --help.")    #zero or more than one argument

    #-- Print argument "--help" --
    if sys.argv[1] == "--help" or (argumentCount == 3 and sys.argv[2] == "--help"):
        print("This script is used as an interpret of XML representation of code writtent in OPPcode21.")
        sys.exit(0)

    if argumentCount == 2:
        if sys.argv[1][:9] == "--source=":
            xmlPath = sys.argv[1][9:]
        elif sys.argv[1][:8] == "--input=":
            inPath = sys.argv[1][8:]
        else:
            Error.print(10, f"Invalid argument.: {sys.argv[1]} Try --help.")    #argument isn't --help --source=<file> or --input=<file>

    elif argumentCount == 3:
        if sys.argv[1][:9] == "--source=" and sys.argv[2][:8] == "--input=":
            xmlPath = sys.argv[1][9:]
            inPath = sys.argv[2][8:]
        elif sys.argv[2][:9] == "--source=" and sys.argv[1][:8] == "--input=":
            xmlPath = sys.argv[2][9:]
            inPath = sys.argv[1][8:]
        else:
            Error.print(10, "Invalid argument. Try --help.")    #argument isn't --help --source=<file> or --input=<file>

    #-- set global input file ---
    global InputFile

    InputFile = open(inPath, "r")



    #-- Open source file --
    try:
        elementTree = ET.ElementTree(file=xmlPath)
    except IOError:
        Error.print(11, "Can not open input file.")    #can't open the file
    except ET.ParseError:
        Error.print(31, "Elements are either missing or misspelled.")    #empty file or wrong arguments

    rootNode = elementTree.getroot()
    Interpret.checkRoot(rootNode)
    Interpret.loadInstructions(rootNode)

    #-- End --
    sys.exit(0)


#-- Classes --
class Error:
    """Error hendler, prints message and ends the program"""
    @staticmethod
    def print(code, message):
        print("ERROR: {0}".format(message), file=sys.stderr)
        print(f"{Interpret.instOrder}", file=sys.stderr)
        exit(code)


class Frames:
    """Frames for storing values"""
    gf = {}
    lf = None
    tf = None

    stack = []    #used for POPFRAME and PUSHFRAME


    @classmethod
    def add(cls, name):
        """Adds a new variable into frame"""

        frame = cls.selFrame(name)
        name = name[3:]    #removes prefix GF@ LF@ TF@
        if name in frame:
            Error.print(52, f"Variable {name} is already in the frame {frame}")
        frame[name] = None

    @classmethod
    def set(cls, name, value):
        """Gives value to a variable in frame"""

        frame = cls.selFrame(name)
        name = name[3:]    #removes prefix GF@ LF@ TF@
        if name not in frame:
            Error.print(54, "Value can't be assigned to a not existing variable")    #variable doesn't exist (frame does)

        #-- if variable -> get value --
        if type(value) == var:
            value = value.getValue()
        frame[name] = value


    @classmethod
    def get(cls, name):
        """Gets a value of a variable in frame"""

        frame = cls.selFrame(name)
        name = name[3:]    #removes prefix GF@ LF@ TF@
        if name not in frame:
            Error.print(54, "Value can't be read from a not existing variable")    #variable doesn't exist (frame does)

        result = frame[name]
        #-- Is it initialized --
        if type(result) == type(None):
            Error.print(56, f"Variable: {name} is not yet initialized {cls.tf}")    #value is missing

        return result;


    @classmethod
    def selFrame(cls, name):
        """Selects which frame should be used"""

        if name[:3] == "GF@":
            frame = cls.gf
        elif name[:3] == "LF@":
            frame = cls.lf
        elif name[:3] == "TF@":
            frame = cls.tf
        else:
            Error.print(32, "Invalid frame syntax")    #syntax error
        if frame == None:
            Error.print(55,"Frame is not inicialized yet")    #non existing frame
        return frame
    
    def __str__(self):
        return f"{self.gf}\n{self.lf}\n{self.tf}"

class Stack:
    """Class for stack"""

    def __init__(self):
        self.content = []


    def pop(self):
        if len(self.content) == 0:
            Error.print(56, "Stack is empty")

        value =self.content.pop() 
        return value


    def push(self, value):
        self.content.append(value)


class Labels:
    """Saves all labels"""

    labels = {}

    @classmethod
    def add(cls, name):
        """Ads new label"""

        name = str(name)
        if name in cls.labels:
            Error.print(52, "Label already exists")    #semantic error
        cls.labels[name] = Interpret.instOrder


    @classmethod
    def jump(cls, name):
        """Jumps on an according label"""

        name = str(name)
        if name not in cls.labels:
            Error.print(52, "Label doesn't exist")    #semantic error
        Interpret.instOrder = cls.labels[name]


class var:
    """Class for a variable"""

    def __init__(self, name):
        self.name = name


    def getValue(self):
        """Returns the value of a variable"""
        return Frames.get(self.getName())


    def getName(self):
        """Returns the name of a variable"""
        return self.name


    def setValue(self, value):
        """sets the name of a variable"""
        Frames.set(self.getName(), value)


    def __getValueWithType(self, expectedType):
        """Returns the value of a variable, if it has the correct type"""
        value = self.getValue()
        if type(value) != expectedType:
            Error.print(53, "Variable is storing an unexpected type")    #wrong operand type
        return value


    def __str__(self):
        """Get str value"""
        return self.__getValueWithType(str)


    def __int__(self):
        """Get int value"""
        return self.__getValueWithType(int)


    def __bool__(self):
        """Get bool value"""
        return self.__getValueWithType(bool)


class symb:
    """Dummy class"""
    pass

class label:
    """Class for a label"""

    def __init__(self, name):
        self.name = name


    def __str__(self):
        return self.name


class Interpret():
    """Interpret it self. The skeleton of this program"""

    instOrder = 1    #The order of active instruction
    prevInstOrder = 0
    valStack = Stack()    #For POPS and PUSHS
    callStack = Stack()    #For CALL and RETURN

    @staticmethod
    def checkRoot(root):
        """Checks if root node is valid"""
        if root.tag != "program":
            Error.print(32, "Root node <program> not found")

        if "language" in root.attrib:
            if root.attrib["language"].lower() != "ippcode21":
                Error.print(32, "Wrong lenguage")
            del root.attrib["language"]
        else:
            Error.print(31, "Language attribute missing")

        #-- If name or discription exists, del --
        if "name" in root.attrib:
            del root.attrib["name"]
        if "description" in root.attrib:
            del root.attrib["description"]

        if len(root.attrib) != 0:
            Error.print(31, "Invalid <program> attributes")


    @classmethod
    def loadInstructions(cls, root):
        """Executes all instructions"""

        #-- Search for all nodes --
        instrNodes = root.findall("*")

        toExe = {}

        """First find all labels"""
        for node in instrNodes:
            if node.tag != "instruction":
                Error.print(32, "Instruction is misspelled.")
            if not "opcode" in node.attrib:
                Error.print(32, "Missing opcode")
            if not "order" in node.attrib:
                Error.print(32, "Missing order")
            elif not node.attrib["order"].isdigit():
                Error.print(32, "Atribute order isn't a digit")

            order = int(node.attrib["order"])
            cls.instOrder = order

            if order in toExe:
                Error.print(32, "order repeats itself")

            toExe[order] = Instruction(node)

            if node.attrib["opcode"].upper() == "LABEL":
                toExe[order].LABEL()


        cls.instOrder = 1    # Reset instruction counter
        # get max order
        maxorder = 0
        for elem in toExe:
            if elem > maxorder: maxorder = elem

        node = None
        #-- go threw all instructions from the beginning --
        while cls.instOrder <= maxorder:

            if cls.instOrder not in toExe:
                cls.instOrder+=1
                continue

            node = toExe[cls.instOrder]

            #print(node)

            node.execute()

            cls.instOrder+=1

    @staticmethod
    def convertValue(xmlType, xmlValue, retDefault):
        """Converts and checks, if a value is correct and is returned in the correct type"""
        """If the value is not correct and the program should end, retDefault is False, otherwise it returns the default value"""


        if xmlType == "var":
            if re.search(r"^(LF|TF|GF)@[A-ZÁ-Ža-zá-ž\_\-\$\&\%\*\!\?][A-ZÁ-Ža-zá-ž0-9\_\-\$\&\%\*\!\?]*$", xmlValue):
                return var(xmlValue)
            Error.print(32, "Name of variable is misspelled.")    #syntax error

        elif xmlType == "int":
            if re.search(r"^[+-]?(0|[1-9][0-9]*)$", xmlValue):
                return int(xmlValue)    # Convert str to int
            else:
                Error.print(32, "Invalid int value")    #syntax error
            if retDefault:
                return 0
            Error.print(32, "Invalid int value")    #syntax error

        elif xmlType == "string":
            if xmlValue == None:
                xmlValue = ""
            if re.search(r"^([^\\#\s]|\\[0-9]{3})*$", xmlValue):
                for seq in list(re.findall(r"[0-9]{3}", xmlValue)):
                    if seq == "092":
                        xmlValue = re.sub("\\\\092", "\\\\", xmlValue)
                    else:
                        xmlValue = re.sub("\\\\{0}".format(seq), chr(int(seq)), xmlValue)
                return xmlValue
            else:
                Error.print(32, "Invalid string value")    #syntax error
            if retDefault:
                return ""
            Error.print(32, "Illegal characters in string")    #syntax error

        elif xmlType == "bool":
            if xmlValue == "true":
                return True
            if xmlValue == "false":
                return False
            if retDefault:
                return False
            Error.print(32, "Invalid boolean value. Use \"True\" or \"False\".")    #syntax error

        elif xmlType == "nil":
            if xmlValue == "nil":
                return ""
            else:
                Error.print(32, "Invalid nil value.")    #syntax error


        #-- Type type --
        if xmlType == "type":
            if re.search(r"^(int|string|bool|nil)$", xmlValue):
                return xmlValue
            Error.print(32, "Invalid type value")    #syntax error

        #-- Type label --
        if xmlType == "label":
            if not re.search(r"^[A-ZÁ-Ža-zá-ž\_\-\$\&\%\*\!\?][A-ZÁ-Ža-zá-ž0-9\_\-\$\&\%\*\!\?]*$", xmlValue):
                Error.print(32, "Invalid label name")    #syntax error
            return label(xmlValue)

        #-- Invalid type --
        else:
            Error.print(32, "Unknown type of argument")    #syntax error



class Instruction():
    """Represents a instruction"""

    def __init__(self, node):

        if node.tag != "instruction":
            Error.print(31, "Expected instruction")        #structure error

        #-- Check order --
        if int(node.attrib["order"]) == Interpret.instOrder:
            self.opcode = node.attrib["opcode"].upper()
            self.args = []
            argNum = 1
            for arg in node:
                if arg.tag[:3] == "arg" and int(arg.tag[3:]) == argNum:
                    self.args.append(Interpret.convertValue(arg.attrib["type"], arg.text, True))
                else:
                    Error.print(32, "Arguments are in a wrong order or duplicated.")    #structure error
                argNum += 1
            self.argCount = len(self.args)
        else:
            Error.print(32, "Wrong instruction order")    #structure error


    def __checkArguments(self, *expectedArgs):
        """Checks if arguments have expected type"""

        if self.argCount != len(expectedArgs):
            Error.print(52, "Unexpected ammount of arguments")    #semantic error

        expectedArgs = list(expectedArgs)
        i = 0;
        for arg in self.args: # Check every argument
            #-- symb represents int, bool, str or var --
            if expectedArgs[i] == symb:
                expectedArgs[i] = [int, bool, str, var]

            argType = type(arg)

            #-- Only one type --
            if type(expectedArgs[i]) == type:
                if argType != expectedArgs[i]:
                    Error.print(53, "Invalid argument type (expected {0} given {1})".format(expectedArgs[i],argType))    #
            #-- More types --
            elif type(expectedArgs[i]) == list:

                if argType not in expectedArgs[i]:    # Check if used argument has one of expected types
                    Error.print(53, "Invalid argument type (expected {0} given {1})".format(expectedArgs[i],argType))    #
            #-- Wrong method parameters --
            else:
                Error.print(Error.internal, "Illegal usage of Instruction.checkArguments()")

            i = i+1


    def execute(self):
        """Executes instructions"""
        if self.opcode == "DEFVAR":
            self.__DEFVAR()
        elif self.opcode == "ADD":
            self.__ADD()
        elif self.opcode == "SUB":
            self.__SUB()
        elif self.opcode == "MUL":
            self.__MUL()
        elif self.opcode == "IDIV":
            self.__IDIV()
        elif self.opcode == "WRITE":
            self.__WRITE()
        elif self.opcode == "MOVE":
            self.__MOVE()
        elif self.opcode == "PUSHS":
            self.__PUSHS()
        elif self.opcode == "POPS":
            self.__POPS()
        elif self.opcode == "STRLEN":
            self.__STRLEN()
        elif self.opcode == "CONCAT":
            self.__CONCAT()
        elif self.opcode == "GETCHAR":
            self.__GETCHAR()
        elif self.opcode == "SETCHAR":
            self.__SETCHAR()
        elif self.opcode == "TYPE":
            self.__TYPE()
        elif self.opcode == "AND":
            self.__AND()
        elif self.opcode == "OR":
            self.__OR()
        elif self.opcode == "NOT":
            self.__NOT()
        elif self.opcode == "LT" or self.opcode == "EQ" or self.opcode == "GT":
            self.__LT_EQ_GT()
        elif self.opcode == "INT2CHAR":
            self.__INT2CHAR()
        elif self.opcode == "STRI2INT":
            self.__STRI2INT()
        elif self.opcode == "READ":
            self.__READ()
        elif self.opcode == "LABEL":
            pass
        elif self.opcode == "JUMP":
            self.__JUMP()
        elif self.opcode == "JUMPIFEQ":
            self.__JUMPIFEQ()
        elif self.opcode == "JUMPIFNEQ":
            self.__JUMPIFNEQ()
        elif self.opcode == "DPRINT" or self.opcode == "BREAK":
            pass
        elif self.opcode == "CREATEFRAME":
            self.__CREATEFRAME()
        elif self.opcode == "PUSHFRAME":
            self.__PUSHFRAME()
        elif self.opcode == "POPFRAME":
            self.__POPFRAME()
        elif self.opcode == "CALL":
            self.__CALL()
        elif self.opcode == "RETURN":
            self.__RETURN()
        elif self.opcode == "EXIT":
            self.__EXIT()
        else:
            Error.print(32, "Unknown syntax in a instruction")        #syntax error


    #-- Instrcution DEFVAR --
    def __DEFVAR(self):
        self.__checkArguments(var)
        Frames.add(self.args[0].getName())


    #-- Instrcution ADD --
    def __ADD(self):
        self.__checkArguments(var, [int, var], [int, var])
        self.args[0].setValue(int(self.args[1]) + int(self.args[2]))


    #-- Instrcution SUB --
    def __SUB(self):
        self.__checkArguments(var, [int, var], [int, var])
        self.args[0].setValue(int(self.args[1]) - int(self.args[2]))


    #-- Instrcution ADD --
    def __MUL(self):
        self.__checkArguments(var, [int, var], [int, var])
        self.args[0].setValue(int(self.args[1]) * int(self.args[2]))


    #-- Instrcution IDIV --
    def __IDIV(self):
        self.__checkArguments(var, [int, var], [int, var])
        if int(self.args[2]) == 0:    #zero division check
            Error.print(57, "Devidsion by zero")
        self.args[0].setValue(int(self.args[1]) // int(self.args[2]))


    #-- Instrcution WRITE --
    def __WRITE(self):
        self.__checkArguments(symb)
        #-- if var -> get its value --
        if type(self.args[0]) == var:
            value = self.args[0].getValue()
        else:
            value = self.args[0]

        #-- Print bool as words --
        if type(value) == bool:
            if value == True:
                value = "true"
            else:
                value = "false"

        #-- end = '' to prevent new lines --
        print(str(value), end = '')


    #-- Instrcution MOVE --
    def __MOVE(self):
        self.__checkArguments(var, symb)
        self.args[0].setValue(self.args[1])


    #-- Instrcution PUSHS --
    def __PUSHS(self):
        self.__checkArguments(symb)

        val = self.args[0]
        if type(val) == var:
            val = val.getValue()

        Interpret.valStack.push(val)

    #-- Instrcution POPS --
    def __POPS(self):
        self.__checkArguments(var)
        val = Interpret.valStack.pop()

        self.args[0].setValue(val)


    #-- Instrcution STRLEN --
    def __STRLEN(self):
        self.__checkArguments(var, [str, var])
        self.args[0].setValue(len(str(self.args[1])))


    #-- Instrcution CONCAT --
    def __CONCAT(self):
        self.__checkArguments(var, [str, var], [str, var])
        self.args[0].setValue(str(self.args[1]) + str(self.args[2]))


    #-- Instrcution GETCHAR --
    def __GETCHAR(self):
        self.__checkArguments(var, [str, var], [int, var])
        if int(self.args[2]) >= len(str(self.args[1])):
            Error.print(58, "getchar out of reach error")    #string error
        self.args[0].setValue(str(self.args[1])[int(self.args[2])])


    #-- Instrcution GETCHAR --
    def __SETCHAR(self):
        self.__checkArguments(var, [int, var], [str, var])
        if int(self.args[1]) >= len(str(self.args[0])) or len(str(self.args[2])) == 0:
            Error.print(58, "setchar out of reach error")    #string error
        self.args[0].setValue(str(self.args[0])[:int(self.args[1])] + str(self.args[2])[0] + str(self.args[0])[int(self.args[1])+1:])


    #-- Instrcution TYPE --
    def __TYPE(self):
        self.__checkArguments(var, symb)
        #-- if var -> get its value --
        if type(self.args[1]) == var:
            value = self.args[1].getValue()
        else:
            value = self.args[1]

        #-- Convert value type name to str --
        valueType = re.search(r"<class '(str|bool|int)'>", str(type(value))).group(1)

        #-- Rename str to string --
        if valueType == "str" and value == "":
            self.args[0].setValue("nil")
        elif valueType == "str":
            self.args[0].setValue("string")
        elif valueType == "int":
            self.args[0].setValue("int")
        elif valueType == "bool":
            self.args[0].setValue("bool")
        else:
            Error.print(31, "Type was not recognised")


    #-- Instrcution AND --
    def __AND(self):
        self.__checkArguments(var, [bool, var], [bool, var])
        self.args[0].setValue(bool(self.args[1]) and bool(self.args[2]))


    #-- Instrcution OR --
    def __OR(self):
        self.__checkArguments(var, [bool, var], [bool, var])
        self.args[0].setValue(bool(self.args[1]) or bool(self.args[2]))


    #-- Instrcution NOT --
    def __NOT(self):
        self.__checkArguments(var, [bool, var])
        self.args[0].setValue(not bool(self.args[1]))


    #-- Instrcution LT/EQ/GT --
    def __LT_EQ_GT(self):

        self.__checkArguments(var, symb, symb)

        #-- if var -> get its value --
        if type(self.args[1]) == var:
            valueA = self.args[1].getValue()
        else:
            valueA = self.args[1]

        if type(self.args[2]) == var:
            valueB = self.args[2].getValue()
        else:
            valueB = self.args[2]

        #-- Compare types --
        if type(valueA) != type(valueB):
            Error.print(53, "Comparing two diffrente operands")

        #-- opcode determines the instruction --
        op = self.opcode
        if op == "EQ":
            self.args[0].setValue(valueA == valueB)
        elif op == "LT":
            self.args[0].setValue(valueA < valueB)
        elif op == "GT":
            self.args[0].setValue(valueA > valueB)
        else:
            Error.print(32, "Wrong operation syntax")


    #-- Instrcution INT2CHAR --
    def __INT2CHAR(self):
        self.__checkArguments(var, [int, var])
        try:
            self.args[0].setValue(chr(int(self.args[1])))
        except ValueError:
            Error.print(58, "Can't convert int to char")    #string error


    #-- Instrcution STRI2INT --
    def __STRI2INT(self):
        self.__GETCHAR()
        self.args[0].setValue(ord(self.args[0].getValue()))


    #-- Instrcution READ --
    def __READ(self):
        global InputFile
        self.__checkArguments(var, str)

        val = InputFile.readline()
        typ = self.args[1]

        if typ == "string":
            if val == None: val = ""
        elif typ == "int":
            try:
                val = int(val)
            except Exception as e:
                val = "" # nil@nil
        elif typ == "bool":
            val = val.lower() == "true"

        self.args[0].setValue(val)

    #-- Instrcution LABEL --
    def LABEL(self):
        self.__checkArguments(label)
        Labels.add(self.args[0])


    #-- Instrcution JUMP --
    def __JUMP(self):
        self.__checkArguments(label)
        Labels.jump(self.args[0])


    #-- Instrcutions JUMPIFEQ --
    def __JUMPIFEQ(self):

        self.__checkArguments(label, symb, symb)

        #-- Get values inside var --
        if type(self.args[1]) == var:
            valueA = self.args[1].getValue()
        else:
            valueA = self.args[1]

        if type(self.args[2]) == var:
            valueB = self.args[2].getValue()
        else:
            valueB = self.args[2]

        #-- Check for same type --
        if type(valueA) != type(valueB):
            Error.print(53, "Comparing two diffrent types")    #operand error

        if valueA == valueB:
            Labels.jump(self.args[0])


    #-- Instrcutions JUMPIFNEQ --
    def __JUMPIFNEQ(self):

        self.__checkArguments(label, symb, symb)

        #-- Get values inside var --
        if type(self.args[1]) == var:
            valueA = self.args[1].getValue()
        else:
            valueA = self.args[1]

        if type(self.args[2]) == var:
            valueB = self.args[2].getValue()
        else:
            valueB = self.args[2]

        #-- Check for same type --
        if type(valueA) != type(valueB):
            Error.print(53, "Comparing two diffrent types")    #operand error

        if valueA != valueB:
            Labels.jump(self.args[0])


    #-- Instrcution CREATEFRAME --
    def __CREATEFRAME(self):
        self.__checkArguments()
        Frames.tf = {}


    #-- Instrcution PUSHFRAME --
    def __PUSHFRAME(self):
        self.__checkArguments()
        if Frames.tf == None:
            Error.print(55, "Frame is not yet defined")
        Frames.stack.append(Frames.tf)
        Frames.lf = Frames.stack[-1]
        Frames.tf = None


    #-- Instrcution POPFRAME --
    def __POPFRAME(self):
        self.__checkArguments()
        if Frames.lf == None:
            Error.print(55, "Frame is not yet defined")
        Frames.tf = Frames.stack.pop()

        if len(Frames.stack) > 0:
            Frames.lf = Frames.stack[-1]
        else :
            Frames.lf = None


    #-- Instrcution CALL --
    def __CALL(self):
        Interpret.callStack.push(Interpret.instOrder)
        self.__JUMP()


    #-- Instrcution RETURN --
    def __RETURN(self):
        self.__checkArguments()
        Interpret.instOrder = Interpret.callStack.pop()

    #-- Instrcution EXIT --
    def __EXIT(self):
        self.__checkArguments(symb)
        if type(self.args[0]) == var:
            value = self.args[0].getValue()
        else:
            value = self.args[0]

        if value >= 0 and value <= 49:
            exit(value)
        else:
            Error.print(57, "Wrong EXIT value")

    def __str__(self):
        return (f"pop:{Interpret.callStack.content}" + 
         f"line: {Interpret.instOrder} {self.opcode}" + 
         f"stack :: {Interpret.valStack.content}" )




main()
