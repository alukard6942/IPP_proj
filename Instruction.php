<?php
/**
 * File: Instruction.php
 * @author: alukard <alukard@github>
 * Date: 16.03.2021
 */

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
	    $argum = explode("@", $argum);
	    $argum = strtoupper($argum[0]) . "@" . $argum[1];

		if (!preg_match("/^[LTG]F@[\-\%\?\*\!\&a-zA-Z_$][\-\%\?\*\!\&a-zA-Z_$0-9]*$/", $argum)){
			print_e("variable name $argum not allowed", 23);
		}
		$this->print("var", $argum);
	}
	
	// can mean symbol or var
	public function print_symb(){
		$argum = $this->arg();
	    $type = strtoupper(explode("@", $argum)[0]);

		// symb in [] // var
		foreach(array("LF", "TF", "GF") as &$value){
			if ($type != $value) continue;

			$this->print_var();
			return;
		}

		$argum = substr($argum, strlen($type)+1);
		// symb in [] // symb

		switch (strtolower($type)){
		case "string":
			$argum = $this->stringcheck($argum);
			break;
		case "bool":
			$argum = strtolower($argum);
			if ($argum != "true" && $argum != "false"){
				print_e("wrong arg: $argum bool can be only true or false", 23);
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
			print_e("unsuported type $type",23);
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
?>
