
PHP=php7.4
PYTHON=python3


interpreter: interpreter.py

	cat complex.ippcode21 | $(PHP) parse.php | $(PYTHON) interpreter.py --input=input.txt

simple:
	$(PYTHON) interpreter.py --source=example.xml --input=input.txt

example.xml: complex.ippcode21 parse.php
	$(PHP) parse.php < ./complex.ippcode21 > example.xml

test1:
	python3 ./tester.py $(PHP) ./parse.php ./tests

help:
	$(PHP) parse.php --help

stats:
	$(PHP) parse.php < example.ippcode21 --stats=loc.txt --loc --stats=comments.txt --comments --stats=labels.txt --labels --stats=jumps.txt --jumps  --stats=fwjumps.txt --fwjumps --stats=backjumps.txt --backjumps --stats=badjumps.txt --badjumps >/dev/null
	cat *.txt
	rm *txt

errrs:
	$(PHP) parse.php --loc   || true
	$(PHP) parse.php --stats || true
	$(PHP) parse.php --jkjl  || true
	$(PYTHON) interpreter.py --input=input.txt --source=example.xml || true
	$(PYTHON) interpreter.py || true

pack1:
	zip xkoval18.zip ./parse.php ./readme1.md ./Instruction.php ./Stat.php

clean:
	rm -rf xkoval18.zip
	rm -rf ./output
	rm -rf example.xml
