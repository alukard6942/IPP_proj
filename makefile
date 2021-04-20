
PHP=php7.4
PYTHON=python3

test: clean parse inst both

parse:
	$(PHP) test.php --directory=./tests/parse-only --parse-only > index1.html
inst:
	$(PHP) test.php --directory=./tests/int-only/ --int-only > index2.html
both:
	$(PHP) test.php --directory=./tests/both/ > index3.html

interpret: interpret.py
	cat complex.ippcode21 | $(PHP) parse.php | $(PYTHON) interpret.py --input=input.txt

simple:
	$(PYTHON) interpret.py --source=example.xml --input=input.txt

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
	$(PYTHON) interpret.py --input=input.txt --source=example.xml || true
	$(PYTHON) interpret.py || true

pack1:
	zip xkoval18.zip ./parse.php ./readme1.md ./Instruction.php ./Stat.php

clean:
	rm -rf xkoval18.zip
	rm -rf ./output
	rm -rf example.xml
	rm -rf index1.html
	rm -rf index2.html
	rm -rf index3.html
