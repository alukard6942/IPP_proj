#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: interpreter.py
# Author: alukard <alukard6942@github>
# Date: 13.04.2021
# Last Modified Date: 13.04.2021

import xml.etree.ElementTree as ET
import re
import sys



# GLOBAL VARS
# extern
# GLBtable = object()


def err(msg="general err", code=0):

    print(table.Line)
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

    Line = 1
    Prog = dict()
    Labels = dict()
    ToReturn = []
    MemStack = []


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

        var_t  = var
        var  = var[3:]

        if self.isGlobal(var_t):
            self.globalVars[var] = "nil@nil"
        elif self.isLocal(var_t):
            self.localVars[var] = "nil@nil"
        else:
            self.tempVars[var] = "nil@nil"

    def __setitem__(self, var, val):

        var_t  = var
        var  = var[3:]

        if self.isGlobal(var_t):
            if var not in self.globalVars:
                err(f"{var_t} not a gloval var", 1)
            self.globalVars[var] = val

        elif self.isLocal(var_t):
            if var not in self.localVars:
                err(f"{var_t} not a local var", 1)
            self.localVars[var] = val

        else: 
            if var not in self.tempVars:
                err(f"{var_t} not a temp var", 1)
            self.tempVars[var] = val
            

    def __getitem__(self, var):
        var_t  = var
        var  = var[3:]

        #print (var)

        if self.isGlobal(var_t):
            if var not in self.globalVars:
                err(f"{var_t} not a gloval var", 1)
            return self.globalVars[var] 

        if self.isLocal(var_t):
            if var not in self.localVars:
                err(f"{var_t} not a local var", 1)
            return self.localVars[var]

        else: 
            if var not in self.tempVars:
                err(f"{var_t} not a temp var", 1)
            return self.tempVars[var]

    def __str__(self):
        out = "TABLE\n-----------\n"
        for i in self.globalVars:
            out += i + ": "+ str(self.globalVars[i]) + "\n"
        for i in self.localVars:
            out += i + ": "+ str(self.localVars[i])+ "\n"
        for i in self.tempVars:
            out += i + ": "+ str(self.tempVars[i])+ "\n"
        for l in self.stack :
            for i in l:
                out += i+ ": "+ str(self.stack[l][i]) + "\n"

        out += "LABELS\n-------------\n"
        for i in self.Labels:
            out+= i + ": " + str(self.Labels[i]) + "\n"

        return out
table = Table()

class Argument:

    def __init__(self, data):
        self.text = data.text
        self.typ = data.attrib["type"]

    def var(self):
        if self.typ != "var":
            err(f"internal err err supose to be var instad {self.type}", 69)

        return self.text

    def label(self):
        if self.typ == "label":
            return self.text

    def type(self):
        if self.typ == "type":
            return self.text

    def symbol(self):
        if   self.typ in ["int", "string", "float"]:
            if not self.text: return "nil@nil"
            return self.text
        elif self.typ == "var":
            return table[ self.text ]
        else :
            err(f"internal err unsuported tipe {self.typ} ")

    def int(self):
        val = self.symbol()
        if val[:4] != "int@":
            raise NameError(f"{val} is definatly not int")

        return int(val[4:])

    def string(self):
        val = self.symbol()
        if val == "nil@nil": return ""

        elif val[:7] == "string@":
            return val[7:]
        else: 
            return val


    def lt(self, to):
        val = self.symbol()
        if val[:4] != "int@":
            return self.int() < to.int()

        if val[:7] != "string@":
            str1 = val.lower()
            str2 = to.symbol().lower()
            for i in range(len(str(val))):
                if ord(str1[i]) < ord(str2[i]):
                    return True
                if ord(str1[i]) > ord(str2[i]):
                    return False
            return False

        if val[:5] != "bool@":
            return not self.bool() and to.bool()

    def eq(self, to):
        return self.string() == to.string() or self.symbol() == to.symbol()

    def bool(self):
        val = self.symbol()
        if val[:5] != "bool@":
            raise NameError(f"{val} is definatly not booleon")

        return val == "bool@true"
    
    def __str__(self):
        val = self.text
        if val == "nil@nil":
            return ">" + "" + "<"
        if val[:7] == "string@": return ">" + val[7:] + "<"
        elif val[:4] == "int@": return ">" + val[4:] + "<"
        elif val[:5] == "bool@": return ">" + val[7:] + "<"

        return ">" + val + "<"


class Instruction: 
    

    def __init__(self, data):
        self.data = data
        self.opcode = data.attrib["opcode"]

    def arg(self, i,):
        i -= 1
        return Argument(self.data[i])

    def jump(self, label):
        table.Line = table.Labels[label]


    def exe(self):
        print(f"todo .exe() for {self.opcode}")

    def __str__(self):
        return str(table.Line) + self.opcode


class MOVE(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ move val from arg2 to arg1 """
        table[self.arg(1).var()] = self.arg(2).symbol()

class CREATEFRAME(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Vytvoří nový dočasný rámec a zahodí případný obsah původního dočasného rámce. """
        table.createFrame()

class PUSHFRAME (Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ coment """
        table.pushFrame()

class  POPFRAME (Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ coment """
        table.popFrame()

class DEFVAR(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ move val from arg2 to arg1 """
        table.defVar( self.arg(1).var() )

class CALL (Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Uloží inkrementovanou aktuální pozici z interního čítače instrukcí do zásobníku volání a provede skok na zadané návěští (případnou přípravu rámce musí zajistit jiné instrukce). """
        table.ToReturn.insert(0, table.Line)
        self.jump( self.arg(1).label())


class RETURN (Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Vyjme pozici ze zásobníku volání a skočí na tuto pozici nastavením interního čítače instrukcí (úklid lokálních rámců musí zajistit jiné instrukce). Provedení instrukce při prázdném zásobníku volání vede na chybu 56. """
        table.Line = table.ToReturn.pop(0)+1  ## only valid jump not to label


class PUSHS (Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Uloží hodnotu ⟨symb⟩ na datový zásobník. """
        table.MemStack.insert(0, self.arg(1).symbol() )


class POPS (Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Není-li zásobník prázdný, vyjme z něj hodnotu a uloží ji do proměnné ⟨var⟩, jinak dojde k chybě 56. """
        table[self.arg(1).var()] = table.MemStack.pop(0)


class ADD(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Sečte ⟨symb 1 ⟩ a ⟨symb 2 ⟩ (musí být typu int) a výslednou hodnotu téhož typu uloží do proměnné ⟨var⟩."""
        table[self.arg(1)] = "int@"+ str(self.arg(1).int() + self.arg(2).int())

class SUB(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Sečte ⟨symb 1 ⟩ a ⟨symb 2 ⟩ (musí být typu int) a výslednou hodnotu téhož typu uloží do proměnné ⟨var⟩."""
        table[self.arg(1).var()] = "int@"+ str(self.arg(1).int() - self.arg(2).int())

class MUL(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Sečte ⟨symb 1 ⟩ a ⟨symb 2 ⟩ (musí být typu int) a výslednou hodnotu téhož typu uloží do proměnné
⟨var⟩."""
        table[self.arg(1).var()] = "int@"+ str(self.arg(1).int() * self.arg(2).int())

class IDIV(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Celočíselně podělí celočíselnou hodnotu ze ⟨symb 1 ⟩ druhou celočíselnou hodnotou ze ⟨symb 2 ⟩ (musí být oba typu int) a výsledek typu int přiřadí do proměnné ⟨var⟩. Dělení nulou způsobí chybu 57."""
        zero = self.arg(2).int()
        if zero == 0: err("division by zero", 57)
        table[self.arg(1).var()] = "int@"+ str(self.arg(1).int() / zero)

class LT (Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Instrukce vyhodnotí relační operátor mezi ⟨symb 1 ⟩ a ⟨symb 2 ⟩ (stejného typu; int, bool nebo string) a do ⟨var⟩ zapíše výsledek typu bool (false při neplatnosti nebo true v případě platnosti odpovídající relace). Řetězce jsou porovnávány lexikograficky a false je menší než true. Pro výpočet neostrých nerovností lze použít AND/OR/NOT. S operandem typu nil (další zdrojový operand je libovolného typu) lze porovnávat pouze instrukcí EQ, jinak chyba 53"""
        table[self.arg(1).var()] = "bool@"+ str(self.arg(2).lt(self.arg(3))).lower()

class GT (Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Instrukce vyhodnotí relační operátor mezi ⟨symb 1 ⟩ a ⟨symb 2 ⟩ (stejného typu; int, bool nebo string) a do ⟨var⟩ zapíše výsledek typu bool (false při neplatnosti nebo true v případě platnosti odpovídající relace). Řetězce jsou porovnávány lexikograficky a false je menší než true. Pro výpočet neostrých nerovností lze použít AND/OR/NOT. S operandem typu nil (další zdrojový operand je libovolného typu) lze porovnávat pouze instrukcí EQ, jinak chyba 53"""
        table[self.arg(1).var()] = "bool@"+ str(self.arg(3).lt(self.arg(2))).lower()

class EQ (Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Instrukce vyhodnotí relační operátor mezi ⟨symb 1 ⟩ a ⟨symb 2 ⟩ (stejného typu; int, bool nebo string) a do ⟨var⟩ zapíše výsledek typu bool (false při neplatnosti nebo true v případě platnosti odpovídající relace). Řetězce jsou porovnávány lexikograficky a false je menší než true. Pro výpočet neostrých nerovností lze použít AND/OR/NOT. S operandem typu nil (další zdrojový operand je libovolného typu) lze porovnávat pouze instrukcí EQ, jinak chyba 53"""
        table[self.arg(1).var()] = "bool@"+ str(self.arg(1).eq(self.arg(2) )).lower()

class AND(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Aplikuje konjunkci (logické A)/disjunkci (logické NEBO) na operandy typu bool ⟨symb 1 ⟩ a ⟨symb 2 ⟩ nebo negaci na ⟨symb 1 ⟩ (NOT má pouze 2 operandy) a výsledek typu bool zapíše do ⟨var⟩."""
        table[self.arg(1).var()] = "bool@"+ str(self.arg(2).bool() and self.arg(3).bool()).lower()

class OR (Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Aplikuje konjunkci (logické A)/disjunkci (logické NEBO) na operandy typu bool ⟨symb 1 ⟩ a ⟨symb 2 ⟩ nebo negaci na ⟨symb 1 ⟩ (NOT má pouze 2 operandy) a výsledek typu bool zapíše do ⟨var⟩."""
        table[self.arg(1).var()] = "bool@"+ str(self.arg(2).bool() and self.arg(3).bool()).lower()

class NOT(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Aplikuje konjunkci (logické A)/disjunkci (logické NEBO) na operandy typu bool ⟨symb 1 ⟩ a ⟨symb 2 ⟩ nebo negaci na ⟨symb 1 ⟩ (NOT má pouze 2 operandy) a výsledek typu bool zapíše do ⟨var⟩."""
        table[self.arg(1).var()] = "bool@"+ str(not self.arg(2).bool()).lower()

class INT2CHAR (Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """Číselná hodnota ⟨symb⟩ je dle Unicode převedena na znak, který tvoří jednoznakový řetězec přiřazený do ⟨var⟩. Není-li ⟨symb⟩ validní ordinální hodnota znaku v Unicode (viz funkce chr v Python 3), dojde k chybě 58. """
        table[self.arg(1).var()] = "string@" + chr(self.arg(2).int())

class CHAR2INT (Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """Číselná hodnota ⟨symb⟩ je dle Unicode převedena na znak, který tvoří jednoznakový řetězec přiřazený do ⟨var⟩. Není-li ⟨symb⟩ validní ordinální hodnota znaku v Unicode (viz funkce chr v Python 3), dojde k chybě 58. """
        table[self.arg(1).var()] = "int@" + str(ord(table[self.arg(2)][self.arg(3)]))


class READ(Instruction):
    def __init__ (self, data): super().__init__(data)

    def exe(self):
        """Načte jednu hodnotu dle zadaného typu ⟨type⟩ ∈ {int, string, bool} a uloží tuto hodnotu do proměnné ⟨var⟩. Načtení proveďte vestavěnou funkcí input() (či analogickou) jazyka Python 3, pak proveďte konverzi na specifikovaný typ ⟨type⟩. Při převodu vstupu na typ bool nezáleží na velikosti písmen a řetězec true“ se převádí na bool@true, vše ostatní na bool@false. V případě chybného nebo chybějícího vstupu bude do proměnné ⟨var⟩ uložena hodnota nil@nil"""
        typ = self.arg(2).type()
        val = "nil@nil"

        try:
            data = input(typ + ": ")
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

        table[self.arg(1).var()] = val

class WRITE(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Vypíše hodnotu ⟨symb⟩ na standardní výstup. Až na typ bool a hodnotu nil@nil je formát výpisu kompatibilní s příkazem print jazyka Python 3 s doplňujícím parametrem end='' (za-mezí dodatečnému odřádkování). Pravdivostní hodnota se vypíše jako true a nepravda jako false. Hodnota nil@nil se vypíše jako prázdný řetězec """
        print( self.arg(1).symbol(), end="")

        
class CONCAT(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Do proměnné ⟨var⟩ uloží řetězec vzniklý konkatenací dvou řetězcových operandů ⟨symb 1 ⟩ a ⟨symb 2 ⟩ (jiné typy nejsou povoleny). """
        table[self.arg(1).var()] = "string@" + str(self.arg(2).string()) + str(self.arg(3).string())

class STRLEN(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ coment """
        table[self.arg(1).var()] = len(str(self.arg(2).string()))


class GETCHAR(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Do ⟨var⟩ uloží řetězec z jednoho znaku v řetězci ⟨symb 1 ⟩ na pozici ⟨symb 2 ⟩ (indexováno celým číslem od nuly). Indexace mimo daný řetězec vede na chybu 58."""
        try:
            table[self.arg(1).var()] = self.arg(2).string()[self.arg(3).int()]
        except Exception as e:
            err("Indexace mimo daný řetězec vede na chybu", 58)

class SETCHAR(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Zmodifikuje znak řetězce uloženého v proměnné ⟨var⟩ na pozici ⟨symb 1 ⟩ (indexováno celočíselně od nuly) na znak v řetězci ⟨symb 2 ⟩ (první znak, pokud obsahuje ⟨symb 2 ⟩ více znaků). Výsledný řetězec je opět uložen do ⟨var⟩. Při indexaci mimo řetězec ⟨var⟩ nebo v případě prázdného řetězce v ⟨symb 2 ⟩ dojde k chybě 58. """
        try:
            # variable[ arg1 ] = arg2
            tomod = table[self.arg(1).var()] 
            table[self.arg(1).var()] = tomod[self.arg(2)] = self.arg(3).string()[0] 
        except Exception as e:
            err("Indexace mimo daný řetězec vede na chybu", 58)

class TYPE(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """Dynamicky zjistí typ symbolu ⟨symb⟩ a do ⟨var⟩ zapíše řetězec značící tento typ (int, bool, string nebo nil). Je-li ⟨symb⟩ neinicializovaná proměnná, označí její typ prázdným řetězcem."""
        table[self.arg(1).var()] = self.arg(2).type()


class LABEL(Instruction):
    """ Speciální instrukce označující pomocí návěští ⟨label⟩ důležitou pozici v kódu jako potenciální cíl libovolné skokové instrukce. Pokus o vytvoření dvou stejně pojmenovaných návěští na různých místech programu je chybou 52. """
    def __init__ (self, data): 
        super().__init__(data)
        lable= self.arg(1).label()
        if lable in table.Labels:
            err(f"lable: {lable} already exists", 52)
        table.Labels[ lable ] = table.Line

    def exe(self):
        pass
    

class JUMP(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ Provede nepodmíněný skok na zadané návěští ⟨label⟩. """
        self.jump(self.arg(1).label())


class JUMPIFEQ(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """Pokud jsou ⟨symb 1 ⟩ a ⟨symb 2 ⟩ stejného typu nebo je některý operand nil (jinak chyba 53) a zároveň se jejich hodnoty rovnají, tak provede skok na návěští ⟨label⟩."""
        if ( self.arg(2).eq(self.arg(3)) ): self.jump( self.arg(1).label() )
        
class JUMPIFNEQ(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """Pokud jsou ⟨symb 1 ⟩ a ⟨symb 2 ⟩ stejného typu nebo je některý operand nil (jinak chyba 53) a zároveň se jejich hodnoty rovnají, tak provede skok na návěští ⟨label⟩."""
        if ( not self.arg(2).eq(self.arg(3)) ): self.jump( self.arg(1).label() )


class EXIT (Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """ coment """
        code = self.arg(1).int()
        if not 0 < code < 50: err("Nevalidní celočíselná hodnota {code} vede na chybu", 57)
        table.Line = len(table.Prog) ## jump to end easyest solution ever god a im smart


class DPRINT(Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """Předpokládá se, že vypíše zadanou hodnotu ⟨symb⟩ na standardní chybový výstup (stderr)."""
        sys.stderr.write( str(self.arg(1)) )


class BREAK (Instruction):
    def __init__ (self, data): super().__init__(data)
    def exe(self):
        """Předpokládá se, že na standardní chybový výstup (stderr) vypíše stav interpretu (např. pozice v kódu, obsah rámců, počet vykonaných instrukcí) v danou chvíli (tj. během vykonávání této instrukce)."""
        sys.stderr.write( str(table) )

        


# fuckn helll this shit is so not optimal it hurts
def get(op, data):
    try:
        if   op == "MOVE":
            return MOVE(data)
        elif op == "LABEL":
            return LABEL(data)
        elif op == "CREATEFRAME":
            return  CREATEFRAME(data)
        elif op == "PUSHFRAME":
            return  PUSHFRAME(data)
        elif op == "POPFRAME":
            return  POPFRAME(data)
        elif op == "DEFVAR":
            return  DEFVAR(data)
        elif op == "CALL":
            return  CALL(data)
        elif op == "RETURN":
            return  RETURN(data)
        elif op == "PUSHS":
            return  PUSHS(data)
        elif op == "POPS":
            return  POPS(data)
        elif op == "ADD":
            return  ADD(data)
        elif op == "SUB":
            return  SUB(data)
        elif op == "MUL":
            return  MUL(data)
        elif op == "IDIV":
            return  IDIV(data)
        elif op == "LT":
            return  LT(data)
        elif op == "GT":
            return  GT(data)
        elif op == "EQ":
            return  EQ(data)
        elif op == "AND":
            return  AND(data)
        elif op == "OR":
            return  OR(data)
        elif op == "NOT":
            return  NOT(data)
        elif op == "INT2CHAR":
            return  INT2CHAR(data)
        elif op == "STRI2INT":
            return  STRI2INT(data)
        elif op == "READ":
            return  READ(data)
        elif op == "WRITE":
            return  WRITE(data)
        elif op == "CONCAT":
            return  CONCAT(data)
        elif op == "STRLEN":
            return  STRLEN(data)
        elif op == "GETCHAR":
            return  GETCHAR(data)
        elif op == "SETCHAR":
            return  SETCHAR(data)
        elif op == "TYPE":
            return  TYPE(data)
        elif op == "JUMP":
            return  JUMP(data)
        elif op == "JUMPIFEQ":
            return  JUMPIFEQ (data)
        elif op == "JUMPIFNEQ":
            return  JUMPIFNEQ (data)
        elif op == "EXIT":
            return  EXIT (data)
        elif op == "DPRINT":
            return  DPRINT (data)
        elif op == "BREAK":
            return  BREAK (data)
    except Exception as e:
        return Instruction(data)


table = Table()


xml = ET.parse("example.xml")
if not xml: err("no file", 1)

program = xml.getroot()
if program.tag != "program" :
    err("root is to be \"program\"", 0)

order = 0
maxim = 0
for data in program :
    order =  int (data.attrib["order"])
    table.Line = order
    if (maxim < order): maxim = order

    if order in table.Prog:
        err(" unclear order", 1)

    
    opcode =  data.attrib["opcode"]
    table.Prog[order] = get(opcode, data)

# check if no numbers are minssing
if order != len(table.Prog):
    err("program mised a step")


table = Table()
i = 0
while (table.Line< len(table.Prog)):

    inst = table.Prog[table.Line]

    inst.exe()

    #print(inst)
    #print(table)

    #i+=1
    #if(i == 20): exit(1)

    
# end while loop
    table.Line += 1






