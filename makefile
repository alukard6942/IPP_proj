
PHP=php7.4


simple:
	$(PHP) parser.php < example.ippcode21

test1:
	python3 ./tester.py $(PHP) ./parser.php ./tests

help:
	$(PHP) parser.php --help

stats:
	$(PHP) parser.php < example.ippcode21 --stats=loc.txt --loc --stats=comments.txt --comments --stats=labels.txt --labels --stats=jumps.txt --jumps  --stats=fwjumps.txt --fwjumps --stats=backjumps.txt --backjumps --stats=badjumps.txt --badjumps >/dev/null
	cat *.txt
	rm *txt

errrs:
	$(PHP) parser.php --loc   || true
	$(PHP) parser.php --stats || true
	$(PHP) parser.php --jkjl  || true
	$(PHP) parser.php         || true

pack1:
	zip xkoval18.zip ./parser.php ./readme1.md

clean:
	rm xkoval18.zip
	rm ./output
