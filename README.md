# IPP Project parser tests


## How to run
`tester.py` can be placed anywhere

`python3 tester.py <php exec> <path_to_parser> <path_to_tests>`
### Example
`python3 tester.py php7.3 ipp_project/parse.php ipp_tests/tests/`

### PHP Output
Script generates `output` file which contains PHP output

## Adding new tests
In tests directory each test is placed in directory by its expected return code
