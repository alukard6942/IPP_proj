```
 File: readme2.md
 Author: alukard <alukard6942@github>
 Date: 20.04.2021
```

# interpret.py
> aplikace v python3 pro interpretaci codu IPPcode21 v jeho xml reprezentaci 

# Pouziti
> kazda nova moznost musi myt definovany soubor kam se ma vypsat pomoci --stats=FILE,
> soubory se nesmi opakovat

	python3 interpreter.py [OPTION]

	 options:
	==========
	 --version -v    | version
	 --help -h       | show this help
	 --source=file   | vstupní soubor s XML reprezentací zdrojového kódu
	 --input=file    | soubor se vstupy pro samotnou interpretaci zadaného zdrojového kódu

# Chybove kody
* 10 - chybějící parametr skriptu (je-li třeba) nebo použití zakázané kombinace parametrů;
* 11 - chyba při otevírání vstupních souborů (např. neexistence, nedostatečné oprávnění);
* 12 - chyba při otevření výstupních souborů pro zápis (např. nedostatečné oprávnění, chyba při zápisu);
* 21 - chybná nebo chybějící hlavička ve zdrojovém kódu zapsaném v IPPcode21;
* 22 - neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode21;
* 23 - jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode21.
* 31 - chybný XML formát ve vstupním souboru (soubor není tzv. dobře formátovaný, angl.  well-formed, viz [1]);
* 32 - neočekávaná struktura XML 
* 52 - chyba při sémantických kontrolách vstupního kódu v IPPcode21 (např. použití nedefinovaného návěští, redefinice proměnné);
* 53 - špatné typy operandů;
* 54 - přístup k neexistující proměnné (rámec existuje);
* 55 - rámec neexistuje (např. čtení z prázdného zásobníku rámců);
* 56 - chybějící hodnota (v proměnné, na datovém zásobníku nebo v zásobníku volání);
* 57 - špatná hodnota operandu (např. dělení nulou, špatná návra- tová hodnota instrukce EXIT);
* 58 - chybná práce s řetězcem.
* 99 - interní chyba (neovlivněná vstupními soubory či parametry příkazové řádky; např. chyba alokace paměti).
