Grading
-------
Activate Virtualenv:
#Using the bash shell
source /storage-home/k/ksl3/School/comp412/default-env/bin/activate

Tests:
------
python tests.py -v  

Parser & Scanner:
-----------------
Parser and scanner are both in compiler.py.
You can test out the package by either running the compiler.py file or running the test cases.

Example:
````````
python compiler.py  #runs default example

#Custom loading 
#start up an interpreter 

scanner = Scanner("input bnf file")
tokenized_output  = s.execute()

parser = Parser(tokenized_output, s.bnf_file)
parse_result = parser.execute()

