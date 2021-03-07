


simple:
	php parser.php < example.ippcode21

help:
	php parser.php --help

stats:
	php parser.php < example.ippcode21 --stats=loc.txt --loc --stats=comments.txt --comments --stats=labels.txt --labels --stats=jumps.txt --jumps  --stats=fwjumps.txt --fwjumps --stats=backjumps.txt --backjumps --stats=badjumps.txt --badjumps >/dev/null
	cat *.txt
	rm *txt

errrs:
	php parser.php --loc   || true
	php parser.php --stats || true
	php parser.php --jkjl  || true
	php parser.php         || true

pack1:
	zip xkoval18.zip ./parser.php ./readme1.md

clean:
	rm xkoval18.zip
