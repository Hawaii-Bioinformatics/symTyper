#!/usr/bin/python
from Bio import SeqIO
import os 

class HmmerFastaExtractor(object):

    def __init__(self, inFastaFile, inHmmerFile, outputFastaFile):
        self.inFile =  inFastaFile
        self.inHmmerFile = inHmmerFile
        self.outputFastaFile = outputFastaFile


    def run(self):
        inFileIndex = SeqIO.index(self.inFile, 'fasta')
        myIds = [x.split()[0] for x in open(self.inHmmerFile, 'r')]
        mySeqs = [inFileIndex.get(x) for x in myIds ]
        SeqIO.write(mySeqs, open(self.outputFastaFile, 'w'), 'fasta')

    
    def dryRun(self):
        return   "Exracting fasta sequences for sample %s and storing fasta file in %s  " % (self.inHmmerFile, self.outputFastaFile )
    
