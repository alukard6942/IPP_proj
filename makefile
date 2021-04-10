
PHP=php7.4


simple:
	$(PHP) parse.php < example.ippcode21

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
	$(PHP) parse.php         || true

pack1:
	zip xkoval18.zip ./parse.php ./readme1.md ./Instruction.php ./Stat.php

clean:
	rm xkoval18.zip
	rm ./output
