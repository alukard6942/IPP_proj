<?php
/**
 * File: test.php
 * @author: alukard <alukard6942@github>
 * Date: 18.04.2021;
 * Last Modified Date: 19.04.2021
 */

ini_set("display_errors", "stderr");
# this is a tester 
# 
# tests if the output of parse.php and interpret.py are adequte
$GLOBALS["parse_php"] = "parse.php";
$GLOBALS["interpret_py"] = "interpret.py";
$GLOBALS["mode"] = "bouth";


function err($msg, $code){
	
	echo ($msg);

	if ($code != 0){
		exit($code);
	}
}

function help(){
	echo ("todo: help\n");
	exit(0);
}


function main($argc, $argv){


	# parse arguments

	$directory = "./";
	$recursive = False;


	for ($i =1; $i < $argc; $i++){
		$arg = $argv[$i];

		if ($arg == "--help"){
			help();
		}
		else if (preg_match("/^--directory=.*$/", $arg)){
			$directory = substr($arg, 12);
		}
		else if ($arg == "--recursive"){
			$recursive = True;
		}
		else if (preg_match("/^--parse-script=.*$/", $arg)){
			$GLOBALS["parse_php"] = substr(15);
		}
		else if (preg_match("/^--int-script=.*$/", $arg)){
			$GLOBALS["interpret_py"] = substr(13);
		}
		else if ($arg == "--int-only"){
			if ($GLOBALS["mode"] != "bouth"){
				err("tento parametr se nesmí kombinovat s parametry --parse-only a --parse-script)", -1);
			}
			$GLOBALS["mode"] = "interpret";
		}
		else if ($arg == "--parse-only"){
			if ($GLOBALS["mode"] != "bouth"){
				err("tento parametr se nesmí kombinovat s parametry --parse-only a --parse-script)", -1);
			}
			$GLOBALS["mode"] = "parse";
		}

		else {
			err("unsuported argm $arg", -1);
		}
	}


	$totest = array();
	if (!is_dir($directory)) {
        err("Invalid diretory path $directory\n", -1);
    }

    $files = array();
    foreach (scandir($directory) as $file) {
        if ($file !== '.' && $file !== '..' && preg_match("/.src$/", "$file")) {

			$file = substr($file ,0, -4);

			$totest[] = new source_file( "$directory/$file" );
		}
    }

	echo ("<!doctype html>\n".
			"<html lang=\"cz\">\n".
			"<head>\n".
			"\t<meta charset=\"utf-8\">\n".
			"\t<title>Test summary</title>\n".
			"</head>\n".
			"<body>\n");
	foreach ( $totest as $toprint ) {
		echo ("\t$toprint\n");
	}
	
	echo ("</body>\n" .
			"</html>");
}


class source_file {
	# src file the code itself 
	private $srcFile = "";

	#tmp files
	# output of parser so we can use xml coperator
	private $parserTMP = null;
	# diff of xlm files
	private $diffTMP = null;

	# input for interpret
	private $input = "/dev/null";

	# expected output 
	private $outFile;

	# expected exit code
	private $expectedCode = 0;
	private $exitCode;

	private $phpV    = "php7.4";
	private $pythonV = "python3.8";

	function __construct($file){
		$this->file = $file;

		if (file_exists( "$file.src" )){
			$this->srcFile = "$file.src" ;
		} 
		else {
			err("src file $file not found", -1);
		}

		if (file_exists( "$file.in" )){
			$this->input = "$file.in";
		}
		if (file_exists( "$file.rc" )){
			$code = file_get_contents("$file.rc");
			if ( ! is_numeric($code) ){
				err("content of .rc file must be number", -1);
			}

			$this->expectedCode = 0+$code;
		}
		if (file_exists( "$file.out" )){
			$this->outFile = "$file.out";
		}
	}

    function __destruct() {

		if ( $this->parserTMP != null ){
			exec( "rm -rf $this->parserTMP " );
			exec( "rm -rf $this->parserTMP.log " );
		}
		if ( $this->diffTMP != null ){
			exec( "rm -rf $this->diffTMP " );
		}
	}

	public function exfrmode(){
		$op = $GLOBALS["mode"];

		if ($op == "parse"){
			return $this->parse();
		}
		else if ($op == "interpret"){
			return $this->interpret();
		}
		else {
			return $this->bouth();
		}
	}

	public function parse(){
		$parser = $GLOBALS["parse_php"];

		$name = $this->tmpParse();

		exec("$this->phpV $parser < $this->srcFile > $name ",$tmp, $this->exitcode );

		# if err happend there is no need for compring files
		if ($this->exitcode != 0) {
			return False;
		}

		return $this->cmpToOutFile();
	}

	public function interpret(){
		$interpret = $GLOBALS["interpret_py"];

		$name = $this->tmpParse();

		exec("$this->pythonV $interpret --input=$this->input < $this->srcFile  > $name",$lines, $this->exitcode );

		# if err happend there is no need for compring files
		if ($this->exitcode != 0) {
			return False;
		}
		
		return $this->normaldiff();
	}

	public function bouth(){
		$parser = $GLOBALS["parse_php"];
		$interpret = $GLOBALS["interpret_py"];

		$name = $this->tmpParse();

		exec("$this->phpV $parser < $this->srcFile | $this->pythonV $interpret --input=$this->input > $name",$lines, $this->exitcode);

		# if err happend there is no need for compring files
		if ($this->exitcode != 0) {
			return False;
		}

		return $this->normaldiff();
	}

	private function normaldiff() {
		$diff = $this->tmpDiff();
		exec("diff $this->parserTMP $this->output", $diff, $exitcode);

		if ($exitcode == 1){
			return True;
		} else {
			return False;
		}
	}

	private function cmpToOutFile() {
		$diff = $this->tmpDiff();
		exec("java -jar /pub/courses/ipp/jexamxml/jexamxml.jar $this->parserTMP $this->outFile $diff /pub/courses/ipp/jexamxml/options",$tmp, $exitcode);

		if ($exitcode == 1){
			return True;
		} else {
			return False;
		}
	}

	private function tmpDiff() {
		$filenam = "tmpDiffn";
		$number  = 1;

		if ($this->diffTMP != null ){
			return $outFile;
		}

		for (; $number < 100 ;$number++){
			$name = "$filenam$number.tmp";
			if ( ! file_exists("$name")) {
				$this->diffTMP = $name;
				return $name;
			}
		}
		err("interner err: unenable to create tmpfile", -1);
	}

	private function tmpParse() {
		$filenam = "tmpFilen";
		$number  = 1;

		if ($this->parseTMP != null ){
			return $this->parserTMP;
		}

		for (; $number < 100 ;$number++){
			$name = "$filenam$number.tmp";
			if ( ! file_exists("$name")) {
				$this->parserTMP = "$name";
				return "$name";
			}
		}
		err("interner err: unenable to create tmpfile", -1);
	}

	public function __toString ( ) {

		$res = $this->exfrmode();

		# if didnt compiled corectly just ceck if we used the right code
		if (!$res) {
			if ($this->exitcode == $this->expectedCode){
				return "<p> <h2> $this->file:</h2> <b> OK </b></p>";
			} else {
				return "<p> <h2> $this->file:</h2> <b> WRONG CODE</b> \n" .
					"\t\treturned $this->exitcode\n\t\texpected $this->expectedCode</p>";
			}


		}

		$diff = file_get_contents("$this->diffTMP");

		return "<p> <h2> $this->file:</h2> <b> WRONG OUTPUT</b>\n\t\tdiff:\n" .
				"\t\t$diff </p>";
	}
};

main($argc, $argv)

?>
