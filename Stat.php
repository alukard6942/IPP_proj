<?php
/**
 * File: Stat.php
 * @author: xkoval18 <xkoval18@github>
 * Date: 16.03.2021
 * Last Modified Date: 21.04.2021
 */

// opttions for 
class Stats {
	
	public $flag;
	public $file;

	public function __construct(String $file, $flag){
		$this->file = $file;
		$this->flag = $this->flagtoglobal($flag);
	}

	protected function flagtoglobal($flag) {
		$flagStrip = trim($flag, "-");

		switch ($flagStrip) {
		case "loc"      :
			return "counter";
		case "comments" :
		case "labels"   :
		case "jumps"    :
		case "fwjumps"  :
		case "backjumps":
		case "badjumps" :
			return $flagStrip;
		case "stats":
			print_e("stats must take flag first", 10);
		default:
			print_e("flag: $flag does not exist", 10);
		}
	}

	public function print () {
		$file = fopen($this->file, "a");
		if (!$file)	print_e ("unable to open file: $this->file", 12);
		
		fwrite($file, $GLOBALS[$this->flag]);

		fclose($file);
	}
}
?>
