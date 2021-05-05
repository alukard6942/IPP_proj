#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: interpret.py
# Author: xkoval18 <xkoval18@github>
# Date: 21.04.2021
# Last Modified Date: 21.04.2021

import xml.etree.ElementTree as ET
import re
import sys



tableerrptr = None
def err(msg="general err", code=0):

    try:
        sys.stderr.write(f"line: {tableerrptr.Line}   ERROR {code}\n")
        sys.stderr.write(f"{tableerrptr.Prog[tableerrptr.Line]} \n")
        # print(tableerrptr)
    except Exception as e:
        pass
    sys.stderr.write(f"{msg} \n")

    if code: exit(code)



def main():

    table = Table()
    global tableerrptr
    tableerrptr = table

    # parse args
    xmlfile = None
    stdfile = None
    for ar in sys.argv[1:]:
    
        if ar == "--help":
            print(""" python3 interpreter.py [OPTION]

 options:
==========
 --version -v    | version
 --help -h       | show this help
 --source=file   | vstupní soubor s XML reprezentací zdrojového kódu
 --input=file    | soubor se vstupy pro samotnou interpretaci zadaného zdrojového kódu""")
            exit(0)
    
        elif ar[:9] == "--source=":
            xmlfile = str(ar[9:])
        
        elif ar[:8] == "--input=":
            stdfile = str(ar[8:])
    
        else:
            err(f"unsuported OPTION: {ar}", 10)
    
    if not xmlfile and not stdfile:
        err(" Alespoň jeden z parametrů (--source nebo --input) musí být vždy zadán. Pokud jeden z nich chybí, jsou chybějící data načítána ze standardního vstupu", 10 )
    
    
    try:
        if not xmlfile:
            xml = ET.parse(sys.stdin)
        else:
            xml = ET.parse(xmlfile)

    except Exception as e:
        err(f"xml file {xmlfile} failed to parse", 32)
    
    program = None
    try:
        if not stdfile:
            table.stdfile = sys.stdin    
        else:
            table.stdfile = open(str(stdfile), "r" ) 
    
        program = xml.getroot()
        if program.tag != "program" :
            err("root is to be \"<program>\"", 32)
        if program.attrib["language"].lower() != "ippcode21" :
            err("language is supose to be ippcode21", 32)

    except Exception as e:
        err(f"bad file {stdfile}", 11)
    
    
    order = 0
    maxim = 0
    for data in program :
        order =  int (data.attrib["order"])
        table.Line = order
        if (maxim < order): maxim = order
    
        if order in table.Prog:
            err(" unclear order", 32)
    
        
        opcode =  data.attrib["opcode"]
        table.append(order, opcode, data)
    
    # check if no numbers are minssing
    if order != len(table.Prog):
        err("program mised a step")
    
    
    table.Line = 0
    while (table.Line <= len(table)):
    
        if table.Line in table.Prog:
            inst = table.Prog[table.Line]
    
            try:
                inst.run()
            except Exception as e:
                err(e, 32)
                inst.jumpend()
    
        table.Line += 1
    
    table.stdfile.close()
    exit(table.exCode)
    



class Argument:

    def __init__(self, data, table):
        self.table = table
        self.text = data.text
        self.typ = data.attrib["type"]

    def var(self):
        if self.typ != "var":
            err(f"internal err err supose to be var instad {self.type}", 32)

        return self.text

    def label(self):
        if self.typ == "label":
            return self.text

    def type(self):
        if self.typ == "type":
            return self.text

        elif self.typ == "var":
            end = 0
            txt = self.symbol()
            for c in txt: 
                if c == "@": break
                end += 1

            typ = txt[0 : end]
            if typ == "nil": typ = "string"
            return typ

        else: return self.typ

    def symbol(self):
        if self.typ == "var":
            return self.table[ self.text ]

        elif self.typ == "string" and not self.text:
            return "nil@nil"

        else:
            itr = 0
            strg = self.text
            out = ""
            while itr < len(strg):
                ch = strg[itr]

                if ch == "\\":
                    ch = chr(int(strg[itr+1 : itr+4]))
                    itr += 3

                out += ch
                itr+=1

            return self.typ + "@" + out

    def __int__(self):
        val = self.symbol()
        if self.type() != "int":
            err(f"{val} is definatly not int", 53)

        val = int(val[4:])
        return val

    def __str__(self):
        val = self.symbol()

        if val == "nil@nil": return ""
        elif val[:7] == "string@":
            return val[7:]

    def __lt__(self, to):
        val = self.symbol()
        typ = self.type()

        if typ == "int":
            b =  int(self) < int(to)
            return b

        elif typ == "string":
            str1 = val.lower()
            str2 = to.symbol().lower()
            for i in range(len(str(val))):
                if ord(str1[i]) < ord(str2[i]):
                    return True
                if ord(str1[i]) > ord(str2[i]):
                    return False
            return False

        elif typ == "bool":
            return not bool(self) and bool(to)
        else:
            err(f"internal err worng type {typ}", 32)

    def __eq__(self, to):
        return str(self.symbol()) == str(to.symbol())

    def __bool__(self):
        val = self.symbol()
        if val[:5] != "bool@":
            err(f"{val} is definatly not booleon", 53)

        return val == "bool@true"


class Instruction: 
    
    def __init__(self, data, table):
        self.table = table
        self.data = data
        self.opcode = data.attrib["opcode"]
        self.__argumentrec = [0]

    def arg(self, i,):
        self.__argumentrec.append(i)
        i -= 1
        return Argument(self.data[i], self.table)

    def jump(self, label):
        if type(label) == int: self.table.Line = label
        else: self.table.Line = self.table.Labels[label]

    def jumpend(self):
        self.table.Line = len(self.table)

    def run(self):
        self.exe()

        argn = len(self.data)
        armax = max(self.__argumentrec)
        if argn != armax:
            err(f" {self.opcode}: namber of arguments given {armax} is wrong", 32)

    def exe(self):
        print(f"todo .exe() for {self.opcode}")

    def __str__(self):
        return str(self.table.Line) + self.opcode


## ========================================
## 
##    COMAND classes declaration
##
## ========================================


class MOVE(Instruction):
    """ move val from arg2 to arg1 """
    def exe(self):
        self.table[self.arg(1).var()] = self.arg(2).symbol()

class CREATEFRAME(Instruction):
    """ Vytvoří nový dočasný rámec a zahodí případný obsah původního dočasného rámce. """
    def exe(self):
        self.table.createFrame()

class PUSHFRAME (Instruction):
    """ Přesuň TF na zásobník rámců. Rámec bude k dispozici přes LF a překryje původní rámce na zásobníku rámců. TF bude po provedení instrukce nedefinován a je třeba jej před dalším použitím vytvořit pomocí CREATEFRAME. Pokus o přístup k nedefinovanému rámci vede na chybu 55. """
    def exe(self):
        self.table.pushFrame()

class  POPFRAME (Instruction):
    """ coment """
    def exe(self):
        self.table.popFrame()

class DEFVAR(Instruction):
    """ move val from arg2 to arg1 """
    def exe(self):
        self.table.defVar( self.arg(1).var() )

class CALL (Instruction):
    """ Uloží inkrementovanou aktuální pozici z interního čítače instrukcí do zásobníku volání a provede skok na zadané návěští (případnou přípravu rámce musí zajistit jiné instrukce). """
    def exe(self):
        self.table.ToReturn.insert(0, self.table.Line)
        self.jump( self.arg(1).label())


class RETURN (Instruction):
    """ Vyjme pozici ze zásobníku volání a skočí na tuto pozici nastavením interního čítače instrukcí (úklid lokálních rámců musí zajistit jiné instrukce). Provedení instrukce při prázdném zásobníku volání vede na chybu 56. """
    def exe(self):
        line = self.table.ToReturn.pop(0)
        self.jump(line)


class PUSHS (Instruction):
    """ Uloží hodnotu ⟨symb⟩ na datový zásobník. """
    def exe(self):
        self.table.MemStack.insert(0, self.arg(1).symbol() )


class POPS (Instruction):
    """ Není-li zásobník prázdný, vyjme z něj hodnotu a uloží ji do proměnné ⟨var⟩, jinak dojde k chybě 56. """
    def exe(self):
        self.table[self.arg(1).var()] = self.table.MemStack.pop(0)


class ADD(Instruction):
    """ Sečte ⟨symb 1 ⟩ a ⟨symb 2 ⟩ (musí být typu int) a výslednou hodnotu téhož typu uloží do proměnné ⟨var⟩."""
    def exe(self):
        self.table[self.arg(1).var()] = "int@"+ str(int(self.arg(2)) + int(self.arg(3)))

class SUB(Instruction):
    """ Sečte ⟨symb 1 ⟩ a ⟨symb 2 ⟩ (musí být typu int) a výslednou hodnotu téhož typu uloží do proměnné ⟨var⟩."""
    def exe(self):
        self.table[self.arg(1).var()] = "int@"+ str(int(self.arg(2)) - int(self.arg(3)))

class MUL(Instruction):
    """ Sečte ⟨symb 1 ⟩ a ⟨symb 2 ⟩ (musí být typu int) a výslednou hodnotu téhož typu uloží do proměnné
    def exe(self):
⟨var⟩."""
    def exe(self):
        self.table[self.arg(1).var()] = "int@"+ str(int(self.arg(2)) * int(self.arg(3)))

class IDIV(Instruction):
    """ Celočíselně podělí celočíselnou hodnotu ze ⟨symb 1 ⟩ druhou celočíselnou hodnotou ze ⟨symb 2 ⟩ (musí být oba typu int) a výsledek typu int přiřadí do proměnné ⟨var⟩. Dělení nulou způsobí chybu 57."""
    def exe(self):
        zero = int(self.arg(3))
        if zero == 0: err("division by zero", 57)
        self.table[self.arg(1).var()] = "int@"+ str(int(self.arg(2)) / zero)

class LT (Instruction):
    """ Instrukce vyhodnotí relační operátor mezi ⟨symb 1 ⟩ a ⟨symb 2 ⟩ (stejného typu; int, bool nebo string) a do ⟨var⟩ zapíše výsledek typu bool (false při neplatnosti nebo true v případě platnosti odpovídající relace). Řetězce jsou porovnávány lexikograficky a false je menší než true. Pro výpočet neostrých nerovností lze použít AND/OR/NOT. S operandem typu nil (další zdrojový operand je libovolného typu) lze porovnávat pouze instrukcí EQ, jinak chyba 53"""
    def exe(self):
        self.table[self.arg(1).var()] = "bool@"+ str( self.arg(2) < self.arg(3)).lower()

class GT (Instruction):
    """ Instrukce vyhodnotí relační operátor mezi ⟨symb 1 ⟩ a ⟨symb 2 ⟩ (stejného typu; int, bool nebo string) a do ⟨var⟩ zapíše výsledek typu bool (false při neplatnosti nebo true v případě platnosti odpovídající relace). Řetězce jsou porovnávány lexikograficky a false je menší než true. Pro výpočet neostrých nerovností lze použít AND/OR/NOT. S operandem typu nil (další zdrojový operand je libovolného typu) lze porovnávat pouze instrukcí EQ, jinak chyba 53"""
    def exe(self):
        self.table[self.arg(1).var()] = "bool@"+ str( self.arg(3) < self.arg(2)).lower()

class EQ (Instruction):
    """ Instrukce vyhodnotí relační operátor mezi ⟨symb 1 ⟩ a ⟨symb 2 ⟩ (stejného typu; int, bool nebo string) a do ⟨var⟩ zapíše výsledek typu bool (false při neplatnosti nebo true v případě platnosti odpovídající relace). Řetězce jsou porovnávány lexikograficky a false je menší než true. Pro výpočet neostrých nerovností lze použít AND/OR/NOT. S operandem typu nil (další zdrojový operand je libovolného typu) lze porovnávat pouze instrukcí EQ, jinak chyba 53"""
    def exe(self):
        self.table[self.arg(1).var()] = "bool@"+ str( self.arg(1) == self.arg(2) ).lower()

class AND(Instruction):
    """ Aplikuje konjunkci (logické A)/disjunkci (logické NEBO) na operandy typu bool ⟨symb 1 ⟩ a ⟨symb 2 ⟩ nebo negaci na ⟨symb 1 ⟩ (NOT má pouze 2 operandy) a výsledek typu bool zapíše do ⟨var⟩."""
    def exe(self):
        self.table[self.arg(1).var()] = "bool@"+ str(bool(self.arg(2)) and bool(self.arg(3))).lower()

class OR (Instruction):
    """ Aplikuje konjunkci (logické A)/disjunkci (logické NEBO) na operandy typu bool ⟨symb 1 ⟩ a ⟨symb 2 ⟩ nebo negaci na ⟨symb 1 ⟩ (NOT má pouze 2 operandy) a výsledek typu bool zapíše do ⟨var⟩."""
    def exe(self):
        self.table[self.arg(1).var()] = "bool@"+ str(bool(self.arg(2)) and bool(self.arg(3))).lower()

class NOT(Instruction):
    """ Aplikuje konjunkci (logické A)/disjunkci (logické NEBO) na operandy typu bool ⟨symb 1 ⟩ a ⟨symb 2 ⟩ nebo negaci na ⟨symb 1 ⟩ (NOT má pouze 2 operandy) a výsledek typu bool zapíše do ⟨var⟩."""
    def exe(self):
        self.table[self.arg(1).var()] = "bool@"+ str(not bool(self.arg(2))).lower()

class INT2CHAR (Instruction):
    """Číselná hodnota ⟨symb⟩ je dle Unicode převedena na znak, který tvoří jednoznakový řetězec přiřazený do ⟨var⟩. Není-li ⟨symb⟩ validní ordinální hodnota znaku v Unicode (viz funkce chr v Python 3), dojde k chybě 58. """
    def exe(self):
        self.table[self.arg(1).var()] = "string@" + chr(self.arg(2).__int__())

class STRI2INT (Instruction):
    """Do ⟨var⟩ uloží ordinální hodnotu znaku (dle Unicode) v řetězci ⟨symb 1 ⟩ na pozici ⟨symb 2 ⟩ (indexováno od nuly). Indexace mimo daný řetězec vede na chybu 58. Viz funkce ord v Python 3 """
    def exe(self):
        try:
            self.table[self.arg(1).var()] = "int@" + str(ord( str(self.arg(2))[ int(self.arg(3)) ] ))
        except Exception as e:
            err(" Indexace mimo daný řetězec vede na chybu 58. Viz funkce ord v Python 3.", 58)

class READ(Instruction):
    """Načte jednu hodnotu dle zadaného typu ⟨type⟩ ∈ {int, string, bool} a uloží tuto hodnotu do proměnné ⟨var⟩. Načtení proveďte vestavěnou funkcí input() (či analogickou) jazyka Python 3, pak proveďte konverzi na specifikovaný typ ⟨type⟩. Při převodu vstupu na typ bool nezáleží na velikosti písmen a řetězec true“ se převádí na bool@true, vše ostatní na bool@false. V případě chybného nebo chybějícího vstupu bude do proměnné ⟨var⟩ uložena hodnota nil@nil"""
    def exe(self):
        typ = self.arg(2).type()
        val = "nil@nil"

        try:
            data = self.table.stdfile.readline()

            if typ == "bool":
                if data.lower() == "true":
                    val = "bool@true"
                else:
                    val = "bool@false"
            elif typ == "int":
                val = "int@" + str(int(data))
            elif typ == "string":
                if data: val = "string@" + data
            else:
                err("not suported type", 1)
        except Exception as e:
            val = "nil@nil"

        self.table[self.arg(1).var()] = val

class WRITE(Instruction):
    """ Vypíše hodnotu ⟨symb⟩ na standardní výstup. Až na typ bool a hodnotu nil@nil je formát výpisu kompatibilní s příkazem print jazyka Python 3 s doplňujícím parametrem end='' (za-mezí dodatečnému odřádkování). Pravdivostní hodnota se vypíše jako true a nepravda jako false. Hodnota nil@nil se vypíše jako prázdný řetězec """
    def exe(self):
        arg = self.arg(1)
        typ = arg.type()

        if typ == "int":
            print( str(int(arg)), end="" )
        elif typ == "bool":
            print( str(bool(arg)).lower(), end="" )
        elif typ == "string":
            print( str(arg), end="" )
        else:
            err(f"unsuported type: {typ}", 32)
        
class CONCAT(Instruction):
    """ Do proměnné ⟨var⟩ uloží řetězec vzniklý konkatenací dvou řetězcových operandů ⟨symb 1 ⟩ a ⟨symb 2 ⟩ (jiné typy nejsou povoleny). """
    def exe(self):
        self.table[self.arg(1).var()] = "string@" + str(self.arg(2)) + str(self.arg(3))

class STRLEN(Instruction):
    """ coment """
    def exe(self):
        self.table[self.arg(1).var()] = "int@" + str(len(str(self.arg(2))))


class GETCHAR(Instruction):
    """ Do ⟨var⟩ uloží řetězec z jednoho znaku v řetězci ⟨symb 1 ⟩ na pozici ⟨symb 2 ⟩ (indexováno celým číslem od nuly). Indexace mimo daný řetězec vede na chybu 58."""
    def exe(self):
        try:
            self.table[self.arg(1).var()] = "string@" + str(self.arg(2))[int(self.arg(3))]
        except Exception as e:
            err("Indexace mimo daný řetězec vede na chybu", 58)

class SETCHAR(Instruction):
    """ Zmodifikuje znak řetězce uloženého v proměnné ⟨var⟩ na pozici ⟨symb 1 ⟩ (indexováno celočíselně od nuly) na znak v řetězci ⟨symb 2 ⟩ (první znak, pokud obsahuje ⟨symb 2 ⟩ více znaků). Výsledný řetězec je opět uložen do ⟨var⟩. Při indexaci mimo řetězec ⟨var⟩ nebo v případě prázdného řetězce v ⟨symb 2 ⟩ dojde k chybě 58. """
    def exe(self):
        try:
            # variable[ arg1 ] = arg2
            tomod = self.table[self.arg(1).var()] 
            self.table[self.arg(1).var()] = tomod[self.arg(2)] = self.arg(3).__str__()[0] 
        except Exception as e:
            err("Indexace mimo daný řetězec vede na chybu", 58)

class TYPE(Instruction):
    """Dynamicky zjistí typ symbolu ⟨symb⟩ a do ⟨var⟩ zapíše řetězec značící tento typ (int, bool, string nebo nil). Je-li ⟨symb⟩ neinicializovaná proměnná, označí její typ prázdným řetězcem."""
    def exe(self):
        self.table[self.arg(1).var()] = "string@" + self.arg(2).type()


class LABEL(Instruction):
    """ Speciální instrukce označující pomocí návěští ⟨label⟩ důležitou pozici v kódu jako potenciální cíl libovolné skokové instrukce. Pokus o vytvoření dvou stejně pojmenovaných návěští na různých místech programu je chybou 52. """
    def __init__ (self, data, table): 
        super().__init__(data, table)
        lable= self.arg(1).label()
        if lable in self.table.Labels:
            err(f"lable: {lable} already exists", 52)
        self.table.Labels[ lable ] = self.table.Line

    def exe(self):
        tmp = self.arg(1).label()
    

class JUMP(Instruction):
    """ Provede nepodmíněný skok na zadané návěští ⟨label⟩. """
    def exe(self):
        self.jump(self.arg(1).label())


class JUMPIFEQ(Instruction):
    """Pokud jsou ⟨symb 1 ⟩ a ⟨symb 2 ⟩ stejného typu nebo je některý operand nil (jinak chyba 53) a zároveň se jejich hodnoty rovnají, tak provede skok na návěští ⟨label⟩."""
    def exe(self):
        if ( self.arg(2).__eq__(self.arg(3)) ): self.jump( self.arg(1).label() )
        
class JUMPIFNEQ(Instruction):
    """Pokud jsou ⟨symb 1 ⟩ a ⟨symb 2 ⟩ stejného typu nebo je některý operand nil (jinak chyba 53) a zároveň se jejich hodnoty rovnají, tak provede skok na návěští ⟨label⟩."""
    def exe(self):
        if  not (self.arg(2).__eq__(self.arg(3)) ): self.jump( self.arg(1).label() )


class EXIT (Instruction):
    """ coment """
    def exe(self):
        code = self.arg(1).__int__()
        if not 0 <= code < 50: err(f"Nevalidní celočíselná hodnota {code} vede na chybu", 57)
        exit(code)


class DPRINT(Instruction):
    """Předpokládá se, že vypíše zadanou hodnotu ⟨symb⟩ na standardní chybový výstup (stderr)."""
    def exe(self):
        sys.stderr.write( str(self.arg(1)) )


class BREAK (Instruction):
    """Předpokládá se, že na standardní chybový výstup (stderr) vypíše stav interpretu (např. pozice v kódu, obsah rámců, počet vykonaných instrukcí) v danou chvíli (tj. během vykonávání této instrukce)."""
    def exe(self):
        sys.stderr.write( str(self.table) )



class Table:

    Line = 1
    exCode = 0

    Prog = dict()
    Labels = dict()
    ToReturn = []
    MemStack = []

    globalVars = dict()
    tempVars = None

    stack = []

    stdfile = sys.stdin

    def append(self, order, op, data):
        if order in self.Prog: 
            err("unclear order of instructions", 32)
        self.Prog[order] = self.__get(op, data)

    # fuckn helll this shit is so not optimal it hurts
    def __get(self, op, data):
        try:
            if   op == "MOVE":          return MOVE(data, self)
            elif op == "LABEL":         return LABEL(data , self )
            elif op == "CREATEFRAME":   return CREATEFRAME(data, self )
            elif op == "PUSHFRAME":     return PUSHFRAME(data, self )
            elif op == "POPFRAME":      return POPFRAME(data, self )
            elif op == "DEFVAR":        return DEFVAR(data, self )
            elif op == "CALL":          return CALL(data, self )
            elif op == "RETURN":        return RETURN(data, self )
            elif op == "PUSHS":         return PUSHS(data, self )
            elif op == "POPS":          return POPS(data, self )
            elif op == "ADD":           return ADD(data, self )
            elif op == "SUB":           return SUB(data, self )
            elif op == "MUL":           return MUL(data, self )
            elif op == "IDIV":          return IDIV(data, self )
            elif op == "LT":            return LT(data, self )
            elif op == "GT":            return GT(data, self )
            elif op == "EQ":            return EQ(data, self )
            elif op == "AND":           return AND(data, self )
            elif op == "OR":            return OR(data, self )
            elif op == "NOT":           return NOT(data, self )
            elif op == "INT2CHAR":      return INT2CHAR(data, self )
            elif op == "STRI2INT":      return STRI2INT(data, self )
            elif op == "READ":          return READ(data, self )
            elif op == "WRITE":         return WRITE(data, self )
            elif op == "CONCAT":        return CONCAT(data, self )
            elif op == "STRLEN":        return STRLEN(data, self )
            elif op == "GETCHAR":       return GETCHAR(data, self )
            elif op == "SETCHAR":       return SETCHAR(data, self )
            elif op == "TYPE":          return TYPE(data, self )
            elif op == "JUMP":          return JUMP(data, self )
            elif op == "JUMPIFEQ":      return JUMPIFEQ (data, self )
            elif op == "JUMPIFNEQ":     return JUMPIFNEQ (data, self )
            elif op == "EXIT":          return EXIT (data, self )
            elif op == "DPRINT":        return DPRINT (data, self )
            elif op == "BREAK":         return BREAK (data, self )
            else:
                err(f"unsuported opcode {op}" , 32)
        except Exception as e:
            err(f"unsuported opcode {op}" , 32)


    def createFrame(self):
        """ Vytvoří nový dočasný rámec a zahodí případný obsah původního dočasného rámce. """
        self.tempVars = dict()


    def pushFrame(self):
        if self.tempVars != None: 
            self.stack.insert(0, self.tempVars)
        else:
            err("Pokus o přístup k nedefinovanému rámci vede na chybu", 55)

    def popFrame(self):
        try:
            self.tempVars = self.stack.pop(0)
        except Exception as e:
            err("Pokus o přístup k nedefinovanému rámci vede na chybu", 55)
    

    def __isGlobal(self, var):
        if re.search("^GF@.*$", var):
            return True
        else:
            return False

    def __isLocal(self, var):
        if re.search("^LF@.*$", var):
            return True
        else:
            return False

    def __isTemp(self, var):
        if re.search("^TF@.*$", var):
            return True
        else:
            return False

    def defVar(self, var):

        if self.__isGlobal(var):
            frame = self.globalVars
        elif self.__isLocal(var) and len(self.stack) > 0:
            frame = self.stack[-1]
        elif self.__isTemp(var) and self.tempVars != None:
            frame = self.tempVars
        else:
            frame = None
            err("Pokus o přístup k nedefinovanému rámci vede na chybu", 55)

        if var[3:] in frame:
            err(f"var {var} does exit", 52)

        frame[var[3:]] = False

    def __len__(self):
        if len( self.Prog ) == 0: return 0 

        return max( self.Prog )

    def __setitem__(self, var, val):

        var_t  = var
        var  = var[3:]

        if self.__isGlobal(var_t):
            if var not in self.globalVars:
                err(f"{var_t} not a gloval var", 54)
            self.globalVars[var] = val

        elif self.__isLocal(var_t):
            try:
                if var not in self.stack[-1]:
                    err(f"{var_t} not a local var", 54)
                self.stack[-1] = val
            except Exception as e:
                err("local variable table not jet defined", 55)

        elif self.__isTemp(var_t): 
            if var not in self.tempVars:
                err(f"{var_t} not a temp var", 54)
            self.tempVars[var] = val
        else:
            err(f"{var_t} not a valid variable var", 32)
            

    def __getitem__(self, var):
        var_t  = var
        var  = var[3:]

        #print (var)
        ret = None

        if self.__isGlobal(var_t):
            if var not in self.globalVars:
                err(f"{var_t} not a gloval var", 56)
            ret = self.globalVars[var] 

        elif self.__isLocal(var_t):
            try:
                if var not in self.stack[-1]:
                    err(f"{var_t} not a local var", 56)
                ret = self.stack[-1]
            except Exception as e:
                err("local variable table not jet defined", 55)

        elif self.__isTemp(var_t): 
            if var not in self.tempVars:
                err(f"{var_t} not a temp var", 56)
            ret = self.tempVars[var]

        else:
            err(f"var {var_t} is not valid variable", 32)
        if ret == None:
            err(f"var {var_t} is not initialized", 56)

        return ret

    def __str__(self):

        def rep(elm, i):
            return str(i) + ": "+ str(elm[i]) + "\n"

        out = "LINE: " + str(self.Line) + "\n"

        out += "TABLE\n-----------\n"
        for i in self.globalVars:
            out += rep(self.globalVars, i)
        for i in self.stack[-1]:
            out += rep(self.stack[-1], i)
        for i in self.tempVars:
            out += rep(self.tempVars, i)
        for stac in self.stack :
            for i in stac:
                out += rep(stac, i)

        out += "LABELS\n-------------\n"
        for i in self.Labels:
            out+= i + ": " + str(self.Labels[i]) + "\n"

        out += "heap\n-------------------\n"
        for i in self.ToReturn:
           out+= str(i) + "\n"
        out += "-------------------\n"


        return out



main()

