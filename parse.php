<?php
/**
 * File: parser.php
 * @author: alukard <alukard@github>
 * Date: 24.02.2021
 */
ini_set("display_errors", "stderr");

$GLOBALS["stats"]    = array();
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

include("Stat.php");
include("Instruction.php");


# ===================================================================
# 	getopts
# ===================================================================

for ($i = 1; $i< $argc; $i++){
	$key = $argv[$i];
	if ($key == "--help" || $key == "-h"){
	    help ();
	    exit(0);
	}

	else if ($key == "--stats"){
		if ($i + 2 > $argc) {
			Usage();
			print_e("stat requres file and flag", 10);
		}

		$stat = new Stats($argv[$i +1], $argv[$i +2]); // file, kindofstat
		$i +=2;
		array_push($GLOBALS["stats"], $stat);
	}

	else {
		Usage();
		exit (1);
	}
}


# ==================================================================
# 	main
# ==================================================================

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
    if ( trim($line) == "") continue;

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

    switch(strtoupper($inst->instruction)){ // count of arg_ 
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

## -------------- end of parsing --------------------


# ===================================================
#  	getopts execution
# ===================================================

foreach ($GLOBALS["stats"] as $stat ){
	$stat->print();
}

#--------------end of program------------------------
?>
