<?php
/**
 * File: test.php
 * @author: alukard <alukard6942@github>
 * Date: 18.04.2021;
 * Last Modified Date: 19.04.2021
 */

# this is a tester 
# 
# tests if the output of parse.php and interpret.py are adequte

function err(String $msg, int $code){
	
	echo ($msg);

	if ($code != 0){
		exit($code);
	}
}

function main(){
	$parsef = new source_file("./tests/both/spec_example");
	
	$parsef->parse();
	
	echo ("$parsef\n");
}


class source_file {

	# src file the code itself 
	private String $srcFile;

	# output of parser so we can use xml coperator
	private String $parserOutput;

	# input for interpret
	private String $inputFile = "";

	# expected output
	private String $outFile;

	# expected exit code
	private int $expectedCode;

	private String $phpV    = "php7.4";
	private String $pythonV = "python3.7";

	function __construct($file){
		$this->file = $file;

		if (file_exists( "$file.src" )){
			$this->srcFile = "$file.src" ;
		} 
		else {
			err(".src file not found", -1);
		}

		if (file_exists( "$file.in" )){
			$this->inputFile = "--input=$file.in";
		}
		if (file_exists( "$file.rc" )){
			$code = readfile("$file.rc");
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
		echo ("destruct");
	}
	private function cmpToOutFile() {

		exec("java -jar /pub/courses/ipp/jexamxml/jexamxml.jar $sampleOut $myOut diffs.xml  /D /pub/courses/ipp/jexamxml/options",$tmp, $exitcode);
		return ($exitcode == $1);
	}


	public function parse(){
		exec("$this->phpV parse.php < $this->file.src",$lines, $this->parsedC );
		
		foreach ( $lines as $val ){
			$this->parsedS .= "$val\n";
		}	
	}

	public function interpret(){
		exec("cat $this->file.src | $this->pythonV interpret.py ",$lines, $this->interpretC );
		
		foreach ( $lines as $val ){
			$this->output .= "$val\n";
		}	
	}

	public function bouth(){

	}

	public function __toString ( ) {
		if ($this->parsedC == 0) {
			return $this->parsedS;
		} else {
			return $this->parsedC;
		}

	}
};

main()

?>
