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
Lexer class performs exactly, as lexical analysis in compilers. Lexer takes input from standard input by line. All redundant spaces are removed from the line, and the line is splitted into tokens by `explode()` where the delimter is exactly one space, after that, tokens are saved into token buffer. Token is representation of one literal of IPPcode19 source code. Lexer class has attributes:
* `token` - represents current loaded token
* `buffer` - represents array of tokens on exactly one line
* `filePointer` - represents place, from where the input is taken (STDIN)

And methods:
* `get_token()` - loads token from `buffer` into `token` attribute
* `get_line_break()` - loads line and splits into tokens to `buffer`
* `check_comments()` - removes all comments from `buffer`
* `get_line_len()` - returns the number of tokens in `buffer`
* `check_var()` - checks if the current loaded token represents `<var>` nonterminal from specification, using regular expressions
* `check_symb()` - checks if the current loaded token represents `<symb>` nonterminal from specification, using regular expressions
* `check_label()` - checks if the current loaded token represents `<label>` nonterminal from specification, using regular expressions
* `check_type()` - checks if the current loaded token represents `<type>` nonterminal from specification, using regular expressions

### Parser description
Parser class is the heart of the script. Parser commands `Lexer` and `Stats` classes. Parser inherits from Lexer `(extends)`, so the script can work as whole. Parser at the beginning, parses the arguments. Sets up the `stats` object, to count the statistics for user. Checks and expects the IPPcode19 header. After the prepration, parser starts parsing the body of the user's IPPcode19 input. Input will be parsed, until the `token` attribute will have `EOF` flag or user's input has syntactic or lexical error. The IPPcode19 instructions, were splitted into 8 subgroups, where the instructions share the same count and types of parameters, so they can be parsed in the exactly same process, and there is no redundant code. Instruction is at first decoded by the instruction name, after that parser is sent to the proper method, to get the tokens parsed. After that, the process is repeated until `EOF` or syntactic/lexical error. After parsing, the parser will print out the XML output and the statistics numbers, if user requested to see statistics. Parser class has attributes:
* `lineCount` - holds the current line of instruction in file
* `instrCount` - holds the number of current parsed instruction
* `xml` - object to the XMLWriter library, which is used to write XML easier
* `stats` - object from the Stats class, used to hold the statistics numbers and few operations with them

And methods:
* `set_up()` - opens up the standard input and creates the XMLWriter object
* `parse_args($argv)` - function takes program arguments, and checks if they are correct
* `check_head()` - checks if the current loaded token is IPPcode19 header
* `generate_head()` - generates the XML version header and the root program element
* `parse()` - starts the parsing process by decoding the instruction and sending the parser to the correct parsing parsing instruction
* `decode()` - decodes the instruction by the current loaded token and returns the flag of the instruction based on the number and nonterminal of parameters which function takes, from `Instruction` enum class
* `parse_zero_fun()` - parses instructions with 0 parameters, checks the number of tokens in buffer, and generates the correct XML tags
* `parse_oneL_fun()` - parses instructions with 1 parameter which is nonterminal `<label>`
* `parse_oneS_fun()` - parses instructions with 1 parameter which is nonterminal `<symb>`
* `parse_oneV_fun()` - parses instructions with 1 parameter which is `<var>`
* `parse_twoVS_fun()` - parses instructions with 2 parameters which are in order `<var>` `<symb>`
* `parse_twoVT_fun()` - parses instructions with 2 parameters which are in order `<var>` `<type>`
* `parse_threeLSS_fun()` - parses instructions with 3 parameters which are in order `<label>` `<symb>` `<symb>`
* `parse_threeVSS_fun()` - parses instructions with 3 parameters which are in order `<var>` `<symb>` `<symb>`
* `check_param_num($count)` - checks if the current token instruction has $count number of parameters
* `generate_symb($choice, $number)` - method, based on the flag `varr` or `val` from class enum `Instruction` and current token, will send the correct type and number of argument to the `generate_arg()` 
* `generate_arg($number, $type)` - generates the `<argX>` element into XML, the X number is taken `$number`, the `$type` represents the type attribute in XML tag arg and element value is taken from `$token`
* `generate_eof()` - method, finishes the work with the XMLWriter object and prints out the XML file
* `generate_results()` - calls from `stats` method `print_results()` which prints the statistics numbers into file

## Stats description
Stats class encapsulates the counters of instructions, comments, labels, jumps. Meanwhile the parser is doing the parse job, in some parts of the parsing the parser will call some method from this class to add the count of some element from `stats`. Stats class has attributes:
* `file` - holds file stream where the statistics result will be printed after parsing
* `instructions` - holds the count of instructions in IPPcode19 input
* `comments` - holds the count of comments in IPPcode19 input
* `labels` - holds the count of UNIQUE labels in IPPcode19 input
* `jumps` - holds the count of jumps in IPPcode19 input
* `labelsName` - array of label names, to prevent counting of nonunique labels
* `order` - array of enums from class `Stats_flags`, order holds the elements which are requested to get printed
* `request` - bool which signifies if the --stats parameter was requested

And methods:
* `add_instr()` - add 1 to the `$instruction`
* `sub_instr()` - sub 1 from the `$instruction`
* `add_comm()` - add 1 to the `$comments`
* `add_label()` - searches the name of the label inside the `$labels` array, if the label is not found, 1 is added to the `$labels`
* `add_jump()` - add 1 to the `$jumps`
* `print_results()` - if stats were requested, method prints out the numbers based on array `$order` which holds which elements statistics user wants to know