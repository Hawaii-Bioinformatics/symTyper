import os
# RUNNABLE OBJECTS that we use in pool map by calling run instance on 
from Helpers import printVerbose

class ProgramRunner(object):
    commands = {
        "HMMER_COMMAND" : "hmmscan -o %s.out %s %s",
        #"HMMER_COMMAND" : "hmmscan %s %s > %s.out",
        "BLAST_COMMAND" : "blastall -p blastn -i %s -d %s -o %s -F F -e 1e-05 -b 10 -v 10 ",
        "CLUSTER_COMMAND" : "cd-hit-est -c 0.995 -i %s -o %s"
        }

    def __init__(self, program, params):
        self.program = program
        self.command = self.commands[program] % tuple(params)

    def run(self):
        if printVerbose.VERBOSE:
            os.system(self.command)
        else:
            # for windows we would want to use NUL instead of /dev/null
            os.system( " ".join([self.command, "> /dev/null 2> /dev/null"]))
    def dryRun(self):
        return self.command
    

        
