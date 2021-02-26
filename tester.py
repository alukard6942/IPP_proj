#!/usr/bin/python3

import os
import sys
from subprocess import call
import shlex


def run_test(executable, parser, test):
    """Run test and return exit code"""
    return call("{} {} < {} >> output".format(executable, shlex.quote(parser), shlex.quote(test)), shell=True)


def __main__():
    test_directory = os.path.realpath(sys.argv[3])   # directory with test bundle
    arr = os.listdir(test_directory)
    parser = os.path.realpath(sys.argv[2])                        # source to parser.php
    executable = sys.argv[1]
    call("> output", shell=True)
    for ret_code in arr:
        if ret_code.isdigit():
            dest = test_directory + "/" + ret_code
            for test in os.listdir(dest):
                error_code = run_test(executable, parser, dest + "/" + test)
                if int(error_code) != int(ret_code):
                    print("{} expected {} but returns {}".format(test, ret_code, error_code))


__main__()
