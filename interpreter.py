#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: interpreter.py
# Author: alukard <alukard6942@github>
# Date: 13.04.2021
# Last Modified Date: 13.04.2021

import xml.etree.ElementTree as ET
import re



# GLOBAL VARS
# extern
GLBlineLine = 0
GLBprog = []
GLBtable = []


def err(msg="general err", code=0):

    print(msg)

    if code: exit(code)





class GFvar:
    def __init__(self, val, line):
        self.val = val
        self.line = line

class LFvar:
    def __init__(self, val, context):
        self.val = val
        self.context = context


class Table:

    context = [0, -1]

    globalVars = dict()
    localVars = dict()
    tempVars = dict()

    stack = []



    def createFrame(self):
        """ Vytvoří nový dočasný rámec a zahodí případný obsah původního dočasného rámce. """
        self.tempVars = dict()


    def pushFrame(self):
        self.stack.insert(0, self.tempVars)

    def popFrame(self):
        self.tempVars = self.stack.pop(0)
    

    def isGlobal(self, var):
        if re.search("^GF@.*$", var):
            return True
        else:
            return False

    def isLocal(self, var):
        if re.search("^LF@.*$", var):
            return True
        else:
            return False

    def defVar(self, var):
        if self.isGlobal(var):
            self.globalVars[var] = None
        elif self.isLocal(var):
            self.localVars[var] = None
        else:
            self.tempVars[var] = None

    def __setattr__(self, var, val):
        if self.isGlobal(var):
            if var not in self.globalVars:
                err(f"{var} not a gloval var", 1)
            self.globalVars[var] = val

        if self.isLocal(var):
            if var not in self.localVars:
                err(f"{var} not a local var", 1)
            self.localVars[var] = val

        else: 
            if var not in self.tempVars:
                err(f"{var} not a temp var", 1)
            self.tempVars[var] = val
            

    def __getattribute__(self, var):
        if self.isGlobal(var):
            if var not in self.globalVars:
                err(f"{var} not a gloval var", 1)
            return self.globalVars[var] 

        if self.isLocal(var):
            if var not in self.localVars:
                err(f"{var} not a local var", 1)
            return self.localVars[var]

        else: 
            if var not in self.tempVars:
                err(f"{var} not a temp var", 1)
            return self.tempVars[var]


class Arg:
    pass

class Var:
    pass

class Instruction: 

    def __init__(self, data):
        self.data = data
        self.opcode = data.attrib["opcode"]

    def get(self):
        op = self.opcode
        if (op == "MOVE"):


    def __str__(self):
        return self.opcode

class Label(Arg):
    def __init__ (self, data):
        self.name = data.
        self.line = 0




class Int(Var):

    def __init__(self, value):
        if not int(value) or value != 0:
            err(f"{value} not a int", 1)
        self.value = value


# GLOBAL VARS

GLBline = 0
GLBprog = dict()
GLBtable = Table()





xml = ET.parse("example.xml")
if not xml: err("no file", 1)

program = xml.getroot()
if program.tag != "program" :
    err("root is to be \"program\"", 0)

order = 0
for tmp in program :
    order = tmp.attrib["order"]

    if order in GLBprog:
        err(" unclear order", 1)

    GLBprog[order] = Instruction(tmp).get()

# check if no numbers are minssing
if order != len(GLBprog):
    err("program mised a step")


table = Table()

while (GLBline< len(GLBprog)):
    inst = GLBprog[GLBline]

    opcode = inst.opcode

    print(inst)









    
# end while loop
    GLBline += 1






