<?php
    // Abstract class used for enumeration of instructions
    abstract class Instructions
    {
        const EOF = 100;
        const EMPTY = 101;
        const zeroParams = 102;

        const oneParamV = 103;
        const oneParamL = 104;
        const oneParamS= 105;

        const twoParamVS = 106;
        const twoParamVT = 107;

        const threeParamVSS = 108;
        const threeParamLSS = 109;

        const unknownFun = 111;

        const varr = 112;
        const val = 113;
    }

    // Abstract class used for enumeration of requested stats
    abstract class Stats_flags
    {
        const instr = 200;
        const comm = 201;
        const labels = 202;
        const jumps = 203;
    }

    // Statistics class with counters and operator with them
    class Stats
    {
        // Holds file stream where the statistics result will be
        // printed after parsing
        protected $file = NULL;
        
        // These variables are holding the number of instructions
        // in IPPcode19 input (stats counters)
        protected $instructions = 0;
        protected $comments = 0;
        protected $labels = 0;
        protected $jumps = 0;

        // Array which contains label names, to prevent counting
        // of nonunique labels
        protected $labelsName = [];
        // Array which contains enums from Stats_flags, these enums
        // hold requested elements from statistics
        protected $order = [];

        // Bool which signifies if the --stats parameter was requested
        protected $request = false;

        // Method parses stats arguments and opens the $file for output
        // and adds enums to the order
        public function parse_stats($argv)
        {
            $statArgc = 2;
            $this->request = true;

            $path = preg_grep("/^--stats=.+$/", $argv);
            if(count($path) != 1)
            {
                fwrite(STDERR, "Error, unknwon parameters!\n");
                fwrite(STDERR, "\n");
                exit(10);
            }
            $path = explode("=", $path[1]);
            $path = $path[1];
            $this->file = $path;
            
            $loc = preg_grep("/^--loc$/", $argv);
            if(count($loc) == 1)
            {
                array_push($this->order, Stats_flags::instr);
                $statArgc++;
            }

            $comments = preg_grep("/^--comments$/", $argv);
            if(count($comments) == 1)
            {
                array_push($this->order, Stats_flags::comm);
                $statArgc++;
            }

            $labels = preg_grep("/^--labels$/", $argv);
            if(count($labels) == 1)
            {
                array_push($this->order, Stats_flags::labels);
                $statArgc++;
            }

            $jumps = preg_grep("/^--jumps$/", $argv);
            if(count($jumps) == 1)
            {
                array_push($this->order, Stats_flags::jumps);
                $statArgc++;
            }

            if($statArgc != count($argv))
            {
                fwrite(STDERR, "Error, expecting parameters for stats!\n");
                exit(10);
            }
        }

        // add 1 to the $instruction
        public function add_instr()
        {
            $this->instructions++;    
        }

        // sub 1 from the $instruction 
        public function sub_instr()
        {
            $this->instructions--;
        }

        // add 1 to the $comments
        public function add_comm()
        {
            $this->comments++;
        }

        // add 1 to the $labels (unique label count)
        public function add_label($buffer)
        {
            if(empty($buffer))
            {
                return;
            }
            if(!in_array($buffer[0], $this->labelsName))
            {
                array_push($this->labelsName, $buffer[0]);
                $this->labels++;
            }
        }

        // add 1 to the $jumps
        public function add_jump()
        {
            $this->jumps++;
        }

        // Method prints out results of statistics, if they 
        // were requested, method prints out the numbers based
        // on array $order
        public function print_results()
        {
            if($this->request == false)
            {
                return;
            }

            $this->file = fopen($this->file, "w");
            if($this->file == false)
            {
                fwrite(STDERR, "Error, creating the statistics file!\n");
                exit(12);
            }

            while(!empty($this->order))
            {
                $top = $this->order[0];
                array_shift($this->order);

                switch($top)
                {
                    case Stats_flags::instr:
                        fwrite($this->file, $this->instructions);
                        break;

                    case Stats_flags::comm:
                        fwrite($this->file, $this->comments);
                        break;

                    case Stats_flags::labels:
                        fwrite($this->file, $this->labels);
                        break;

                    case Stats_flags::jumps:
                        fwrite($this->file, $this->jumps);
                        break;
                }

                fwrite($this->file, "\n");
            }

            fclose($this->file);
        }
    }

    // Class represents Lexical Analyser from compilers
    class Lexer
    {
        // Represents current loaded token
        protected $token = 1;
        // Represents array of (yet unprocessed)tokens on current line
        protected $buffer = [];
        // Represents place, from which is the input taken
        protected $filePointer = "php://stdin";

        // Loads line and splits it into tokens to $buffer
        protected function get_line_break()
        {
            $this->buffer = fgets($this->filePointer);
            $this->lineCount++;

            if($this->buffer == FALSE)
            {
                $this->buffer = [];
                array_push($this->buffer, Instructions::EOF);
                return;
            }
            
            $this->buffer = trim(preg_replace("/\s+/", " ", $this->buffer));
            $this->buffer = explode(" ", $this->buffer);
            
            $this->check_comments();


            if($this->buffer[0] == NULL)
            {
                $this->buffer = [];
                array_push($this->buffer, Instructions::EMPTY);
                return;
            }

        }

        // Loads token from $buffer into $token (removes it from buffer)
        protected function get_token()
        {
            if($this->token == Instructions::EOF)
            {
                return;
            }
            
            if(empty($this->buffer) == true)
            {
                $this->get_line_break();
            }

            $this->token = $this->buffer[0];
            array_shift($this->buffer);
            

            // Empty token equals empty line
            if($this->token == Instructions::EMPTY)
            {
                $this->get_token();
            }
        }

        // Removes all comments from $buffer (useless tokens)
        protected function check_comments()
        {
            $comments = preg_grep("/#.*$/", $this->buffer);
            if(!empty($comments))
            {
                $this->stats->add_comm();
                $triggered = 0;
                $len = count($this->buffer);

                for($token = key($this->buffer); $token < $len; $token++)
                {
                    
                    if($triggered == 1)
                    {
                        unset($this->buffer[$token]);
                        continue;
                    }
                    $isThere = preg_match("/#.*$/", $this->buffer[$token]);
                    if($isThere == 1)
                    {
                        $triggered = 1;
                    }

                    $value = preg_replace("/#.*$/", "", $this->buffer[$token]);

                    if($value == "")
                    {
                        unset($this->buffer[$token]);
                        continue;
                    }
                    $this->buffer[$token] = $value;
                }

                if(empty($this->buffer))
                {
                    $this->buffer = [NULL];
                } 
            }
        }

        // Returns the number of tokens in $buffer
        protected function get_line_len()
        {
            return count($this->buffer);
        }

        // Checks if the current loaded token represents <var> nonterminal
        // from specification, using regular expressions
        protected function check_var()
        {
            $regex = "/^TF@[a-zA-Z_\-$&%*!?]{1}[a-zA-Z0-9_\-$&%*!?]*$|^LF@[a-zA-Z_\-$&%*!?]{1}[a-zA-Z0-9_\-$&%*!?]*$|^GF@[a-zA-Z_\-$&%*!?]{1}[a-zA-Z0-9_\-$&%*!?]*$/";

            $result = preg_match($regex, $this->token);

            if($result == 0 or $result == FALSE)
            {
                fwrite(STDERR, "Error, expecting <var> function parameter! Line: ");
                fwrite(STDERR, $this->lineCount);
                fwrite(STDERR, "\n");
                exit(23);
            }
        }

        // Checks if the current string has some incorrect escape sequences
        protected function check_string()
        {
            $string_regex = "/^string@.*/";
            $backslash_regex = "/\\\/";
            $escape_regex = "/\\\[0-9]{3}/";
            $test = preg_match($escape_regex, $this->token);
            $result = preg_match($string_regex, $this->token);
            // checks if token is string
            if($result)
            {
                $backslashes = preg_match_all($backslash_regex, $this->token);
                // if token has backslashes
                if($backslashes > 0)
                {
                    // get count of sequences
                    $escapes = preg_match_all($escape_regex, $this->token);
                    // if there is not same number of escapes and sequences = error
                    if($escapes != $backslashes)
                    {
                        fwrite(STDERR, "Error, wrong escape sequence!\n");
                        exit(23);
                    }
                }
            }
        }

        //Checks if the current loaded token represents <symb> nonterminal 
        // from specification, using regular expressions
        protected function check_symb()
        {
            $var_regex = "/^TF@[a-zA-Z_\-$&%*!?]{1}[a-zA-Z0-9_\-$&%*!?]*$|^LF@[a-zA-Z_\-$&%*!?]{1}[a-zA-Z0-9_\-$&%*!?]*$|^GF@[a-zA-Z_\-$&%*!?]{1}[a-zA-Z0-9_\-$&%*!?]*$/";

            $result = preg_match($var_regex, $this->token);

            if($result)
            {
                return Instructions::varr;
            }

            $val_regex = "/^int@[-+]?[0-9]+$|^bool@true$|^bool@false$|^string@.*|^nil@nil$/";

            $result = preg_match($val_regex, $this->token);

            $this->check_string();

            if($result)
            {
                return Instructions::val;
            }
            else
            {
                return false;
            }
        }

        // Checks if the current loaded token represents <label> nonterminal
        // from specification, using regular expressions
        protected function check_label()
        {
            $regex = "/^[a-zA-Z_\-$&%*!?]{1}[a-zA-Z0-9_\-$&%*!?]*$/";

            $result = preg_match($regex, $this->token);

            if($result == 0 or $result == FALSE)
            {
                fwrite(STDERR, "Error, expecting <label> function parameter! Line: ");
                fwrite(STDERR, $this->lineCount);
                fwrite(STDERR, "\n");
                exit(23);
            }            
        }

        // Checks if the current loaded token represents <type> nonterminal
        // from specification, using regular expressions
        protected function check_type()
        {
            $regex = "/^int$|^bool$|^string$/";

            $result = preg_match($regex, $this->token);

            if($result == 0 or $result == FALSE)
            {
                fwrite(STDERR, "Error, expecting <type> function parameter! Line: ");
                fwrite(STDERR, $this->lineCount);
                fwrite(STDERR, "\n");
                exit(23);
            }             
        }
    }
    
    // Syntactic analyser and heart of the script
    class Parser extends Lexer
    {
        // Holds the current line in file
        protected $lineCount = 0;
        // Holds the number of current parsed instruction
        protected $instrCount = 0;
        // Object to the XMLWriter library, which used to write XML easier
        protected $xml = NULL;
        // Object created based on Stats class, used to hold current statistics of current 
        // input
        protected $stats = NULL;

        // Opens up the standart input and creates the XMLWriter object
        public function set_up()
        {
            $this->filePointer = fopen($this->filePointer, 'r');
            $this->xml = new XMLWriter();
        }

        // Method takes program arguments, and checks if they are correct
        public function parse_args($argv)
        {
            $this->stats = new Stats();
            $argc = count($argv);

            if($argc == 1)
            {
                return;
            }
            else if($argc == 2)
            {
                if($argv[1] == "--help" or $argv[1] == "-h")
                {
                    print "IPPcode19 parser\n";
                    print "Written by Tomáš Sasák for BUT FIT 2019.\n\n";
                    print "Parser parses IPPcode19 language and translates it into XML representation.\n";
                    print "Checks syntactic analysis and lexical analysis.\n";
                    print "IPPcode19 is taken from STDIN.\n";
                    exit(0);
                }
            }
            else if(preg_grep("/^--stats=.+$/", $argv))
            {
                $this->stats->parse_stats($argv);
                return;
            }
            fwrite(STDERR, "Error, unknown parameters!\n");
            exit(10);
        }
        
        // Checks if the current loaded token is IPPcode19 header
        public function check_head()
        {
            $this->get_token();
    
            if((strcasecmp($this->token,".IPPcode19") != 0) or ($this->get_line_len() != 0))
            {
                fwrite(STDERR, "Error, expecting .IPPcode19 header! Line: ");
                fwrite(STDERR, $this->lineCount);
                fwrite(STDERR, "\n");
                exit(21);
            }
        }

        // Generates the XML version header and the root program element
        public function generate_head()
        {
            
            $this->xml->openMemory();
            $this->xml->setIndent(true);
            $this->xml->startDocument("1.0","UTF-8");
            $this->xml->startElement("program");
            $this->xml->writeAttribute("language","IPPcode19");
        }

        // Method, finishes the work with the XMLWriter object and prints out 
        // the XML output
        public function generate_eof()
        {
            $this->xml->endDocument();
            $result = $this->xml->outputMemory();
            print $result;
        }

        // Generates instruction element based on current token and 
        // instruction count
        protected function generate_instruction()
        {
            $this->xml->startElement("instruction");
            $this->xml->writeAttribute("order", $this->instrCount);
            $this->xml->writeAttribute("opcode", $this->token);
        }

        // Generates the <argX> element into XML output, the X number is taken
        // from $number parameter and $type represents the type attribute in XML tag
        // arg and element value is taken from current loaded token
        protected function generate_arg($number, $type)
        {
            $arg = "arg" . $number;

            $this->xml->startElement($arg);
            $this->xml->writeAttribute("type", $type);
            $this->xml->text($this->token);

            $this->xml->endElement();
        }

        // Method, based on the flag Instruction::var or Instruction::val from
        // and current token will send the correct type and number of argument to the
        // generate_arg()
        protected function generate_symb($choice, $number)
        {
            if($choice == false)
            {
                fwrite(STDERR, "Error, expecting <symb> function parameter! Line: ");
                fwrite(STDERR, $this->lineCount);
                fwrite(STDERR, "\n");
                exit(23);                
            }
            else if($choice == Instructions::varr)
            {
                $this->generate_arg($number, "var");
            }
            else if($choice == Instructions::val)
            {
                // Split on two parts, int@25 = int, 25, string@lol = string, lol
                $split = explode("@", $this->token, 2);
                $this->token = $split[1];

                $this->generate_arg($number, $split[0]);
            }
        }

        // Calls from $stats method print_results, which prints the
        // statistics results into file
        public function generate_results()
        {
            $this->stats->print_results();
        }


        // Decodes the instruction by the current loaded token and returns the flag
        // of the instruction based on the number and nonterminal of parameters, which 
        // function takes, from Instruction enum class
        public function decode()
        {
            $this->get_token();
            $this->token = strtoupper($this->token);

            switch($this->token)
            {
                case "RETURN":
                    $this->stats->add_jump();
                case "CREATEFRAME":
                case "PUSHFRAME":
                case "POPFRAME":
                case "BREAK":
                    return Instructions::zeroParams;
                
                case "DEFVAR":
                case "POPS":
                    return Instructions::oneParamV;

                case "LABEL":
                    $this->stats->add_label($this->buffer);
                    return Instructions::oneParamL;    

                case "JUMP":
                case "CALL":
                    $this->stats->add_jump();
                    return Instructions::oneParamL;

                case "PUSHS":
                case "WRITE":
                case "EXIT":
                case "DPRINT":
                    return Instructions::oneParamS;

                case "MOVE":
                case "INT2CHAR":
                case "STRLEN":
                case "TYPE":
                case "NOT":
                    return Instructions::twoParamVS;
                
                case "READ":
                    return Instructions::twoParamVT;
                
                case "ADD":
                case "SUB":
                case "MUL":
                case "IDIV":
                case "LT":
                case "GT":
                case "EQ":
                case "AND":
                case "OR":
                case "STRI2INT":
                case "CONCAT":
                case "GETCHAR":
                case "SETCHAR":
                    return Instructions::threeParamVSS;
                
                case "JUMPIFEQ":
                case "JUMPIFNEQ":
                    $this->stats->add_jump();
                    return Instructions::threeParamLSS;
                
                case Instructions::EOF:
                    return Instructions::EOF;

                default:
                    return Instructions::unknownFun;
            }

        }

        // Checks if the current token instruction has $count number of
        // parameters
        protected function check_param_num($count)
        {
            if(count($this->buffer) != $count)
            {
                fwrite(STDERR, "Error, wrong number of parameters! Line: ");
                fwrite(STDERR, $this->lineCount);
                fwrite(STDERR, "\n");
                exit(23);
            }
        }

        // Parses instructions with 0 parameters, checks the number of 
        // tokens in buffer, and generates the correct XML tags
        protected function parse_zero_fun()
        {
            $this->check_param_num(0);

            $this->generate_instruction();

            $this->xml->endElement();

            $this->parse();
        }

        // parses instructions with 1 parameter which is nonterminal 
        // <label>
        protected function parse_oneL_fun()
        {
            $this->check_param_num(1);

            $this->generate_instruction();

            $this->get_token();
            $this->check_label();
            $this->generate_arg("1", "label");
            
            $this->xml->endElement();

            $this->parse();
        }

        // parses instructions with 1 parameter which is nonterminal
        // <var>
        protected function parse_oneV_fun()
        {
            $this->check_param_num(1);

            $this->generate_instruction();

            $this->get_token();
            $this->check_var();
            $this->generate_arg("1", "var");
            
            $this->xml->endElement();

            $this->parse();            
        }

        // parses instructions with 1 parameter which is nonterminal 
        // <symb>
        protected function parse_oneS_fun()
        {
            $this->check_param_num(1);

            $this->generate_instruction();

            $this->get_token();
            $result = $this->check_symb();
            $this->generate_symb($result, "1");

            $this->xml->endElement();

            $this->parse();
        }

        // parses instructions with 2 parameters which are in order 
        // <var> <symb>
        protected function parse_twoVS_fun()
        {
            $this->check_param_num(2);

            $this->generate_instruction();

            $this->get_token();
            $this->check_var();
            $this->generate_arg("1", "var");

            $this->get_token();
            $result = $this->check_symb();
            $this->generate_symb($result, "2");

            $this->xml->endElement();

            $this->parse();
        }

        // parses instructions with 2 parameters which are in order
        // <var> <type>
        protected function parse_twoVT_fun()
        {
            $this->check_param_num(2);

            $this->generate_instruction();

            $this->get_token();
            $this->check_var();
            $this->generate_arg("1", "var");

            $this->get_token();
            $this->check_type();
            $this->generate_arg("2", "type");

            $this->xml->endElement();

            $this->parse();
        }

        // parses instructions with 3 parameters which are in order 
        // <var> <symb> <symb>
        protected function parse_threeVSS_fun()
        {
            $this->check_param_num(3);

            $this->generate_instruction();

            $this->get_token();
            $this->check_var();
            $this->generate_arg("1", "var");

            $this->get_token();
            $result = $this->check_symb();
            $this->generate_symb($result, "2");

            $this->get_token();
            $result = $this->check_symb();
            $this->generate_symb($result, "3");

            $this->xml->endElement();

            $this->parse();
        }

        // parses instructions with 3 parameters which are in order 
        // <label> <symb> <symb>
        protected function parse_threeLSS_fun()
        {
            $this->check_param_num(3);

            $this->generate_instruction();

            $this->get_token();
            $this->check_label();
            $this->generate_arg("1", "label");

            $this->get_token();
            $result = $this->check_symb();
            $this->generate_symb($result, "2");

            $this->get_token();
            $result = $this->check_symb();
            $this->generate_symb($result, "3");

            $this->xml->endElement();

            $this->parse();
        }

        // Starts the parsing process by decoding the instruction 
        // and sending the parser to the correct parsing parsing instruction
        public function parse()
        {
            $choice = $this->decode();
            
            $this->instrCount++;
            $this->stats->add_instr();

            switch($choice)
            {
                case Instructions::zeroParams:
                    $this->parse_zero_fun();
                    break;
                case Instructions::oneParamL:
                    $this->parse_oneL_fun();
                    break;
                case Instructions::oneParamS:
                    $this->parse_oneS_fun();
                    break;
                case Instructions::oneParamV:
                    $this->parse_oneV_fun();
                    break;
                case Instructions::twoParamVS:
                    $this->parse_twoVS_fun();
                    break;
                case Instructions::twoParamVT:
                    $this->parse_twoVT_fun();
                    break;
                case Instructions::threeParamLSS:
                    $this->parse_threeLSS_fun();
                    break;
                case Instructions::threeParamVSS:
                    $this->parse_threeVSS_fun();
                    break;

                case Instructions::EOF:
                    $this->stats->sub_instr();
                    break;

                case Instructions::unknownFun:
                    fwrite(STDERR, "Error! Calling undefined function! Line: ");
                    fwrite(STDERR, $this->lineCount);
                    fwrite(STDERR, "\n");
                    exit(22);
            }
        }
    }
    $parser = new Parser();

    $parser->parse_args($argv);

    $parser->set_up();

    $parser->check_head();
    $parser->generate_head();

    $parser->parse();

    $parser->generate_eof();

    $parser->generate_results();
?>