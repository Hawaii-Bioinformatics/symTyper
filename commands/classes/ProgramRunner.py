import os
# RUNNABLE OBJECTS that we use in pool map by calling run instance on 


class ProgramRunner(object):
    commands = {
        "HMMER_COMMAND" : "/home/mahdi/programs/hmmer-3.0-linux-intel-x86_64/binaries/hmmscan %s %s > %s.out",
        "BLAST_COMMAND" : "blastall -p blastn -i %s -d %s -o %s -F F -e 1e-05 -b 10 -v 10 ",
        "CLUSTER_COMMAND" : "/home/mahdi/programs/cd-hit-v4.5.6-2011-09-02/cd-hit-est -c 0.995 -i %s -o %s"
        }

    def __init__(self, program, params):
        self.program = program
        self.command = self.commands[program] % tuple(params)

    def run(self):
        os.system(self.command)

    def dryRun(self):
        return self.command
    

        
