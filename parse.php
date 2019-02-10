<?php
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

        const unknownFun = 110;

        const varr = 111;
        const val = 112;
    }

    class Parser_vars
    {
        protected $token = 1;
        protected $wasOP = false;
        protected $buffer = [];
        protected $lineCount = 0;
        protected $instrCount = 0;
        protected $filePointer = "text";
        protected $xml = NULL;
    }

    class Parser extends Parser_vars
    {

        // TODO: KVOLI DEBUGGERU UPRAVIM NA FILE OPEN, POTOM OPRAVIT NA STDIN!!!!!!!!!!!!!!!!!!!!!!!!!!§§
        public function set_up()
        {
            $this->filePointer = fopen($this->filePointer, 'r');
        }

        public function get_line_break()
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

            if($this->buffer[0] == NULL)
            {
                $this->buffer = [];
                array_push($this->buffer, Instructions::EMPTY);
                return;
            }
        }

        public function get_token()
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

        public function get_line_len()
        {
            return count($this->buffer);
        }

        public function generate_head()
        {
            $this->xml = new XMLWriter();
    
            $this->xml->openMemory();
            $this->xml->setIndent(true);
            $this->xml->startDocument("1.0","UTF-8");
            $this->xml->startElement("program");
            $this->xml->writeAttribute("language","IPPcode19");
        }

        public function generate_eof()
        {
            $this->xml->endDocument();
            $result = $this->xml->outputMemory();
            print $result;
        }

        protected function generate_instruction()
        {
            $this->xml->startElement("instruction");
            $this->xml->writeAttribute("order", $this->instrCount);
            $this->xml->writeAttribute("opcode", $this->token);
        }

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

        public function decode()
        {
            $this->get_token();
            $this->token = strtoupper($this->token);

            switch($this->token)
            {
                case "CREATEFRAME":
                case "PUSHFRAME":
                case "POPFRAME":
                case "RETURN":
                case "BREAK":
                    return Instructions::zeroParams;
                
                case "DEFVAR":
                case "POPS":
                    return Instructions::oneParamV;

                case "CALL":
                case "LABEL":
                case "JUMP":
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
                    return Instructions::twoParamVS;
                
                case "READ":
                    return Instructions::twoParamVT;
                
                case "ADD":
                case "SUB":
                case "MUL":
                case "IDIV":
                case "LG":
                case "GT":
                case "EQ":
                case "AND":
                case "OR":
                case "NOT":
                case "STRI2INT":
                case "CONCAT":
                case "GETCHAR":
                case "SETCHAR":
                    return Instructions::threeParamVSS;
                
                case "JUMPIFEQ":
                case "JUMPIFNEQ":
                    return Instructions::threeParamLSS;
                
                case Instructions::EOF:
                    return Instructions::EOF;

                default:
                    return Instructions::unknownFun;
            }

        }

        private function check_param_num($count)
        {
            if(count($this->buffer) != $count)
            {
                fwrite(STDERR, "Error, wrong number of parameters! Line: ");
                fwrite(STDERR, $this->lineCount);
                exit(23);
            }
        }

        protected function check_var()
        {
            $regex = "/^TF@[a-zA-Z0-9_\-$&%*!?]+$|^LF@[a-zA-Z0-9_\-$&%*!?]+$|^GF@[a-zA-Z0-9_\-$&%*!?]+$/";

            $result = preg_match($regex, $this->token);

            if($result == 0 or $result == FALSE)
            {
                fwrite(STDERR, "Error, expecting <var> function parameter! Line: ");
                fwrite(STDERR, $this->lineCount);
                exit(23);
            }
        }

        protected function check_symb()
        {
            $var_regex = "/^TF@[a-zA-Z0-9_\-$&%*!?]+$|^LF@[a-zA-Z0-9_\-$&%*!?]+$|^GF@[a-zA-Z0-9_\-$&%*!?]+$/";

            $result = preg_match($regex, $this->token);

            if($result)
            {
                return Instructions::varr;
            }

            $val_regex = "/^int@[-+]?[0-9]+$|^bool@true$|^bool@false$|^string@.*/";

            $result = preg_match($regex, $this->token);

            if($result)
            {
                return Instructions::val;
            }
            else
            {
                return false;
            }
        }

        protected function check_label()
        {
            $regex = "/^[a-zA-Z0-9_\-$&%*!?]+$/";

            $result = preg_match($regex, $this->token);

            if($result == 0 or $result == FALSE)
            {
                fwrite(STDERR, "Error, expecting <label> function parameter! Line: ");
                fwrite(STDERR, $this->lineCount);
                exit(23);
            }            
        }

        protected function check_type()
        {
            $regex = "/^int$|^bool$|^string$/";

            $result = preg_match($regex, $this->token);

            if($result == 0 or $result == FALSE)
            {
                fwrite(STDERR, "Error, expecting <type> function parameter! Line: ");
                fwrite(STDERR, $this->lineCount);
                exit(23);
            }             
        }

        protected function cut_symb()
        {
            $var_regex = ""
        }

        private function parse_zero_fun()
        {
            $this->check_param_num(0);

            $this->generate_instruction();

            $this->xml->endElement();

            $this->parse();
        }

        private function parse_oneL_fun()
        {
            $this->check_param_num(1);

            $this->generate_instruction();

            $this->get_token();
            
            $this->check_label();

            $this->xml->startElement("arg1");
            $this->xml->writeAttribute("type","label");
            $this->xml->text($this->token);
            
            $this->xml->endElement();
            $this->xml->endElement();

            $this->parse();
        }

        private function parse_oneV_fun()
        {
            $this->check_param_num(1);

            $this->generate_instruction();

            $this->get_token();
            
            $this->check_var();

            $this->xml->startElement("arg1");
            $this->xml->writeAttribute("type","var");
            $this->xml->text($this->token);
            
            $this->xml->endElement();
            $this->xml->endElement();

            $this->parse();            
        }

        private function parse_oneS_fun()
        {
            $this->check_param_num(1);

            $this->generate_instruction();

            $this->get_token();
            
            $result = $this->check_symb();

            if($result == false)
            {
                fwrite(STDERR, "Error, expecting <symb> function parameter! Line: ");
                fwrite(STDERR, $this->lineCount);
                exit(23);                
            }
            else if($result == Instructions::varr)
            {
                $this->xml->startElement("arg1");
                $this->xml->writeAttribute("type","var");
                $this->xml->text($this->token);
            }
            else if($result == Instructions::val)
            {
                
            }
        }

        public function parse()
        {
            $choice = $this->decode();
            
            $this->instrCount++;

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
                    $this->parse_twoLSS_fun();
                    break;
                case Instructions::threeParamVSS:
                    $this->parse_threeVSS_fun();
                    break;

                case Instructions::EOF:
                    break;

                case Instructions::unknownFun:
                    fwrite(STDERR, "Error! Calling undefined function! Line: ");
                    fwrite(STDERR, $this->lineCount);
                    fwrite(STDERR, "\n");
                    exit(21);
            }
        }
    }

    $parser = new Parser();
    $parser->set_up();

    $parser->check_head();
    $parser->generate_head();

    $parser->parse();

    $parser->generate_eof();
?>