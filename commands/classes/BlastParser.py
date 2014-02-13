## if length(query) > lenght(hit)
##    hit must completely align 100% with query with 97%.
## else (length(query) < lenght(hit)):
##     If length(query) > 0.90 lenght(hit))
##        then apply the formula for Adaptive Similarity Score
##      Length        0.9 length(hit)             0.95 length(hit)            0.999999 length(hit)
##      Similarity      100%                          98.5%                           97%
##     else
##        Query is too short
## A short sequence can never be EXACT. However, a short sequence can be UNIQUE if it is >= 0.9 * length(hit) but < Adaptive Similarity Score

## TODO: convert the blast identity to real scores
## TODO: Check cases where we are multiple perfect.

from Bio import SearchIO
import os
import sys

class BlastParser(object):
    def __init__(self, inFile, outputDirPath, minEval=1e-20, minIdentity=0.97, minCoverage = 0.96):
        self.inFile = inFile
        self.outputDirPath = outputDirPath
        self.minEval= minEval
        self.minIdentity = minIdentity
        self.minCoverage = minCoverage
        self.perfect, self.unique, self.multiple, self.short, self.new, self.shortnew = (None, None, None, None, None, None)

    def __openOutputFiles__(self):
        self.perfect = open(os.path.join(self.outputDirPath, "PERFECT", os.path.basename(self.inFile)), 'w') 
        self.unique = open(os.path.join(self.outputDirPath, "UNIQUE", os.path.basename(self.inFile)), 'w') 
        self.multiple = open(os.path.join(self.outputDirPath, "MULTIPLE", os.path.basename(self.inFile)), 'w') 
        self.short = open(os.path.join(self.outputDirPath, "SHORT", os.path.basename(self.inFile)), 'w') 
        self.new = open(os.path.join(self.outputDirPath, "NEW", os.path.basename(self.inFile)), 'w') 
        self.shortnew = open(os.path.join(self.outputDirPath, "SHORTNEW", os.path.basename(self.inFile)), 'w') 

    def __closeOutputFiles__(self):        
        self.perfect.close()
        self.unique.close()
        self.multiple.close()
        self.short.close()
        self.new.close()
        self.shortnew.close()

    def run(self):
        self.__openOutputFiles__()
        myIn = SearchIO.parse(self.inFile, "blast-text")
        for result in myIn:
            results=[];
            perfectHits=[];
            has_perfect_hit=False;
            has_hit=False;
            stop=False;
            oldBits=-1;


            if len(result.hits)==0:
                print >> self.new, "%s, No Blast hit" % result.id

            for hit in result.hits:
                if len(hit.hsps):
                    hsp = hit.hsps[0]
                else:
                    break;
                # This is a test measure since we are not sure how to deal with fragmented HSPs
                assert not hsp.is_fragmented
                pctIdent = float(hsp.ident_num)/hsp.aln_span
                oldBits = hsp.bitscore;
                if(result.seq_len >= hit.seq_len):
                    # query sequence is longer that db sequence
                    if (not has_perfect_hit) and ( pctIdent > self.minIdentity)  and ((float(hsp.hit_span + 1) / hit.seq_len) > self.minCoverage):
                        # perfect hit needs to have 100 similarity over at least minCoverage (96% default)
                        if pctIdent == 100: 
                            perfectHits.append(hit.id)
                            has_perfect_hit = True
                            stop=True
                            break

                        # only results equal to the previous oldbits are appended 
                        if hsp.bitscore == oldBits:
                            results.append(hit.id)
                            has_hit = True
                        else:
                            stop = True
                    else:
                        if not (has_perfect_hit or has_hit):
                            # report that lenght(query) > lenght(hit) but hit does not
                            # align with at least 97% similarity over 96% of the sequence
                            print >> self.new,  result.id
                            stop = True
                else:
                    # query sequence is shorter that db sequence
                    # only process if the sequence does not already have hits 
                    # and is at least 0.9 * the length of the hit sequence
                    if not has_hit:
                        # adaptive smilarity formula. A sequence that exactly the same lengtht he hit sequence is required 
                        # to align with less similarity than one that is shorter
                        if result.seq_len >= 0.90 * hit.seq_len:
                            sim = (((result.seq_len/ hit.seq_len) - 0.9)/(1-.09)) * (100 - 97)
                            if ( pctIdent > (sim + 97)):
                                # Passes as short hit
                                results.append(hit.id)
                                has_hit=True
                            else:
                                # Does not pass as short hit
                                print >> self.shortnew, ("%s\t%s\t%s\t%s") % (result.id, hit.id, (float(result.seq_len)/hit.seq_len), pctIdent) 
                                stop = 1
                        else:
                            print >> self.short, "%s\t%s\t%s\t%s" % (result.id, result.seq_len, hit.id, hit.seq_len)
                            stop=1;
                if stop:
                    break    
            if len(perfectHits) >= 1:
                print >> self.perefect,  "%s\t%s" % (result.id," ".join(perfectHits))
            elif len(results) == 1:
                print >> self.unique,  "%s\t%s" % (result.id," ".join(results))
            elif(len(results) >1):
                print >> self.multiple, "%s\t%s" % (result.id," ".join(results))
        self.__closeOutputFiles__()

    def dryRun(self):
        return   "Parsing blast output for sample %s, minEval=%s,minIdentity=%s, minCoverage=%s" % (self.inFile, self.minEval, self.minIdentity, self.minCoverage)
