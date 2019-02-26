## Documentation of Project Implementation for IPP 2018/2019 </br> Name and surname: Tomáš Sasák </br> Login: xsasak01

### Functionality description
`parse.php` is implemented using object oriented programming. There are few classes implemented, which communicates together to achieve the main goal, to parse IPPcode19 language into XML representation. List of implemented classes:
* `Instruction` - Abstract class used for enumeration
* `Lexer` - Lexical analyser
* `Parser` - Syntactic analyser and heart of parser
* `Stats` - Statistics counter and operator with them
* `Stats_flags` - Abstract class used for enumeration of requested stats

IPPcode19 input is taken from standard input (STDIN) and parsed XML output is printed out on standard output (STDOUT).

### Lexer description
Lexer class performs exactly, as lexical analysis in compilers. Lexer takes input from standard input by line. All redundant spaces are removed from the line, and the line is splitted into tokens by `explode()` where the delimter is exactly one space, after that, tokens are saved into token buffer. Token is representation of one literal of IPPcode19 source code. 

### Parser description
Parser class is the heart of the script. Parser commands `Lexer` and `Stats` classes. Parser inherits from Lexer `(extends)`, so the script can work as whole. Parser at the beginning, parses the arguments. Sets up the `stats` object, to count the statistics for user. Checks and expects the IPPcode19 header. After the prepration, parser starts parsing the body of the user's IPPcode19 input. Input will be parsed, until the `token` attribute will have `EOF` flag or user's input has syntactic or lexical error. The IPPcode19 instructions, were splitted into 8 subgroups, where the instructions share the same count and types of parameters, so they can be parsed in the exactly same process, and there is no redundant code. Instruction is at first decoded by the instruction name, after that parser is sent to the proper method, to get the tokens parsed. After that, the process is repeated until `EOF` or syntactic/lexical error. After parsing, the parser will print out the XML output and the statistics numbers, if user requested to see statistics.

### Stats description
Stats class encapsulates the counters of instructions, comments, labels, jumps. Meanwhile the parser is doing the parse job, in some parts of the parsing the parser will call some method from this class to add the count of some element from `stats`.