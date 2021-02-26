```
Implementační dokumentace k 1. úloze do IPP 2020/2021
Jméno a příjmení: Milan Koval
Login: xkoval18
```

# Parser.php
> aplikace v php pro prevod codu IPPcode21 na jeho reprezentaci v xml

# Pouziti
> kazda nova moznost musi myt definovany soubor kam se ma vypsat pomoci --stats=FILE,
> soubory se nesmi opakovat

	Usage: php parser.php [options]
	options:
		 --help         	 prints this help
		 --stats=FILE   	 set file to output statiscic
		 --loc          	 koli instruci se provedlo
		 --comments     	 koli bylo komentaru
		 --labels       	 pocet definovanych navesti
		 --jumps        	 pocet vsech instruci pro skoky
		                	  (souhrnně podmíněné/nepodmíněné skoky, volání a návraty z volání)
		 --fwjumps      	 pocet skoku dopredu
		 --backjumps    	 pocet skoku dozadu
		 --badjumps     	 

# Chybove kody
* 10 - chybějící parametr skriptu (je-li třeba) nebo použití zakázané kombinace parametrů;
* 11 - chyba při otevírání vstupních souborů (např. neexistence, nedostatečné oprávnění);
* 12 - chyba při otevření výstupních souborů pro zápis (např. nedostatečné oprávnění, chyba při zápisu);
* 20 – 69 - návratové kódy chyb specifických pro jednotlivé skripty;
* 99 - interní chyba (neovlivněná vstupními soubory či parametry příkazové řádky; např. chyba alokace paměti).
* 21 - chybná nebo chybějící hlavička ve zdrojovém kódu zapsaném v IPPcode21;
* 22 - neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode21;
* 23 - jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode21.
