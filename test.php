<?php
/**
 * File: test.php
 * Autor: Aleš Chudárek
 * Date: 14.4.2020
 * Desc: Tests for 1. project IPP
 */

function writeErrorMessage($id, $message = ""){
    //write default message
    if ($message == ""){
        switch ($id) {
            case 10:
                fwrite(STDERR, "Wrong combination of parameters! Try --help.\n");
                break;
            case 11:
                fwrite(STDERR, "Can't find test file directory! Try --help.\n");
                break;
        }
    }
    //write modified message
    else
        fwrite(STDERR, $message);
    exit($id);
}

//tests and stores all arguments
$Arguments = new Arguments();
$Arguments->checkArguments();

//scans directories for tests
$DirectoryScanner = new DirectoryScanner();
$DirectoryScanner->scan($Arguments->directory, $Arguments->recursive);

//temporary file for storing outputs
$TmpFile = new TemporaryFile();
$TmpFile->create();

//in every directory that should be searched
foreach ($DirectoryScanner->directories as $dir)
{
    //for every test in a directory
    foreach ($DirectoryScanner->testFiles[$dir] as $test)
    {
        //full paths to tests
        $srcFile = $dir.$test['name'].'.src';
        $rcFile = $dir.$test['name'].'.rc';
        $inFile = $dir.$test['name'].'.in';
        $outFile = $dir.$test['name'].'.out';

        //names with suffixes
        $srcFileName = $test['name'] . '.src';
        $rcFileName = $test['name'] . '.rc';
        $inFileName = $test['name'] . '.in';
        $outFileName = $test['name'] . '.out';

        //intOnly argument wasn't used => use parser
        if(!$Arguments->intOnly) {
            //empty parseOutput
            unset($parseOutput);
            //php7.4 parse.php < file.src
            exec('php7.4 ' . $Arguments->parseScript . ' < ' . $srcFile, $parseOutput, $parseReturnCode);
        }
        //intOnly argument was used => skip parser
        else
        {
            //.src file is stored as parse output
            $parseOutput = explode("\n", file_get_contents($srcFile));
            $parseReturnCode = 0;
        }
        //parseOnly argument wasn't used => use interpret
        //if parsReturnCode isn't 0, parser returned error
        if(!$Arguments->parseOnly and $parseReturnCode == 0)
        {
            //TmpFile stores XML text
            $TmpFile->reset();
            $TmpFile->writeExecOutput($parseOutput);
            //empty interpretOutput
            unset($interpretOutput);
            //puthon3.8 interpret.py source=file.src/XML --input=file.in
            exec('python3.8 ' . $Arguments->intScript . ' --source=' . $TmpFile->getPath() . ' --input=' . $inFile, $interpretOutput, $interpretReturnCode);
            //TmpFile stores interpret output
            $TmpFile->reset();
            $TmpFile->writeExecOutput($interpretOutput);

            //compare interpret outputs with .rc
            if ($interpretReturnCode == file_get_contents($rcFile))
            {
                //interpret run successfully => compare output
                if ($interpretReturnCode == 0)
                {
                    //compare interpret outputs with .out
                    exec('diff ' . $TmpFile->getPath() . ' ' . $outFile, $output, $diffReturnCode);
                    //output is identical as .out => test success
                    if ($diffReturnCode == 0)
                    {
                        $DirectoryScanner->addTestResult($dir, $test['name'], $Arguments->parseOnly, $Arguments->intOnly, file_get_contents($rcFile), 0, 0, true);
                    }
                    //output is different as .out => test fail
                    else
                    {
                        $DirectoryScanner->addTestResult($dir, $test['name'], $Arguments->parseOnly, $Arguments->intOnly, file_get_contents($rcFile), 0, 1, false);
                    }
                }
                //interpret error, but same error as in .rc => test success
                else
                {
                    $DirectoryScanner->addTestResult($dir, $test['name'], $Arguments->parseOnly, $Arguments->intOnly, file_get_contents($rcFile), $interpretReturnCode, -1, true);
                }
            }
            //different returnCode from .rc => test fail
            else
            {
                $DirectoryScanner->addTestResult($dir, $test['name'], $Arguments->parseOnly, $Arguments->intOnly, file_get_contents($rcFile), $interpretReturnCode, -1, false);
            }
        }
        //parseOnly argument was used => skip interpret
        else if($Arguments->parseOnly)
        {
            //TmpFile stores XML text
            $TmpFile->reset();
            $TmpFile->writeExecOutput($parseOutput);

            //compare parser outputs with .rc
            if ($parseReturnCode == file_get_contents($rcFile))
            {
                //parser run successfully => compare output
                if ($parseReturnCode == 0)
                {
                    //compare parser outputs with .out
                    exec("java -jar " . $Arguments->jexamxml . $TmpFile->getPath() . " " . $outFile . " " . str_replace( "jexamxm.jar", "options", $Arguments->jexamxml), $a7SoftReturnCode);

                    //output is identical as .out => test success
                    if ($a7SoftReturnCode == 0)
                    {
                        $DirectoryScanner->addTestResult($dir, $test['name'], $Arguments->parseOnly, $Arguments->intOnly, file_get_contents($rcFile), 0, 0, true);
                    }
                    //output is different as .out => test fail
                    else
                    {
                        $DirectoryScanner->addTestResult($dir, $test['name'], $Arguments->parseOnly, $Arguments->intOnly, file_get_contents($rcFile), 0, 1, false);
                    }
                }
                //parser error, but same error as .rc => test success
                else
                {
                    $DirectoryScanner->addTestResult($dir, $test['name'], $Arguments->parseOnly, $Arguments->intOnly, file_get_contents($rcFile), $parseReturnCode, -1, true);
                }
            }
            //different returnCode from .rc => test fail
            else
            {
                $DirectoryScanner->addTestResult($dir, $test['name'], $Arguments->parseOnly, $Arguments->intOnly, file_get_contents($rcFile), $parseReturnCode, -1, false);
            }
        }
        //parseOnly or intOnly argument weren't used and parserReturnCode != 0
        else
        {
            //parserReturnCode is identical as .rc => test success
            if ($parseReturnCode == file_get_contents($rcFile))
            {
                $DirectoryScanner->addTestResult($dir, $test['name'], $Arguments->parseOnly, $Arguments->intOnly, file_get_contents($rcFile), $parseReturnCode, -1, true);
            }
            //parserReturnCode is different as .rc => test fail
            else
            {
                $DirectoryScanner->addTestResult($dir, $test['name'], $Arguments->parseOnly, $Arguments->intOnly, file_get_contents($rcFile), $parseReturnCode, -1, false);
            }
        }
    }
}
$TmpFile->close();

//generates HTML representation of results
$HtmlGenerator = new HtmlGenerator($DirectoryScanner);
$HtmlGenerator->generate();

class Arguments
{
    public $directory;
    public $recursive;
    public $parseScript;
    public $intScript;
    public $parseOnly;
    public $intOnly;
    public $jexamxml;

    public function __construct()
    {
        //default values
        $this->directory = getcwd().'/';
        $this->recursive = false;
        $this->parseScript = './parse.php';
        $this->intScript = './interpret.py';
        $this->parseOnly = false;
        $this->intOnly = false;
        $this->jexamxml = './pub/courses/ipp/jexamxml/jexamxml.jar';
    }

    /*
     * Checks all arguments and saves all data
     */
    function checkArguments()
    {
        global $argc;
        $argsUsed = 0;

        //all possible arguments
        $options = getopt(null, ["help", "directory:", "recursive", "parse-script:", "int-script:", "parse-only", "int-only", "jexamxml:"]);

        //if argument --help is used, program ends
        if (isset($options["help"]))
        {
            print("This program test.php tests the functionality of scripts parse.php (converts 
IPPcode2021 into XML file) and interpret.py (performs XML instructions).
This script works with these parameters:
\t--help prints help
\t--directory=path path to the directory, where all tests are (if missing, looks for test in this directory)
\t--recursive if this parameter is used, tests are executed in subdirectories also
\t--parse-script=path path to the parse script (if missing, looks for parse.php in this directory)
\t--int-script=path path to the interpret script (if missing, looks for interpret.py in this directory)
\t--parse-only if this parameter is used, only parser is tested (can't be combined with --int-only or --int-script=path)
\t--int-only if this parameter is used, only interpret is tested (can't be combined with --parse-only or --parse-script=path)
\t--jexamxml=path path to the directory, with a A7Soft JExamXML tool for comparing XML files");
            exit(0);
        }
        //no arguments
        if ($argc == 1)
        {
            if (!file_exists($this->intScript))
            {
                writeErrorMessage(10, "File " . $this->intScript . " does not exist.\n");
            }
            if (!file_exists($this->parseScript))
            {
                writeErrorMessage(10, "File " . $this->parseScript . " does not exist.\n");
            }
            if (!file_exists($this->jexamxml))
            {
                writeErrorMessage(10, "File " . $this->jexamxml . " does not exist.\n");
            }
            return;
        }
        //tests can be run with max 5 arguments
        else if ($argc >= 2 && $argc <= 6)
        {
            if (isset($options["directory"]))
            {
                $this->directory = $options['directory'];
                //checking if the specified path ends with '/'
                if (substr($this->directory, -1) != '/')
                    $this->directory = $this->directory."/";
                $argsUsed++;
                if (!file_exists($this->directory))
                    writeErrorMessage(11, "File with tests does not exist.\n");
            }
            if (isset($options["recursive"]))
            {
                $this->recursive = true;
                $argsUsed++;
            }
            if (isset($options["parse-script"]) and !isset($options["int-only"]))
            {
                $this->parseScript = $options["parse-script"];
                $argsUsed++;
            }
            if (isset($options["int-script"]) and !isset($options["parse-only"]))
            {
                $this->intScript = $options["int-script"];
                $argsUsed++;
            }
            //argument --int-only
            if (isset($options["int-only"]) and !isset($options["parse-script"]) and !isset($options["parse-only"]))
            {
                $this->intOnly = true;
                $argsUsed++;
            }
            //argument --parse-only
            if (isset($options["parse-only"]) and !isset($options["int-script"]) and !isset($options["int-script"]))
            {
                $this->parseOnly = true;
                $argsUsed++;
            }


            if (isset($options["jexamxml"]))
            {
                $this->jexamxml = $options["jexamxml"];
                if (!file_exists($this->jexamxml))
                    writeErrorMessage(10, "File " . $this->jexamxml . " does not exist.\n");
                //checking if the specified path ends with '/'
                if (substr($this->jexamxml, -1) != '/')
                    $this->jexamxml = $this->jexamxml."/";
                $argsUsed++;
            }

            //No arguments or additional arguments
            if ($argsUsed != $argc - 1)
            {
                writeErrorMessage(10, "Wrong arguments. Try --help.\n");
            }


            //test if interpret and parser can be opened
            if (!isset($options["parse-only"]) and !file_exists($this->intScript))
                writeErrorMessage(10, "File " . $this->intScript . " does not exist.\n");
            if (!isset($options["int-only"]) and !file_exists($this->parseScript))
                writeErrorMessage(10, "File " . $this->parseScript . " does not exist.\n");
        }
        else
        {
            writeErrorMessage(10, "Wrong number of arguments.\n");
        }
    }
}

/*
 * DirectoryScanner looks through directory and looks for .src files (tests)
 */
class DirectoryScanner
{
    //all directories
    public $directories;
    //saves all tests
    public $testFiles;

    public function __construct()
    {
        $this->directories = [];
        $this->testFiles = [];
    }

    /*
     * Saves paths of .src, .rc, .in, .out files and generates new if missing
     */
    public function scan($dir, $recursive)
    {
        $Directory = new RecursiveDirectoryIterator($dir);
        if ($recursive == true)
            $Iterator = new RecursiveIteratorIterator($Directory);
        else
            $Iterator = new IteratorIterator($Directory);
        $Regex = new RegexIterator($Iterator, '/^.+\.src$/i', RecursiveRegexIterator::GET_MATCH);
        foreach ($Regex as $reg)
        {
            //only name without suffix
            $fileName = $this->getFileName($reg[0]);
            //path to directory
            $dir = $this->getDirectoryPath(realpath($reg[0]));
            if (!in_array($dir, $this->directories))
                $this->directories[] = $dir;

            //if .src exist, generate rest if missing
            $this->testFiles[$dir][$fileName]['name'] = $fileName;
            if (!file_exists($dir.$fileName.'.rc'))
                $this->genFile($dir, $fileName.'.rc', "0");
            if (!file_exists($dir.$fileName.'.in'))
                $this->genFile($dir, $fileName.'.in', "");
            if (!file_exists($dir.$fileName.'.out'))
                $this->genFile($dir, $fileName.'.out', "");
        }

        //sorting
        array_multisort($this->testFiles, SORT_ASC);
        sort($this->directories);
    }

    /*
     * Saves all needed files in testFiles variable
     * var $dir directory path
     * var $fileName name of the test without suffix
     * var $parseOnly bool if --parse-only was used
     * var $intOnly bool if --int-only was used
     * var $expValue value from .rc file
     * var $retValue return value after using parser/interpret
     * var $sameOut 0 if output is identical to .out, 1 if output is different than .out, -1 if it's not needed to print
     * var $pass bool true if test is successful, false if failed
     */
    public function addTestResult($dir, $fileName, $parseOnly, $intOnly, $expValue, $retValue, $sameOut, $pass)
    {
        $this->testFiles[$dir][$fileName]['parseOnly'] = $parseOnly;
        $this->testFiles[$dir][$fileName]['intOnly'] = $intOnly;
        $this->testFiles[$dir][$fileName]['expValue'] = $expValue;
        $this->testFiles[$dir][$fileName]['retValue'] = $retValue;
        $this->testFiles[$dir][$fileName]['sameOut'] = $sameOut;
        $this->testFiles[$dir][$fileName]['pass'] = $pass;
    }

    /*
     * Generates file with content
     * var $directory path for generated file
     * var $fileName name of file with suffix
     * var $content content of generated file
     */
    private function genFile($directory, $fileName, $content)
    {
        file_put_contents($directory.$fileName, $content);
    }

    /*
     * Uses regex and returns the name of a file without suffix from path
     * var $pathToFile string containing the path of searched file
     */
    private function getFileName($pathToFile)
    {
        return preg_replace('/^(.*\/)?(.+)\.src$/','\2', $pathToFile);
    }

    /*
     * Searches for a file (.src .in .out .rc) and returns the path to the directory, where the file is
     * var $pathToFile path of the file
     */
    private function getDirectoryPath($pathToFile)
    {
        return preg_replace('/^(.*\/).+\.(in|out|rc|src)$/','\1', $pathToFile);
    }
}

/*
 * Class storing data in a temporary file
 */
class TemporaryFile
{
    private $file;

    /*
     * creates the temporary file
     */
    public function create()
    {
        $this->file = tmpfile();
    }

    /*
     * closes the temporary file
     */
    public function close()
    {
        fclose($this->file);
    }

    /*
     * resets the content of the temporary file
     */
    public function reset()
    {
        $this->close();
        $this->create();
    }

    /*
     * returns the path to the temporary file
     */
    public function getPath()
    {
        $metaData = stream_get_meta_data($this->file);
        return $metaData['uri'];
    }

    /*
     * Writes an array of strings in the temporary file
     * every object on a different line
     * var $array string array to be written
     */
    public function writeExecOutput($array)
    {
        fwrite($this->file, implode("\n", $array));
    }
}

/*
 * Class generating html output
 */
class HtmlGenerator
{
    private $DirectoryScanner;

    /*
     * init
     */
    public function __construct($DirectoryScanner)
    {
        $this->DirectoryScanner = $DirectoryScanner;
    }

    /*
     * Generates HTML and prints it to STDOUT
     */
    public function generate()
    {

        $html ='<!doctype html>
        <html lang=\"en\">
        <head>
            <meta charset=\"utf-8\">
            <title>IPPcode21 Tests</title>
            <meta name=\"Tests summary\">
            <meta name=\"Aleš Chudárek\">
            
            <style>
                h1 {
                    text-align: center;
                    color: black;
                }
                #main {
                    width: 100%;
                    margin: auto;
                }
                tr#summary{
                    background: #ccff66;
                    color: black;            
                }
                table {
                    width: 100%;
                    -webkit-box-shadow: 1px 1px 5px 0px rgba(0,0,0,0.47);
                    -moz-box-shadow: 1px 1px 5px 0px rgba(0,0,0,0.47);
                    box-shadow: 1px 1px 5px 0px rgba(0,0,0,0.47);
                    font-family: Helvetica, Arial, Helvetica, sans-serif;
                    border-collapse: collapse;
                }
                
                table td, table th {
                    padding: 8px;
                }
                
                table tbody tr {
                    //border: 2px solid white;
                }
                
                table tr:nth-child(even){background-color: #ffffe5;}
                
                table tr:hover {background-color: #ddd;}
                
                table th {
                    padding-top: 12px;
                    padding-bottom: 12px;
                    text-align: left;
                    background-color: #ffff00;
                    color: black;
                    text-align: center;
                }
                .dir-heading {
                    text-align: left;
                    padding: 5px 15px;    
                    background-color: #ffff00 !important;  
                    color: #606060;          
                }
                .background-gray{
                    background: #dcdcd9;
                }
                .bool {
                    color: #000000;
                }
                .failed {
                    color: #e50000;
                }
                .passed {
                    color: #00b500;
                }
                .center {
                    text-align: center;
                }
                .left {
                    text-align: left;
                }
                ul li {
                    display: inline;
                    float: left;
                    padding: 0 15px;
                }
                ul li div {
                    float: left;
                    margin-right: 10px !important;
                }
            </style>
        </head>

        <body>
            <div id="main">
                <pre class="left">
                    <font size = "+20">IPPcode21</font>
                </pre>
                <table class="center">
                    <thead>
                        <tr>
                            <th>No.</th>
                            <th>Test name</th>
                            <th>parse-only</th>
                            <th>int-only</th>
                            <th>Exp. value</th>
                            <th>Real return value</th>
                            <th>Identical output</th>
                            <th>Passed</th>
                        </tr>
                    </thead>
                    ';

        //number of all tests tested
        $allTestCount = 0;
        //number of all tests tested that passed
        $allTestPassedCount = 0;

        //far all directories to be searched
        foreach ($this->DirectoryScanner->directories as $dir) {
            //number of test in a directory
            $testDirCount = 0;
            //number of passed test in a directory
            $testDirPassedCount = 0;
            //html text
            $html = $html . "<tbody>\n";

            //for every test in a directory
            foreach ($this->DirectoryScanner->testFiles[$dir] as $test) {

                $html = $html . "<tr>\n";
                //test number
                $html = $html . "<td class='center'>" . ($allTestCount + 1) . "</td>\n";
                //test name
                $html = $html . "<td class='center'>" . $test['name'] . "</td>\n";

                //check if parse-only
                $html = $html . "<td class='bool'>";
                if ($test['parseOnly'])
                    $html = $html . "&#10004;</td>\n";
                else
                    $html = $html . "&#10007;</td>\n";

                //check if int-only
                $html = $html . "<td class='bool'>";
                if ($test['intOnly'])
                    $html = $html . "&#10004;</td>\n";
                else
                    $html = $html . "&#10007;</td>\n";

                //.rc expected value
                $html = $html . "<td class='center'>" . $test['expValue'] . "</td>\n";

                //real return value
                $html = $html . "<td class='center'>" . $test['retValue'] . "</td>\n";

                //comparing output only if .rc and real return value are both 0
                //print same output true
                if($test['sameOut'] == 0)
                {
                    $html = $html . "<td class='bool'>&#10004;</td>\n";
                }
                //print same output false
                else if($test['sameOut'] == 1)
                {
                    $html = $html . "<td class='bool'>&#10007;</td>\n";
                }
                //dont print same output
                else //($test['sameOut'] == -1)
                {
                    $html = $html . "<td class='center'></td>\n";
                }

                //test passed
                if($test['pass'])
                {
                    $html = $html . "<td class='passed'>&#10004;</td>\n</tr>\n\n";
                    $testDirPassedCount = $testDirPassedCount +1;
                    $testDirCount = $testDirCount +1;
                    $allTestCount = $allTestCount +1;
                    $allTestPassedCount = $allTestPassedCount +1;
                }
                //test failed
                else
                {
                    $html = $html . "<td class='failed'>&#10007;</td>\n</tr>\n\n";
                    $testDirCount = $testDirCount +1;
                    $allTestCount = $allTestCount +1;
                }
            }
            //after every directory
            $html = $html.'
<tr class="dir-heading">
    <td colspan="7" class="left">'.$dir.' &#8599;</td>
    <td class="center">'.$testDirPassedCount.'/'.$testDirCount.'</td>
</tr>';
        }

        //prints if all is OK or all is fail
        $allSucFail = "";
        if($allTestPassedCount == $allTestCount and $allTestPassedCount != 0)
            $allSucFail = "ALL SUCCEEDED";
        else if($allTestPassedCount != $allTestCount and $allTestPassedCount == 0)
            $allSucFail = "ALL FAILED";

        //Summary of all tests
        $html = $html.
'</tbody>

<tr id="summary">
            <td class="left" colspan="6">Summary</td>
            <td class="center">' . $allSucFail . '</td>
            <td class="center">' . $allTestPassedCount . '/' . $allTestCount . '</td>
        </tr>
    </tbody>
</table>
    <ul>
        <li class="passed">&#10004; PASSED</li>
        <li class="failed">&#10007; FAILED</li>
    </ul>
</div>
<script></script>
</body>
</html>';
        //prints html
        echo $html;
    }

}
