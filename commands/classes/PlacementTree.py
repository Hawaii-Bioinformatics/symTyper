from ete2 import Tree, TreeStyle, NodeStyle, faces, AttrFace, CircleFace, TextFace
from Bio import Phylo
from Helpers import makeDirOrdie
import re
import os


class PlacementTree(object):
    def __init__(self, clade, correctedPlacementPerClade, newickRef, outputsDir):
        self.correctedCountsFile = os.path.join(correctedPlacementPerClade, clade)
        self.newickRef = newickRef

        self.clade = clade
        
        self.cladeDir = os.path.join(outputsDir, self.clade)
        makeDirOrdie(self.cladeDir)

        self.nodeCladeDistribution = os.path.join(self.cladeDir,"treenodeCladeDist.tsv")
        self.newickOutptutFile = os.path.join(self.cladeDir,"placed_clade_%s.nwk" % self.clade)

    def __relabelInternalNodes__(self, tree):
        for iNode in tree.get_nonterminals():
            if iNode.name:
                iNode.name = "N_"+iNode.name

    def __getDistributionPerInternalNode__(self, tree, visitedInternalNodes):

        nodeCladesOutFile = open(self.nodeCladeDistribution, 'w')

        # get all the subtypes that we use in headers and print the header
        subtypes = set([i for x in visitedInternalNodes.values() for i in x])
        print >> nodeCladesOutFile, "\t",
        print >> nodeCladesOutFile, "\t".join(["%s"%x for x in subtypes])

        for node in  visitedInternalNodes.keys():
            print  >> nodeCladesOutFile, node,
            for sType in subtypes:
                print >> nodeCladesOutFile, "\t",
                print >> nodeCladesOutFile, visitedInternalNodes[node][sType] if sType in visitedInternalNodes[node].keys() else 0,
            print >> nodeCladesOutFile, "\n";
        nodeCladesOutFile.close()
        

    def run(self):
        try:
            cladeInfo = open(self.correctedCountsFile,"r")
        except IOError:
            print "** Could not open %s file" % self.correctedCountsFile
        # read in the newick tree 
        try:
            print "*** opening the newick ref file %s" % self.newickRef
            tree = Phylo.parse(self.newickRef, 'newick').next()
        except IOError:
            print "Could not open newick reference file %s" % self.newickRef


        # keeps the counts of sameple per internal_node {49:{X1: 11, X2 : 2, ... }, 55:{ X9 : 115:...}}
        nodeSampleCounts= {}
        #  @presentSamples{(keys(%counts), keys(%presentSamples))}=()
        # for each of the value in the init array assign () as a values  # {110:(), 111:(), ...}                                                                  
        presentSamples={}
        # The collection of nodes that we have visited
        visitedInternalNodes={};

        # TODO The resolving stage should be moved around the resolve action in the script, should not be here!
        # TODO: EASY fix

        # will get the the subtype disctribution of the clusters that resolved (have only one subtype), after applying the resolve stage

        # each line represents one cluster
        for line in cladeInfo:
            line = line.rstrip()
            clusterId = re.search('CL_(\d+)\t', line).groups()[0]
            numSeqs = re.search('numSeq: (\d+)\t', line).groups()[0]

            breakdown = re.search('breakDown:(.+)\t', line).groups()[0]  #breakdown by sample
            # takes a string breakdown= 'X2:2 X3:1 X1:8'
            # and generates a dict counts= {'X2' : 2, 'X3' : 1, 'X1' : 8}
            counts = dict(map(lambda x: x.split(":"), breakdown.split()))

            # generate dict from array where i is key (subtype) and i+1 is value (count)
            # TODO: use more efficient way to do this!
            subtypesInfo = dict(zip([x.replace(":", "") for x in line.split("\t")[4].split()[1::2]], [y for y in line.split("\t")[4].split()[2::2]]))

            if len(subtypesInfo.keys()) == 1:
                # TODO. ADD THIS TO RESOLVED
                ##push(leafs, $subtype);
                pass
            lca  = tree.common_ancestor(subtypesInfo.keys())
            total = str(int(lca.name) + int(numSeqs)) if  lca.name else str(numSeqs)
            lca.name = total


            if (lca in visitedInternalNodes.keys()):
                for c in counts.keys():
                    if c in visitedInternalNodes[lca].keys():
                        visitedInternalNodes[lca][c] = int(visitedInternalNodes[lca][c]) +  int(counts[c])
                    else:
                        visitedInternalNodes[lca][c] = int(counts[c])
            else:
                visitedInternalNodes[lca] = counts;
        # WRITE THIS
        self.__relabelInternalNodes__(tree)
        self.__getDistributionPerInternalNode__(tree, visitedInternalNodes)
        
        Phylo.write(tree, self.newickOutptutFile, "newick")


    def dryRun(self):
        
        return "Running placement tree for clade %s, the newick ref file is %s" % (self.clade, self.newickRef)
