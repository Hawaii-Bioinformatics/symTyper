#!/usr/bin/python
import sys
import os

import argparse
import logging
from multiprocessing import Pool

from classes.Helpers import *
from classes.CladeParser import *
from classes.HmmerFastaExtractor import *
from classes.FastaExtractor import *
from classes.BlastParser import *
from classes.ProgramRunner import *
from classes.CD_HitParser import *
from classes.PlacementTree_ete2 import * 

import Bio.SearchIO
from Bio import SeqIO

version="0.01"

FORMAT = "%(asctime)-15s  %(message)s"

### TODO add this to configuration file
hmmer_db =  "/home/hputnam/Clade_Alignments/HMMER_ITS2_DB/All_Clades.hmm"
blast_db =  "/home/hputnam/Clade_Alignments/blast_DB/ITS2_Database_04_23_13.fas"

logging.basicConfig(format=FORMAT, level=logging.DEBUG)

def runInstance(myInstance):
   dryRunInstance(myInstance)
   myInstance.run()

def dryRunInstance(myInstance):
   logging.warning(myInstance.dryRun())


def makeDirOrdie(dirPath):
   if not os.path.isdir(dirPath):
      os.makedirs(dirPath)
   else:
      pass
      #TODO; Uncomment after testing done
      #logging.error("Split fasta directory %s already exists " % hmmerOutputDir)
      #sys.exit()
   return dirPath 



def computeStats(args):
   """ Retrn statistics about the sequences and about the database"""
   print "------"
   Helpers.fastaStats(args.inFile)
   print "------"

def processClades(args, pool=Pool(processes=1)):

   logging.debug('CLADE:Processing caldes for: %s ' % args.inFile.name)
   # Split fasta file
   # Put all the directories is at the same level as the inFile.
   fastaFilesDir = os.path.join(os.path.dirname(args.inFile.name), "fasta")
   
   fastaList = Helpers.splitFileBySample(args.inFile.name, args.samplesFile.name, fastaFilesDir)

   # Running HMMscan
   hmmerOutputDir =  os.path.join(os.path.dirname(args.inFile.name), "hmmer_output")
   makeDirOrdie(hmmerOutputDir)   
   logging.debug('CLADE: Starting hmmscans for %s files ' % len(fastaList))
   # TODO UNCOMMENT THIS
   pool.map(runInstance, [ProgramRunner("HMMER_COMMAND", [ hmmer_db, os.path.join(fastaFilesDir,x), os.path.join(hmmerOutputDir,x.split(".")[0]) ] ) for x in fastaList])
   logging.debug('CLADE: Done with hmmscans')

   #Parse HMMscan

   parsedHmmerOutputDir = os.path.join(os.path.dirname(args.inFile.name), "hmmer_parsedOutput")   


   makeDirOrdie(parsedHmmerOutputDir)

   logging.debug('CLADE:Parsing Hmmer outputs for %s files ' % len(fastaList))

   # making dirs in hmmer_parsedOutput with the sample names
   

   pool.map(makeDirOrdie, [ os.path.join(parsedHmmerOutputDir, x.split(".")[0]) for x in fastaList])    


   logging.debug('CLADE: Starting parsing for  for %s files ' % len(fastaList))
   samples = [sample.rstrip() for sample  in open(args.samplesFile.name, 'r')]
   # TODO CHANGE THIS TO RUN ISNTANCE 

   print samples
   print os.path.join(hmmerOutputDir, samples[0]+".out")
   print os.path.join(parsedHmmerOutputDir, samples[0])
   print args.evalue
   
   raw_input("press enter to contunue")
   #for sample in samples:
   #   cp = CladeParser( os.path.join(hmmerOutputDir, sample+".out"), os.path.join(parsedHmmerOutputDir, sample), args.evalue)
   #   runInstance(cp)

   pool.map(runInstance, [CladeParser( os.path.join(hmmerOutputDir, sample+".out"), os.path.join(parsedHmmerOutputDir, sample), args.evalue) for sample in samples])    

   logging.debug('CLADE:Done Parsing Hmmer outputs for %s files ' % len(fastaList))

   # generate tables and pie-charts
   logging.debug("CLADE:Generating formatted output")
   makeCladeDistribTable( args.samplesFile.name, os.path.join(os.path.dirname(args.inFile.name),"hmmer_parsedOutput"))   
   generateCladeBreakdown(args.samplesFile.name, os.path.join(os.path.dirname(args.inFile.name),"hmmer_parsedOutput"), "HIT", 4)
   logging.debug("CLADE:Done Generating formatted output")


   # Create the regular expressions to split the files
   splitFastaRegEx = os.path.join(fastaFilesDir, "%s"+".fasta")
   inFileRegEx = os.path.join(os.path.dirname(args.inFile.name),"hmmer_parsedOutput", "%s", "HIT") 
   makeDirOrdie(os.path.join(os.path.dirname(args.inFile.name),"hmmer_hits"))
   outputFastaRegEx = os.path.join(os.path.dirname(args.inFile.name),"hmmer_hits", "%s"+".fasta")

   extractSeqsFromHits(splitFastaRegEx, inFileRegEx, outputFastaRegEx,  0, args.samplesFile.name, pool)

   logging.debug('Done with Clade run')



def extractSeqsFromHits(splitFastaRegEx, inFileRegEx, outputFastaRegEx, idCol, samplesFile,  pool, args=""):
   """
   extracts the sequences of each hmmer HIT file, in parallel, using the sample specific fasta file (/data/fasta/sample.fasta)
   define args 
   an exmaple fileRegEx is os.path.join(args.hmmerOutputs, "%s", "HIT") it just has one missing field for the sample
   idCol is the position of the id in the file. We assue that the field are tab delimited
   """ 
   if args and args.action== "splitFasta":
      # do something
      pass
   else:
      logging.debug("Extracting Hits from hmmer_parsedOutput")
      samples = [sample.rstrip() for sample in open(samplesFile, 'r')]
      pool.map(runInstance, [FastaExtractor( splitFastaRegEx % sample, inFileRegEx % sample, outputFastaRegEx % sample, idCol) for sample in samples])
      logging.debug(" Done extracting Hits from hmmer_parsedOutput")
      

def processSubtype(args, pool):
   logging.debug("SYBTYPE: Running blast for subtyping")
   samples = [sample.rstrip() for sample in open(args.samplesFile.name, 'r')]
   makeDirOrdie(args.blastOutDir)
   pool.map(runInstance, [ProgramRunner("BLAST_COMMAND", [os.path.join(args.hitsDir, sample+".fasta"), blast_db, os.path.join(args.blastOutDir, sample+".out") ] ) for sample in samples])
   logging.debug("SUBTYPE: Done running blast for subtyping")

   logging.debug("SUBTYPE: Parsing blast output files")
   makeDirOrdie(args.blastResults)
   makeDirOrdie(os.path.join(args.blastResults,"PERFECT"))
   makeDirOrdie(os.path.join(args.blastResults,"UNIQUE"))
   makeDirOrdie(os.path.join(args.blastResults,"MULTIPLE"))
   makeDirOrdie(os.path.join(args.blastResults,"SHORT"))
   makeDirOrdie(os.path.join(args.blastResults,"NEW"))
   makeDirOrdie(os.path.join(args.blastResults,"SHORTNEW"))

   pool.map(runInstance,  [BlastParser( os.path.join(args.blastOutDir, sample+".out"), args.blastResults) for sample in samples])
   logging.debug("SUBTYPE: Parsing blast output files")

   logging.debug("SUBTYPE:Generating formatted output")
   generateSubtypeCounts(args.samplesFile.name, args.blastResults, "UNIQUE")
   generateSubtypeCounts(args.samplesFile.name, args.blastResults, "PERFECT")
   # The SHORTNEW Has a different meaning. 
   # HIS does not show the distribution of subtype hits, but the closest one that these short new seqeunces are hitting
   # However the hits are not significant enough to assign them to them
   generateSubtypeCounts(args.samplesFile.name, args.blastResults, "SHORTNEW")
   logging.debug("SUBTYPE:Done Generating formatted output")

   logging.debug("SUBTYPE:Extracting multiple hits")
   splitFastaRegEx = os.path.join(args.fastaFilesDir, "%s"+".fasta")
   inFileRegEx = os.path.join(args.blastResults,"MULTIPLE", "%s"+".out")
   makeDirOrdie(os.path.join(args.blastResults,"MULTIPLE", "fasta"))
   outputFastaRegEx= os.path.join(args.blastResults,"MULTIPLE", "fasta", "%s"+".fasta")
   extractSeqsFromHits(splitFastaRegEx, inFileRegEx, outputFastaRegEx,  0, args.samplesFile.name, pool)
   logging.debug("SUBTYPE:Done Extracting multiple hits")
   logging.debug("SUBTYPE:Completed")



def resolveMultipleHits(args, pool):
   # Cluster each sample independently and then merges all representatives in allReps.fasta

   repsDir = "Reps"
   repsFasta = "allReps.fasta" # fasta file for all cluster respresentatives
   repsClustersDir= "Clusters" # directoy containing output of clustering
   correctedResultsDir = "correctedMultiplesHits"
   logging.debug("resolveMultipleHits: Started process for resolving multiple hits")

   samples = [sample.rstrip() for sample in open(args.samplesFile.name, 'r')]

   makeDirOrdie(os.path.join(args.clustersDir, "clusters",))

   
   
   pool.map(runInstance, [ProgramRunner("CLUSTER_COMMAND", [os.path.join(args.multipleFastaDir, sample+".fasta"), 
                                                            os.path.join(args.clustersDir, "clusters", sample)])  for sample in samples])
   logging.debug("resolveMultipleHits: Done clustering of multiple reads")

   # Directory where all cluster representatives will be set up    
   makeDirOrdie(os.path.join(args.clustersDir, repsDir))

   allRepsFasta = open(os.path.join(args.clustersDir, repsDir, repsFasta), 'w')

   # WARNING this shoud work fine as long as each clstr file not very large. 
   for sample in samples:
      with open(os.path.join(args.clustersDir, "clusters", sample)) as infile:
            allRepsFasta.write(infile.read())
   allRepsFasta.close()
   logging.debug("resolveMultipleHits: clustering concatenated all reps")

   #Now Cluster all the representatives
   makeDirOrdie(os.path.join(args.clustersDir, repsDir, repsClustersDir))
   runInstance(ProgramRunner("CLUSTER_COMMAND", [os.path.join(args.clustersDir, repsDir, repsFasta), os.path.join(args.clustersDir, repsDir, repsClustersDir, repsFasta)]))
   logging.debug("resolveMultipleHits: done clustering the reps %s" % os.path.join(args.clustersDir, repsDir, repsFasta))
   cdHitParser =  CD_HitParser("data/samples.ids", "data/resolveMultiples/Reps/Clusters/allReps.fasta.clstr", 
                               "data/resolveMultiples/clusters/", "data/blastResults/MULTIPLE/",)
   
   makeDirOrdie(os.path.join(args.clustersDir, correctedResultsDir))
   cdHitParser.run(os.path.join(args.clustersDir, correctedResultsDir)) 

   logging.debug("resolveMultipleHits: Finished resolving multiple hits")


def buildPlacementTree(args, pool):
   

   logging.debug("placermentTree: Building Newick placement Tree for multiple hits") 
   correctedClades = os.listdir(args.correctedResultsDir)
   logging.debug("placermentTree: Clades to be processed are: %s" % " ".join(correctedClades)) 
   # for each the clades, call the the Newick
   makeDirOrdie(args.outputDir)

   # For debugging purposes, call this without the pool
   cClade = correctedClades[0]
   pt = PlacementTree(cClade, args.correctedResultsDir, os.path.join(args.newickFilesDir, "Clade_%s.nwk" % cClade), args.outputDir)
   pt.run()

   # include this in the final code
   #pool.map(runInstance, [PlacementTree(cClade, args.correctedResultsDir, os.path.join(args.newickFilesDir, "Clade_%s.nwk" % cClade), args.outputDir) for cClade in correctedClades])   

   logging.debug("placermentTree: Done with Placement tree processing") 


   




def main(argv):
   # Pool of threads to use. One by default
   # PARENT PARSER PARAMS
   parser = argparse.ArgumentParser(description="symTyper Description", epilog="symTyper long text description")
   parser.add_argument('-v', '--version', action='version', version='%(prog)s '+version)
   
   #TODO: Chnage the default to 1 after testing
   parser.add_argument('-t', '--threads', type=int, default = 1)
   subparsers = parser.add_subparsers(dest='action', help='Available commands')

   ## CLADE
   parser_clade = subparsers.add_parser('clade')
   parser_clade.add_argument('-s', '--samplesFile', type=argparse.FileType('r'), required=True, help=" Samples file  ")
   parser_clade.add_argument('-i', '--inFile', type=argparse.FileType('r'), required=True, help=" Input fasta file ")
   parser_clade.add_argument('-e', '--evalue', type=float, default=1e-20)
   parser_clade.add_argument('-d', '--evalDifference', type=float, default=1e5, help="Eval difference between first and second hits")
   parser_clade.set_defaults(func=processClades)

   ## EXTRACTFASTA
   ## TODO: COMPLETE THIS IF NECESSARY
   #parser_extractFasta = subparsers.add_parser('extractFasta')
   #parser_extractFasta.set_defaults(func=extractSeqsFromHits, someArg= XYZ)

   ## SUBTYPE
   # In a PIPELINE SUBTYPE REQUIRES the extrction of the sequences (EXTRACTFASTA) into into fasta files 
   parser_subtype = subparsers.add_parser('subtype')
   parser_subtype.add_argument('-s', '--samplesFile', type=argparse.FileType('r'), required=True, help=" Samples file ")
   parser_subtype.add_argument('-H', '--hitsDir', required=True, help=" hmmer fasta hits ouput directory")
   parser_subtype.add_argument('-b', '--blastOutDir', type=makeDirOrdie, required=True, help=" blast ouput directory")
   parser_subtype.add_argument('-r', '--blastResults', type=makeDirOrdie, required=True, help=" parsed blast results directory")
   parser_subtype.add_argument('-f', '--fastaFilesDir', type=makeDirOrdie, required=True, help="Split fasta files directory ")
   parser_subtype.set_defaults(func=processSubtype)

   ## RESOLVEMULTIPLE
   # In a PIPELINE SUBTYPE REQUIRES the extrction of the sequences (EXTRACTFASTA) into into fasta files 
   parser_subtype = subparsers.add_parser('resolveMultipleHits')
   parser_subtype.add_argument('-s', '--samplesFile', type=argparse.FileType('r'), required=True, help=" Samples file ")
   parser_subtype.add_argument('-m', '--multipleFastaDir', required=True, help="Directory containing fasta sequences that yielded multiple hits")
   parser_subtype.add_argument('-c', '--clustersDir', type=makeDirOrdie, required=True, help="Dir that will contain cluster information")
   parser_subtype.set_defaults(func=resolveMultipleHits)


   ## BuildPlacermentTree
   # 
   parser_subtype = subparsers.add_parser('builPlacementTree')
   parser_subtype.add_argument('-c', '--correctedResultsDir', required=True, help=" Directory containing corrected Clade placements")
   parser_subtype.add_argument('-n', '--newickFilesDir', required=True, help="Newick directory with files having format info_clade.nwk")
   parser_subtype.add_argument('-o', '--outputDir', type=makeDirOrdie, required=True, help="Dir that will contain the newick and interenal nodes information")
   parser_subtype.set_defaults(func=buildPlacementTree)





   ## INPUT FILE STATS
   parser_stats = subparsers.add_parser('stats')
   parser_stats.add_argument('-i', '--inFile', type=argparse.FileType('r'), required=True, help=" Input fasta file ")
   parser_stats.set_defaults(func=computeStats)

   args = parser.parse_args()

   print "Running with %s threads" % args.threads
   pool = Pool(processes=args.threads)

   # my arguments are
   logging.debug("Initial ARGS are:")   
   logging.debug(args)

   args.func(args, pool)   



if __name__ == "__main__":
   main(sys.argv)
   ###  python symTyper.py -t 3 clade  -i data/sampleInput.fasta -s data/samples.ids
   ### python symTyper.py  -t 3 subtype -H data/hmmer_hits/ -s data/samples.ids -b data/blast_output/ -r data/blastResults/ -f data/fasta
   ### python symTyper.py  -t 3 resolveMultipleHits -s data/samples.ids -m data/blastResults/MULTIPLE/fasta/ -c data/resolveMultiples/
   ### python symTyper.py  -t 3 builPlacementTree -c data/resolveMultiples/correctedMultiplesHits/corrected -n /home/hputnam/Clade_Trees/ -o data/placementInfo

   ### Build this option eventually to run the complete pipeline
   ###  python symTyper.py -t 3 symType  -i data/sampleInput.fasta -s data/samples.ids
