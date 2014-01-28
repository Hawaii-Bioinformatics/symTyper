from ete2 import Tree, TreeStyle, NodeStyle, faces, AttrFace, CircleFace, TextFace
from Bio import Phylo
from Helpers import makeDirOrdie
import re
import os


class PlacementTree(object):
    #
    # clade: calde for which a tree will be built
    # correctedPlacementPerClade: data/resolveMultiples/correctedMultiplesHits/corrected
    # newickRef: newick tree for clade
    # outputDir: where the results will be written


    def __init__(self, clade, correctedPlacementPerClade, newickRef, outputsDir):
        self.correctedCountsFile = os.path.join(correctedPlacementPerClade, clade)
        self.newickRef = newickRef

        self.clade = clade
        
        self.cladeDir = os.path.join(outputsDir, self.clade)
        makeDirOrdie(self.cladeDir)

        # otuputs
        self.nodeCladeDistribution = os.path.join(self.cladeDir,"treenodeCladeDist.tsv")
        self.newickOutptutFile = os.path.join(self.cladeDir,"placed_clade_%s.nwk" % self.clade)
        self.treePNGFile = os.path.join(self.cladeDir,"placed_clade_%s.png" % self.clade)
        self.treeSVGFile = os.path.join(self.cladeDir,"placed_clade_%s.svg" % self.clade)
        
        self.totalcount = 0


    def __getDistributionPerInternalNode__(self, tree, visitedInternalNodes):

        nodeCladesOutFile = open(self.nodeCladeDistribution, 'w')
        # get all the samples that were used                                                                                                                                             
        samples = set([i for x in visitedInternalNodes.values() for i in x])

        nodes = visitedInternalNodes.keys()
        print >> nodeCladesOutFile, "sample\t",
        print >> nodeCladesOutFile, "\t".join(["%s_%s" % (self.clade, x) for x in nodes])
        for sample in samples:
            print  >> nodeCladesOutFile, sample,
            for node in  visitedInternalNodes.keys():
                print >> nodeCladesOutFile, "\t",
                print >> nodeCladesOutFile, visitedInternalNodes[node][sample] if sample in visitedInternalNodes[node].keys() else 0,
            print >> nodeCladesOutFile
        nodeCladesOutFile.close()

        # get all the samples that were used 
        # samples = set([i for x in visitedInternalNodes.values() for i in x])
        # print >> nodeCladesOutFile, "\t",
        # print >> nodeCladesOutFile, "\t".join(["%s"%x for x in samples])

        # for node in  visitedInternalNodes.keys():
        #     print  >> nodeCladesOutFile, node,
        #     for sample in samples:
        #         print >> nodeCladesOutFile, "\t",
        #         print >> nodeCladesOutFile, visitedInternalNodes[node][sample] if sample in visitedInternalNodes[node].keys() else 0,
        #     print >> nodeCladesOutFile, "\n";
        # nodeCladesOutFile.close()


    # layout required by generateImage
    def __layout__(self, node):
        if node.is_leaf():
            # Add node name to laef nodes
            N = AttrFace("name", fsize=14, fgcolor="black")
            faces.add_face_to_node(N, node, 0)
            nstyle = NodeStyle()

            nstyle["size"] = 0
            node.set_style(nstyle)
        if "internalCount" in node.features:
            print node.name
            # Creates a sphere face whose size is proportional to node's     
            # feature "weight"
            rad = int( ((float(node.internalCount) / float(self.totalcount)) * 100.0) )
            C = CircleFace(radius=rad, color="RoyalBlue", style="sphere")
            T = TextFace(rad)
            # Let's make the sphere transparent
            C.opacity = 0.5
            # And place as a float face over the tree
            faces.add_face_to_node(C, node, 0, position="float")
            faces.add_face_to_node(T, node, 1)

    def generateImage(self, tree):
        ts = TreeStyle()
        ts.layout_fn = self.__layout__
        ts.mode = "c"
        ts.show_leaf_name = False
        tree.render(self.treePNGFile, w=1000, tree_style = ts)
        tree.render(self.treeSVGFile, w=250, tree_style = ts)
        

    def run(self):

        try:
            cladeInfo = open(self.correctedCountsFile,"r")
        except IOError:
            print "** Could not open %s file" % self.correctedCountsFile

        # read in the newick tree 
        try:
            print "*** opening the newick ref file %s" % self.newickRef
            tree = Tree(open(self.newickRef).readline().rstrip())
        except IOError:
            print "Could not open newick reference file %s" % self.newickRef


            
        # Label all interenal nodes
        # label is I:<int>    
        i=0
        for n in tree.traverse():
            if not n.is_leaf():
                n.name = "I:%s" % i
                i+=1



        # keeps the counts of sample per internal_node {49:{X1: 11, X2 : 2, ... }, 55:{ X9 : 115:...}}
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
            
            counts = dict(map(lambda x: x.split(":"), breakdown.split())) # breakdown by sample for an internal node

            # generate dict from array where i is key (subtype) and i+1 is value (count)
            # TODO: use more efficient way to do this!
            subtypesInfo = dict(zip([x.replace(":", "") for x in line.split("\t")[4].split()[1::2]], [y for y in line.split("\t")[4].split()[2::2]]))

            if len(subtypesInfo.keys()) == 1:
                # TODO. ADD THIS TO RESOLVED
                ##push(leafs, $subtype);
                pass
            lca  = tree.get_common_ancestor(subtypesInfo.keys())
            if 'internalCount' in lca.features:
                lca.intenalCounts =  lca.internalCount + numSeqs
            else:
                lca.add_features( internalCount = numSeqs)
            self.totalcount += numSeqs
                

            #Update the breakdown by samples, based on the new samples
            if (lca.name in visitedInternalNodes.keys()):
                for c in counts.keys():
                    if c in visitedInternalNodes[lca.name].keys():
                        visitedInternalNodes[lca.name][c] = int(visitedInternalNodes[lca.name][c]) +  int(counts[c])
                    else:
                        visitedInternalNodes[lca.name][c] = int(counts[c])
            else:
                visitedInternalNodes[lca.name] = counts;
        # WRITE THIS

        self.__getDistributionPerInternalNode__(tree, visitedInternalNodes)
        tree.write(features=["count", "name"], format=0, outfile=self.newickOutptutFile)
        print visitedInternalNodes

        self.generateImage(tree)

        


    def dryRun(self):
        
        return "Running placement tree for clade %s, the newick ref file is %s" % (self.clade, self.newickRef)
