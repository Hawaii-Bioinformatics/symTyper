## THIS CODE IS MOSTLY COMPLETELY SEQUENTIAL.
### TODO, rewrite using a pool of processes

#### VARIABLES CONVENTIONS
#### data structures are either specific for samples: first level of clustering or for
#### reps: second level of  clustering 
#### Variables describe the data structure
#### EX.:
## reps_clusterSequences 
##    reps specific data structure
##    cluster is a key and sequences is value (list)
## sample_sequenceCluster
##    sample specific data structure
##    sequence is a key and cluster is values

import os
import sys
from collections import Counter, defaultdict

from Helpers import makeDirOrdie, printVerbose


class CD_HitParser(object):
    MIN_NUM_SEQS = 1;
    #samplesNames = samples
    def __init__(self, samplesFile, repsClustersFile, samplesClustDir, multiplesDir):

        """
                #reps_clusterSequences           {CL_ID:[seq1Id, seq2Id, ...], CL_ID:[seq1Id, ...], ... }
                #reps_clusterSubtypeCounts       {CL_ID:{subtype_1:count, ...}}
                #reps_sequenceCluster            {seq1Id:CL_ID, seq1Id:CL_ID, ... }
        """
        self.samplesClustDir = samplesClustDir
        self.repsClustersFile = repsClustersFile
        self.multiplesDir = multiplesDir

        self.samples =  [sample.rstrip() for sample  in open(samplesFile, 'r')] 
        # clusterSequences
        self.reps_clusterSequences= {} #{"CL_1": ["X1::29010", "X23::112", ...], "CL_2": ["X3::110", "X11::191", ...]}
        # clusters       
        # this actually should be called self.reps_clusterSampleCount not subtupeCount
        self.reps_clusterSubtypeCounts= {} ## {"CL_1" : {"X1": 2, "X2": 10, ...}, "CL_2" : {"X1": 3, "X3": 1, ...}, ...}
        # instead of counting the reps, we count the reps and the sequences they represent at the sample level
        self.reps_sampleTotalCounts={} 
        # sequences
        self.reps_sequenceCluster= {} ## {"X1::1": "CL_1" , "X2::1": "CL_2", ... }

        self.__initRepsDicts__(samplesFile)


        # This one is similar to self.reps_clusterSequences, except that it describes the clusters in the first clustering iteration (the individual samples)
        #{"X1": {"CL_1":\["X1::1503",'X1::1403" ...], "CL_2":\["X1::4", "X1::167"]}}
        self.sample_clustersSeqs ={}
        # This one is similar to self.reps_sequenceCluster, except that it describes the sequences in the first clustering iteration (the individual samples)
        # {"X1" : {"X1::1": "CL_1","X1::23" : "CL_2", ... }, "X2": {"X2:11", "CL_78", ...} ...}
        self.sample_sequenceCluster = {}
        
        for sample in self.samples:
            self.__initSamplesDicts__(sample)

    def __getEffectiveSubtypes__(self, subtypeCounts, minCount):
        filtered = []

        for (k,v) in subtypeCounts.items():
            if subtypeCounts[k] < minCount:
                filtered.append(k)
                subtypeCounts.pop(k)
            
        return subtypeCounts, filtered


    def __initSamplesDicts__(self, sample):
        """
        process the clusts file for one sample
        """
        clusterId = ""
        self.sample_clustersSeqs[sample]={}
        self.sample_sequenceCluster[sample]={}
        

        with open(os.path.join(self.samplesClustDir, sample+'.clstr'),'r' ) as sampleClusters:
            for line in sampleClusters:
                line = line.rstrip()
                if line.startswith(">"):
                    clusterId = "CL_"+line.split()[1]
                    self.sample_clustersSeqs[sample][clusterId] = []
                else:
                    seq = line.split()[2][1:-3]
                    self.sample_clustersSeqs[sample][clusterId].append(seq)
                    self.sample_sequenceCluster[sample][seq] = clusterId 


    def __initRepsDicts__(self, samplesFile):
        """
        Process the clusters file for the reps.
        """
        clusterId = ""

        with open(self.repsClustersFile,'r' ) as repsClusters:
            for line in repsClusters:
                line = line.rstrip()
                if line.startswith(">"):
                    clusterId = "CL_"+line.split()[1]
                    self.reps_clusterSubtypeCounts[clusterId] = {}
                    self.reps_clusterSequences[clusterId] = []
                else:
                    seq = line.split()[2][1:-3]
                    subType = seq.split("::")[0]
                    self.reps_clusterSequences[clusterId].append(seq)
                    self.reps_clusterSubtypeCounts[clusterId][subType]  = self.reps_clusterSubtypeCounts[clusterId].get(subType ,0) + 1
                    self.reps_sequenceCluster[seq] = clusterId


    def __filterSeqs__(self):
        """ We check cluster to which seq belongs
        and make sure the cluster has seqs from at least 3 samples
        if it doess, the seqeunces is kept """
        passed = []
        for seq in self.reps_sequenceCluster:
            clusterId = self.reps_sequenceCluster[seq]
            if len(self.reps_clusterSubtypeCounts[clusterId]) >= self.MIN_NUM_SEQS:
                passed.append(seq)
        return passed


    def __initSeqSubtypes__(self):
        # {'X1::1234': ['subtype_1", "subtype_2",...], ...}
        sSubtypes={}
        for sample in self.samples:
            # open file exists and add subtypes
            if os.path.exists(os.path.join(self.multiplesDir, sample+".out")):
                for line in open(os.path.join(self.multiplesDir, sample+".out"), 'r'):
                    line = line.rstrip()
                    data = line.split()
                    sSubtypes[data[0]] = data[1:]
        return sSubtypes

    #TODO: Document this thouroughly
    def __computeEffectiveRange__(self, counts, sensitivity=0):
        """
        """
        sortedList = sorted(counts, reverse=True)
        start, end = 1, sortedList[0]
        for val in sortedList[1:]:
            if val > start:
                start = start + 1.0/5 * ((1.0 * val)/end) * (end - start + 1)
        newSart = 1
        for val in sorted(sortedList):
            newStart = val
            if val >= start:
                break
        return (newStart, end)

    def run(self, correctedResultsDir):
        detailedOutputFile  = open(os.path.join( correctedResultsDir, "detailedOutputFile_all_clades" ),  'w')
        correctedOutputFile = open(os.path.join( correctedResultsDir, "correctedOutputFile_all_clades"), 'w')
        resolvedOutputFile  = open(os.path.join( correctedResultsDir, "resolvedOutputFile_all_clades" ),  'w')

        # only sequences that occur in a cluster with at least MIN_NUM_SEQS from other clusters pass
        passedSeqs = self.__filterSeqs__()
        printVerbose(passedSeqs)

        seqSubtypes= self.__initSeqSubtypes__()

        
        # will keep a list of the sequences that were thu sfar processed
        processedSeqs = {}
        subtypeCounts = {}

        # Keep the correct output breakdown by file
        # {'A': file_handle, 'B': file_handle,... }

        splitCorrectedCladeOutputFiles={}
        splitResolvedCladeOutputFiles={}

        # We get one filtered seqeunce at a time. For each filterd sequence, the reps in its cluster
        # for each of the rep, we then process the sequences that were in its cluster at the sample level.
        for passedSeq in passedSeqs:
            # contains the subtupes associated with one cluster of reps (and their representees in the samples)
            subtypes = []

            # number of sequences in a cluster of reps + number of sequences in each of samples they represent
            nbSeqs=0

            if processedSeqs.has_key(passedSeq):
                continue
            clustId =  self.reps_sequenceCluster[passedSeq]


            print >> detailedOutputFile, "#### Cluster: %s" % clustId;
            #### printVerbose(passedSeq)
            # we resolve all the rep sequences that belong to that cluster from which we selected the passedSeq
            
            sampleClust=[]
            for seq in self.reps_clusterSequences[clustId]:
                # Remove seq from later processing since it was found. 
                processedSeqs[seq]= clustId+"_"+passedSeq;
                # which sample does seq belong to?
                sample = seq.split("::")[0]
                clust = self.sample_sequenceCluster[sample][seq]
                sampleClust.append((sample,clust))
                # Which sequences are with seq in the sample  cluster file?
                ####printVerbose("\t"+seq)
                for sampleSeq in self.sample_clustersSeqs[sample][clust]:
                    ####printVerbose("\t\t"+sampleSeq)
                    nbSeqs+=1
                    # we collect all the subtypes that for all the sequences in the same cluster  
                    # for later computing the effective range
                    subtypes.extend(seqSubtypes[sampleSeq])
                ####printVerbose("\n")
            ####printVerbose("\n")


            subtypeCounts = dict(Counter(subtypes))
            # array of counts used to determine the effective lower and upper ranges
            counts=subtypeCounts.values()
            print >> detailedOutputFile, "Cluster: %s\tnumReps: %s\tnumSeq: %s\tsubtypes:" % (clustId, len(self.reps_clusterSequences[clustId]), nbSeqs),
            for (k, v) in  subtypeCounts.items():
                print >> detailedOutputFile, "%s:\t%s," % (k, v),
            print >> detailedOutputFile

            # breakdown number of squences by sample
            countBySamples=defaultdict(int)
            for s,c in sampleClust:
                countBySamples[s] = countBySamples[s]+len(self.sample_clustersSeqs[s][c])

            self.reps_sampleTotalCounts[clustId] = countBySamples
            print >> detailedOutputFile,  "Breakdown by sample: %s " % dict(countBySamples)

            
            #computer the effective range
            effectiveRange = self.__computeEffectiveRange__(counts)
            print >> detailedOutputFile, "The effective range is: %s" % " ".join(map(str, effectiveRange))
            # Get the clade information, check the first letter of the first subtypes in counts list
            clade = subtypeCounts.keys()[0][0]
            print >> detailedOutputFile, "Corrected\tnumSeq: %s\tclade: %s\tsubtypes:" % (nbSeqs, clade),
            
        
            makeDirOrdie(os.path.join(correctedResultsDir, "corrected"))
            makeDirOrdie(os.path.join(correctedResultsDir, "resolved"))




            effectiveSubtypes, filtered = self.__getEffectiveSubtypes__(subtypeCounts, effectiveRange[0]) 

            # if resolved
            if len(effectiveSubtypes.keys()) == 1:

                print >> resolvedOutputFile, "Cluster: %s\tnumSeq: %s\tclade: %s\tbreakDown:%s\tsubtypes:%s" % (
                    clustId, nbSeqs, clade, " ".join(["%s:%s" % (key,val) for (key,val) in self.reps_sampleTotalCounts[clustId].items()]), 
                    " ".join(["%s:%s" %(x,y) for (x,y) in effectiveSubtypes.items()])
                    ),  

                if clade not in splitResolvedCladeOutputFiles.keys():
                    # print the line in the appropriate clade file
                    splitResolvedCladeOutputFiles[clade] = open(os.path.join(correctedResultsDir, "resolved", clade), 'w')
                print >> splitResolvedCladeOutputFiles, "Cluster: %s\tnumSeq: %s\tclade: %s\tbreakDown:%s\tsubtypes:%s" % (
                    clustId, nbSeqs, clade, " ".join(["%s:%s" % (key,val) for (key,val) in self.reps_sampleTotalCounts[clustId].items()]), 
                    " ".join(["%s:%s" %(x,y) for (x,y) in effectiveSubtypes.items()])
                    ),  
            else:

                if clade not in splitCorrectedCladeOutputFiles.keys():
                    # print the line in the appropriate clade file
                    splitCorrectedCladeOutputFiles[clade] = open(os.path.join(correctedResultsDir, "corrected", clade), 'w')
                    printVerbose("*****************print I am here*******************")
                    printVerbose(clade)
                 
                    printVerbose(splitCorrectedCladeOutputFiles)
                    printVerbose("************************************")
                #print >> splitCorrectedCladeOutputFiles[clade], " Cluster: %s\tnumSeq: %s\tclade: %s\tbreakDown:%s\tsubtypes:" % (
                #    clustId, nbSeqs, clade, " ".join(["%s:%s" % (key,val) for (key,val) in self.reps_clusterSubtypeCounts[clustId].items() ])
                #    ),            
                print >> splitCorrectedCladeOutputFiles[clade], " Cluster: %s\tnumSeq: %s\tclade: %s\tbreakDown:%s\tsubtypes:" % (
                    clustId, nbSeqs, clade, " ".join(["%s:%s" % (key,val) for (key,val) in self.reps_sampleTotalCounts[clustId].items()])
                    ),            

                
                
                #print >> correctedOutputFile, "Cluster: %s\tnumSeq: %s\tclade: %s\tbreakDown:%s\tsubtypes:" % (
                #    clustId, nbSeqs, clade, " ".join(["%s:%s" % (key,val) for (key,val) in self.reps_clusterSubtypeCounts[clustId].items() ])
                #    ),
                print >> correctedOutputFile, "Cluster: %s\tnumSeq: %s\tclade: %s\tbreakDown:%s\tsubtypes:" % (
                    clustId, nbSeqs, clade, " ".join(["%s:%s" % (key,val) for (key,val) in self.reps_sampleTotalCounts[clustId].items()])
                    ),

                for (k,v) in effectiveSubtypes.items():
                    # printing to bow files the detailed output and the just the correct information
                    print >> detailedOutputFile, "%s: %s," % (k, v),
                    print >> correctedOutputFile, "%s: %s," % (k, v),
                    print >> splitCorrectedCladeOutputFiles[clade], "%s: %s," % (k, v),

                print >> detailedOutputFile, "filtered are: %s" % " ".join(filtered)
                print >> correctedOutputFile, ""
                print >> splitCorrectedCladeOutputFiles[clade], ""
        detailedOutputFile.close()
        correctedOutputFile.close()
        resolvedOutputFile.close()
        
        # close all the split files that have been open
        [splitCorrectedCladeOutputFiles[cl].close() for cl in splitCorrectedCladeOutputFiles.keys()]
        [splitResolvedCladeOutputFiles[cl].close() for cl in splitResolvedCladeOutputFiles.keys()]

        
    def dryRun(self):
        pass
