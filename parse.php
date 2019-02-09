<?php
    abstract class Instructions
    {
        const EOF = 100;
        const EMPTY = 101;
    }

    class Parser 
    {
        public $token = 1;
        public $wasOP = false;
        public $buffer = [];
        public $lineCount = 0;
        private $filePointer = "text";
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
            $xml = new XMLWriter();
    
            $xml->openMemory();
            $xml->setIndent(true);
            $xml->startDocument("1.0","UTF-8");
            $xml->startElement("program");
            $xml->writeAttribute("language","IPPcode19");
    
            return $xml;
        }

        public function generate_eof($xml)
        {
            $xml->endDocument();
            $result = $xml->outputMemory();
            print $result;
        }

        public function check_head()
        {
            $this->get_token();

            if($this->token != ".IPPcode19" or ($this->get_line_len() != 0))
            {
                fwrite(STDERR, "Error, expecting .IPPcode19 header! Line: ");
                fwrite(STDERR, $this->lineCount);
                fwrite(STDERR, "\n");
                exit(21);
            }
        }

        public function parse()
        {

        }
    }

    $parser = new Parser();
    $parser->set_up();

    $parser->check_head();
    $xml = $parser->generate_head();


    $parser->generate_eof($xml);
?>