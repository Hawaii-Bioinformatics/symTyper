#!/usr/bin/python
from Bio import SeqIO
import os 

class FastaExtractor(object):

    def __init__(self, inFastaFile, inFile, outputFastaFile, idCol=0):
        self.inFastaFile =  inFastaFile
        self.inFile = inFile
        self.outputFastaFile = outputFastaFile
        self.idCol = idCol


    def run(self):
        inFileIndex = SeqIO.index(self.inFastaFile, 'fasta')
        myIds = [x.split()[self.idCol] for x in open(self.inFile, 'r')]
        print myIds
        mySeqs = [inFileIndex.get(x) for x in myIds ]
        SeqIO.write(mySeqs, open(self.outputFastaFile, 'w'), 'fasta')

    
    def dryRun(self):
        return   "Exracting fasta sequences for sample %s and storing fasta file in %s  " % (self.inFile, self.outputFastaFile )
    
