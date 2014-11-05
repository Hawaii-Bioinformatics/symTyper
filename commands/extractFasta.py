#!/usr/bin/python

import sys
import os

import logging
from multiprocessing import Pool

from classes.FastaExtractor import *


def makeDirOrdie(dirPath):
   if not os.path.isdir(dirPath):
      os.makedirs(dirPath)
   else:
      pass
   return dirPath


if(len(sys.argv) != 4):
    print "USAGE: %s <listing  directory> <list file extension> <input fasta (seq db)>"%(sys.argv[0])
    sys.exit(1)

parent = sys.argv[1]
outputdir = makeDirOrdie(os.path.join(parent, "fasta"))

for f in os.listdir(parent):
    if not f.endswith(sys.argv[2]):
        continue
    samples = os.path.join(parent, f)
    outfile = "%s.fasta"%(os.path.splitext(os.path.basename(samples))[0])
    FastaExtractor(sys.argv[3], samples, os.path.join(outputdir, outfile)).run()
