<?php 

    Class Tester
    {
        protected $recursive = false;
        protected $directory = NULL;
        protected $parser = NULL;
        protected $interpret = NULL;
        protected $parseOnly = false;
        protected $intOnly = false;
        protected $files = NULL;
        protected $argc = 1;
        protected $parsedArgs = 1;
        protected $resultsParse = [];
        protected $resultsInt = [];
        protected $resultsRetval = [];

        private function rsearch($folder, $pattern)
        {
            $dir = new RecursiveDirectoryIterator($folder);
            $ite = new RecursiveIteratorIterator($dir);

            $files = new RegexIterator($ite, $pattern, RegexIterator::GET_MATCH);
            
            $fileList = array();
            foreach($files as $file) 
            {
                $fileList = array_merge($fileList, $file);
            }

            return $fileList;
        }

        public function parse_args($args)
        {
            #$test = $this->search(getcwd(),);
            #print_r($test);
            
            $this->argc = count($args);

            $help = preg_grep("/^--help$|^-h$/", $args);
            if(!empty($help) and count($args) != 2)
            {
                fwrite(STDERR, "Error, wrong parameters!\n");
                exit(10);
            }
            else if(!empty($help))
            {
                print "Testing tool test.php for parse.php and interpret.py\n";
                print "Written by Tomáš Sasák for BUT FIT 2019\n\n";
                print "Legal arguments:\n";
                print "--help               Shows this message.\n";
                print "--directory=path     Searches .src tests in <path>, if empty searches cwd().\n";
                print "--recursive          Searches for tests recursively.\n";
                print "--parse-script=file  Path to the \"parse.php\", if empty searches cwd().\n";
                print "--int-script=file    Path to the \"interpret.py\", if empty searches cwd().\n";
                print "--parse-only         Tests are performed only on \"parse.php\".\n";
                print "--int-only           Tests are performed only on \"interpret.py\".\n";
                exit(0);
            }

            $recursive = preg_grep("/^--recursive$|^-r$/", $args);
            if(!empty($recursive) and count($recursive) == 1)
            {
                $this->recursive = true;
                $this->parsedArgs++;
            }
            else if(!empty($recursive) and count($recursive) != 1)
            {
                fwrite(STDERR, "Error, wrong parameters!\n");
                exit(10);
            }

            $directory = preg_grep("/^--directory=.+$/", $args);
            if(!empty($directory) && count($directory) == 1)
            {
                $directory = implode($directory);
                
                $path = explode("=", $directory, 2);
                $path = $path[1];

                $exists = is_dir($path);
                if($exists == false)
                {
                    fwrite(STDERR, "Error, invalid directory!\n");
                    exit(10);
                }

                $this->directory = realpath($path);
                $this->parsedArgs++;

            }
            else if(!empty($directory) && count($directory) != 1)
            {
                fwrite(STDERR, "Error, wrong parameters!\n");
                exit(10);
            }
            else
            {
                $this->directory = getcwd();
            }

            $parser = preg_grep("/^--parse-script=.+$/", $args);
            if(!empty($parser) and count($parser) == 1)
            {
                $parser = implode($parser);

                $path = explode("=", $parser, 2);
                $path = $path[1];

                $this->parser = $path;
                $this->parsedArgs++;
            }
            else if(!empty($parse) and count($parse) != 1)
            {
                fwrite(STDERR, "Error, wrong parameters!\n");
                exit(10);
            }
            else
            {
                $this->parser = getcwd() . "/parse.php";
            }

            $interpret = preg_grep("/^--int-script=.+$/", $args);
            if(!empty($interpret) and count($interpret) == 1)
            {
                $interpret = implode($interpret);

                $path = explode("=", $interpret, 2);
                $path = $path[1];

                $this->interpret = $path;
                $this->parsedArgs++;
            }
            else if(!empty($parse) and count($parse) != 1)
            {
                fwrite(STDERR, "Error, wrong parameters!\n");
                exit(10);
            }
            else
            {
                $this->interpret = getcwd() . "/interpret.py";
            }

            $parseOnly = preg_grep("/^--parse-only$/", $args);
            if(!empty($parseOnly) and count($parseOnly) == 1)
            {
                $this->parseOnly = true;
                $this->parsedArgs++;
            }
            else if(!empty($parseOnly) and count($parseOnly) != 1)
            {
                fwrite(STDERR, "Error, wrong parameters!\n");
                exit(10);
            }

            $intOnly = preg_grep("/^--int-only$/", $args);
            if(!empty($intOnly) and count($intOnly) == 1)
            {
                $this->intOnly = true;
                $this->parsedArgs++;
            }
            else if(!empty($intOnly) and count($intOnly) != 1)
            {
                fwrite(STDERR, "Error, wrong parameters!\n");
                exit(10);
            }

            if(($this->intOnly and $this->parseOnly))
            {
                fwrite(STDERR, "Error, wrong parameters!\n");
                exit(10);
            }
            else if($this->argc != $this->parsedArgs)
            {
                fwrite(STDERR, "Error, wrong parameters!\n");
                exit(10);
            }

        }

        public function fetch_tests()
        {
            if($this->recursive == true)
            {
                $this->files = $this->rsearch($this->directory, "/^.*\.src$/");
            }
            else
            {
                $regex = $this->directory . "/*.src";
                $this->files = glob($regex);
            }
        }

        private function compare_results()
        {
            $queue = 0;

            foreach($this->files as $i)
            {
                $testname = substr($i, 0, -4);

                if(!$this->intOnly)
                {
                    exec("diff $testname.in $testname.superdupermemexml", $output, $diff);
                    if($diff == "0\n")
                    {
                        array_push($this->resultsParse, true);
                    }
                    else
                    {
                        array_push($this->resultsParse, false);
                    }
                }

                if(!$this->parseOnly)
                {
                    exec("diff $testname.out $testname.superdupermemeint", $output, $diff);
                    if($diff == "0\n")
                    {
                        array_push($this->resultsInt, true);
                    }
                    else
                    {
                        array_push($this->resultsInt, false);
                    }
                }

                exec("diff $testname.rc $testname.superdupermemeretval", $output, $diff);
                if($diff == "0\n")
                {
                    array_push($this->resultsRetval, true);
                }
                else
                {
                    array_push($this->resultsRetval, false);
                }

            }
        }

        public function run_tests()
        {
            foreach($this->files as $i)
            {
                $i = substr($i, 0, -4);
                $filename = $i . ".in";
                $creator = fopen($filename, "a");
                fclose($creator);

                $filename = $i . ".out";
                $creator = fopen($filename, "a");
                fclose($creator);

                $filename = $i . ".rc";
                if(!is_file($filename))
                {
                    $creator = fopen($filename, "a");
                    fwrite($creator, "0");
                    fclose($creator);
                }
                if(!$this->intOnly)
                {
                    $command = "php " . $this->parser . " < " . $i . ".src" . " > " . $i . ".superdupermemexml 2>&1";
                    exec($command, $output, $retval);
                    
                    if($retval != "0\n")
                    {
                        shell_exec("echo -n \"$retval\" > $i.superdupermemeretval");
                        continue;
                    }
                    else
                    {
                        shell_exec("echo -n \"0\" > $i.superdupermemeretval");
                    }
                }

                if(!$this->parseOnly)
                {
                    $command = "python3 " . $this->interpret . " < " . $i . ".in" . " > " . $i . ".superdupermemeint 2>&1";
                    exec($command, $output, $retval);
                    
                    if($retval != "0\n")
                    {
                        shell_exec("echo -n \"$retval\" > $i.superdupermemeretval");
                        continue;
                    }
                }
            }
            $this->compare_results();

        }

        public function print_result()
        {
            date_default_timezone_set("Europe/Prague");
            $time = date("Y-m-d - H:m:s");
            print "<!DOCTYPE html>
            <html>
            <head>
            <title>Test results</title>
            </head>
            <body style=\"background-color:rgb(23,24,28);color:white;font-family:arial\">
            <h1 style=\"text-align:center;\">Test results for \"parse.php\" and \"interpret.py\"</h1>
            <h2 style=\"text-align:center;\">$time</h2>
            <br>
            <table style=\"text-align:center;width:100%;font-size:12px\">\n";
            print "<tr style=\"font-size:17px\">";
            print "<th>File</th>";
            if(!$this->intOnly)
            {
                print "<th>Parser</th>";
            }
            if(!$this->parseOnly)
            {
                print "<th>Interpret</th>";
            }
            
            print "<th>Return code</th> </tr>";
            

            for($i = 0; $i < count($this->files); $i++)
            {
                print "<tr>";
                $file = $this->files[$i];
                print "<th style=\"font-size:10px\">$file</th>";
                if(!$this->intOnly)
                {
                    if($this->resultsParse[$i] == true)
                    {
                        print "<th style=\"color:green\"> Success </th>";
                    }
                    else
                    {
                        print "<th style=\"color:red\"> Failed </th>";
                    }
                }
                if(!$this->parseOnly)
                {
                    if($this->resultsInt[$i] == true)
                    {
                        print "<th style=\"color:green\"> Success </th>";
                    }
                    else
                    {
                        print "<th style=\"color:red\"> Failed </th>";
                    }
                }

                if($this->resultsRetval[$i] == true)
                {
                    print "<th style=\"color:green\"> Success </th>";
                }
                else
                {
                    print "<th style=\"color:red\"> Failed </th>";
                }

                print "</tr>";
            }
        }

        public function print_hints()
        {
            print "</table>";
            print "<p style=\"font-size:10px;text-align:center;\">Warning! All tests do NOT need to have an \"\\n\" at the end of the file.</p>";
            if(!is_file($this->parser) && !$this->intOnly)
            {
                print "<p style=\"font-size:10px;text-align:center;\">Warning! \"parser.php\" not found! All tests for parser will fail.</p>"; 
            }
            if(!is_file($this->interpret) && !$this->parseOnly)
            {
                print "<p style=\"font-size:10px;text-align:center;\">Warning! \"interpret.py\" not found! All tests for interpret will fail.</p>"; 
            }
            print "</body>
            </html>";
        }

        public function clean_up()
        {
            foreach($this->files as $i)
            {
                $filename = substr($i, 0, -4);

                if(!$this->parseOnly)
                {
                    shell_exec("rm $filename.superdupermemeint");
                }

                if($this->intOnly)
                {
                    shell_exec("rm $filename.superdupermemexml");
                }
                
                shell_exec("rm $filename.superdupermemeretval");
            }
        }
    }

    $tester = new Tester();

    $tester->parse_args($argv);

    $tester->fetch_tests();

    $tester->run_tests();

    $tester->print_result();

    $tester->print_hints();

    $tester->clean_up();


    #$handle = fopen($my_file, 'a') or die('Cannot open file: '.$my_file);

    
?>