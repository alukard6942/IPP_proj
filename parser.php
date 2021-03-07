<?php
/**
 * File: parser.php
 * @author: alukard <alukard@github>
 * Date: 24.02.2021
 */
ini_set("display_errors", "stderr");

$GLOBALS["stats_file"]      = null;
$GLOBALS["stats_file_used"] = array();
$GLOBALS["stats_file_t"]    = null;
$GLOBALS["lock"]     = 0;
$GLOBALS["comments"] = 0;
$GLOBALS["labels"]   = array();
$GLOBALS["jumps"]    = 0;
$GLOBALS["fwjumps"]  = 0;
$GLOBALS["backjumps"]= 0;
$GLOBALS["badjumps"] = array();

$GLOBALS["counter"]  = 0;
$GLOBALS["line_n"]   = 0;
$GLOBALS["line_str"] = "\n";



// getopts
function usage (){
	echo ("Usage: php parser.php [options]\n");
}

function help (){
	usage();
	echo "options:\n" .
	"\t --help         \t prints this help\n" .
	"\t --stats=FILE   \t set file to output statiscic\n" .
	"\t --loc          \t koli instruci se provedlo\n" .
	"\t --comments     \t koli bylo komentaru\n" .
	"\t --labels       \t pocet definovanych navesti\n" .
	"\t --jumps        \t pocet vsech instruci pro skoky\n" .
	"\t                \t  (souhrnně podmíněné/nepodmíněné skoky, volání a návraty z volání)\n" .
	"\t --fwjumps      \t pocet skoku dopredu\n" .
	"\t --backjumps    \t pocet skoku dozadu\n" .
	"\t --badjumps     \t \n";
}

function print_e( $err, $code = 0 ){

	$line_n = $GLOBALS["line_n"];
	$line_str = $GLOBALS["line_str"];
	fwrite(STDERR, "ERROR line: $line_n\t$line_str");
	fwrite(STDERR, "\t$err\n");

	if ($code) exit($code);
}

$longopts  = array(
	"stats",
	"loc",
	"comments",
	"labels",
	"jumps",
	"fwjumps",
	"backjumps",
	"badjumps",
);

foreach (array_diff($argv,[$argv[0]]) as $key){
	if ($key == "--help" || $key == "-h"){
	    help ();
	    exit(0);
	}

	$err = true;
	foreach ($longopts as $op=> $v){
		if ( substr($key, 2, strlen($v)) == $v ){
			$err = false;
			break;
		}
	}
	if ($err) {
		usage();
		print_e("invalid option $key", 10);
	}
}



class Instruction {

	public $instruction;

	private $arg_c = 1;
	private $args;

	public function __construct(String $line){
    	$this->args = preg_split('/\s+/', $line, -1, PREG_SPLIT_NO_EMPTY);
    	$this->instruction= strtoupper($this->args[0]);
	}

	static function stringcheck($string){

		$out = "";
		$len = strlen($string);

		for($i = 0; $i < $len;  $i++){
			switch($string[$i]){
			case "<":
				$out .= "&lt;";
				break;
			case ">":
				$out .= "&gt;";
				break;
			case "&":
				$out .= "&amp;";
				break;
			case "\"":
				$out .= "&quot;";
				break;
			case "\'":
				$out .= "&apos;";
				break;
			case "\\":
				if ( $i+4 > $len || !preg_match("/^[0-9][0-9][0-9]$/", substr($string, $i+1, 3)) ) {
					print_e("escape sequence must be in format \xyz", 23);
				}
			default:
				$out .= $string[$i];
			}
		}

		return $out;
	}

	private function arg(){
		if ($this->arg_c>= count($this->args)){
			print_e("instruction $this->instruction requre diferent number of arg", 20);
		}
		return $this->args[$this->arg_c];
	}

	private function print(String $type, String $var){
	    printf ("\t\t<arg%d type=\"%s\">%s</arg%d>\n", $this->arg_c, $type, $var, $this->arg_c);
		$this->arg_c++;
	}

	public function print_head(){
    	printf("\t<instruction order=\"%s\" opcode=\"%s\">\n", $GLOBALS["counter"], $this->instruction);
	}

	public function print_var(){

		$argum = $this->arg();

		if (!preg_match("/^[LTG]F@[\-\%\?\*\!\&a-zA-Z_$][\-\%\?\*\!\&a-zA-Z_$0-9]*$/", $argum)){
			print_e("variable name $argum not allowed", 23);
		}
		$this->print("var", $argum);
	}
	
	// can mean symbol or var
	public function print_symb(){
		$argum = $this->arg();
	    $type = explode("@", $argum)[0];

		// symb in [] // var
		foreach(array("LF", "TF", "GF") as &$value){
			if ($type != $value) continue;

			$this->print_var();
			return;
		}

		$argum = substr($argum, strlen($type)+1);
		// symb in [] // symb

		switch ($type){
		case "string":
			$argum = $this->stringcheck($argum);
			break;
		case "bool":
			$argum = strtolower($argum);
			if ($argum != "true" || $argum != "false"){
				print_e("bool can be only true or false", 23);
			}
			break;
		case "int":
			if (!is_numeric($argum)){
				print_e("int has to be a number", 23);
			}
			break;
		case "nil":
			#$argum = strtolower($argum);
			if ($argum != "nil"){
				print_e("nil can be only nil", 23);
			}
			break;
		case "label":
		case "type":
		case "var":
			break;
		default:
			print_e("unsuported type $value",23);
		}

		$this->print($type, $argum );
	}
	
	public function print_type(){
		$this->print("type", $this->arg());
	}
	
	public function print_label(){
		$label = $this->arg();
		$this->print("label", $label);

		if ($this->instruction == "LABEL"){

			// label nesmi byt definovan vicekat
			if (in_array($label, $GLOBALS["labels"])){
				print_e("labels can be define only onece. label: $label is already defined", 52);
			}

			array_push($GLOBALS["labels"], $label); 

			// label exist => not a bad jump, can have multiple inst
			foreach( $GLOBALS["badjumps"] as $key => $val){
				if ($val == $label){
					$GLOBALS["fwjumps"]++;
					unset($GLOBALS["badjumps"][$key]);
				}
			}
			return;
		}

		// already defined => back jump
		if (in_array($label, $GLOBALS["labels"])){
			$GLOBALS["backjumps"]++;
		} else {
			array_push($GLOBALS["badjumps"], $label);
		}
	}

	// checks if is final argument
	public function end_print(){
		if ( $this->arg_c != count($this->args) ){
			$counter = $GLOBALS["counter"];
			print_e("wrong number of arguments", 23);
		}

		$GLOBALS["counter"]++;
	}
}

# ==========================
# 	main
# ==========================

//header
echo ("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<program language=\"IPPcode21\">\n");

//body
while($line = fgets(STDIN)){
	$GLOBALS["line_n"]++;
	$GLOBALS["line_str"] = $line;

	// trim unimportant noise
   	$line = trim($line, "\n");
    for($i = 0; $i < strlen($line); $i++){
		if ($line[$i] == '#'){
			// delete comment
		    $line = substr($line, 0, $i);

			// count num of comment
			$GLOBALS["comments"]++;
		}
    }
    if ( $line == "") continue;

    // check corrent header
    if ($counter == 0) {
		if ( preg_match("/^.IPPCODE21\s*/", strtoupper($line))){
	    	$counter++;
	    	continue;
		}
		else print_e ("missing header: .IPPcode21", 21);
    }


	// create instruction
	$inst = new Instruction($line);
	$inst->print_head();

    switch($inst->instruction){ // count of arg_ 
	case "RETURN": case "BREAK":
		$GLOBALS["jumps"]++;
    case "CREATEFRAME": case "PUSHFRAME": case "POPFRAME":
		$inst->end_print();
		break;
    case "DEFVAR": case "POPS":
		$inst->print_var();
		$inst->end_print();
		break;
	case "CALL": case "JUMP":
		$GLOBALS["jumps"]++;
	case "LABEL":
		$inst->print_label();
		$inst->end_print();
		break;
    case "PUSHS": case "WRITE": case "EXIT": case "DPRINT":
		$inst->print_symb();
		$inst->end_print();
		break;
    case "MOVE": case "INT2CHAR": case "STRLEN": case "TYPE": case "NOT": 
		$inst->print_var();
		$inst->print_symb();
		$inst->end_print();
		break;
    case "READ":
		$inst->print_var();
		$inst->print_type();
		$inst->end_print();
		break;
    case "ADD": case "SUB": case "MUL": case "IDIV": case "LT": case "EQ": case "GT": case "AND":
	case "OR": case "STRI2INT": case "CONCAT": case "GETCHAR": case "SETCHAR":
		$inst->print_var();
		$inst->print_symb();
		$inst->print_symb();
		$inst->end_print();
		break;
    case "JUMPIFEQ": case "JUMPIFNEQ":
		$GLOBALS["jumps"]++;
		$inst->print_label();
		$inst->print_symb();
		$inst->print_symb();
		$inst->end_print();
		break;
	default:
		print_e("instruction $inst->instruction does not exist", 22);
    }
	
	// end of instruction
	echo "\t</instruction>\n";
}
// footer
echo "</program>\n";


function print_stats($line){
	if (!$GLOBALS["stats_file"] || in_array($GLOBALS["stats_file"], $GLOBALS["stats_file_used"])){
		print_e ("file not set or repeats itself", 10);
	}

	$file = fopen($GLOBALS["stats_file"], "a");
	if (!$file){
		$file = $GLOBALS["stats_file"];
		print_e ("unable to open file: $file", 12);
	}

	fwrite($file, $line);
	fclose($file);
	array_push($GLOBALS["stats_file_used"], $GLOBALS["stats_file"]);
	$GLOBALS["stats_file"] = null;
}

foreach (array_diff($argv,[$argv[0]]) as $key){
	if (substr($key, 0, 8) == "--stats="){
		$val = substr($key, 8);

		if ( is_null($val) ){
			print_e( "stats take argument file", 10);
		}

		$GLOBALS["stats_file"] = $val;
		continue;
	} 

	if ($key == "--loc"){
		$count = $GLOBALS["counter"]-1;
		print_stats("$count\n");
	}
	else if ($key == "--comments"){
		$count = $GLOBALS["comments"];
		print_stats("$count\n");
	}
	else if ($key == "--labels"){
		$count = count($GLOBALS["labels"]);
		print_stats("$count\n");
	}
	else if ($key == "--jumps"){ // totdo return 
		$count = $GLOBALS["jumps"];
		print_stats("$count\n");
	}
	else if ($key == "--fwjumps"){
		$count = $GLOBALS["fwjumps"];
		print_stats("$count\n");
	}
	else if ($key == "--backjumps"){
		$count = $GLOBALS["backjumps"];
		print_stats("$count\n");
	}
	else if ($key == "--badjumps"){
		$count = count($GLOBALS["badjumps"]);
		print_stats("$count\n");
	}

	else {
		usage();
		print_e("$key is invalid arg for --stats", 10);
	}
}

?>
