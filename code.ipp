.ippcode21

# spaceship
# a picure-esq thing in a array flouting

Jump main

LABEL INIT
PUSHFRAME 
CREATEFRAME 
DEFVAR TF@SIDE
POPS TF@SIDE 
	
	DEFVAR TF@TMP

	LT TF@TMP TF@SIDE int@100

POPFRAME 
return


LABEL main 

CREATEFRAME 

pushs int@1
call init

