#!/usr/bin/python
import Bio
import os 
from Helpers import printVerbose

class CladeParser(object):
    def __init__(self, inFile, outputDirPath, minEval=1e-20):
        self.inFile = inFile
        self.outputDirPath = outputDirPath
        self.minEval= minEval

    def run(self):
        printVerbose("+++++"+self.outputDirPath+"++++++")
        lowFile  = open(os.path.join(self.outputDirPath, "LOW"), 'w')
        ambiguousFile = open(os.path.join(self.outputDirPath, "AMBIGUOUS"), 'w')
        hitsFile = open(os.path.join(self.outputDirPath, "HIT"), 'w')
        noHitsFile = open(os.path.join(self.outputDirPath, "NOHIT"), 'w')
        for seq in Bio.SearchIO.parse(self.inFile, 'hmmer3-text'):
            if len(seq.hits) > 1:
                if seq.hits[0].evalue > self.minEval:
                    lowFile.write("LOW:%s\t%s\t%s\n" % (seq.id, seq.hits[0].id, seq.hits[0].evalue));
                    continue
                else:
                    if len(seq.hits) > 1:
                        if (seq.hits[1].evalue / seq.hits[0].evalue) < 1e5:                
                            ambiguousFile.write("AMBIGUOUS:%s\t%s\t%s\t%s\t%s\n"
                                                % (seq.id, seq.hits[0].id, seq.hits[1].id, seq.hits[0].evalue, seq.hits[1].evalue));
                            continue
                    # previous contienue shortcircuits the following
                    hitsFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n"
                                   % (seq.id, seq.hits[0].hsps[0].query_start, seq.hits[0].hsps[0].query_end,  
                                      seq.hits[0].id, seq.hits[1].id, seq.hits[0].evalue, seq.hits[1].evalue))
                    continue
            else:
                noHitsFile.write("seqId:%s\n" % (seq.id) );
                continue
        lowFile.close(); ambiguousFile.close(); hitsFile.close(); noHitsFile.close()        
    
    def dryRun(self):
        return   "parsing hmmer out  for file %s and putting results in %s" % (self.inFile, self.outputDirPath)
    
