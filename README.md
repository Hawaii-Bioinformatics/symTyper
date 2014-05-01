## Description
Some description here.

## Dependencies
* Python 2.7
* Python pacakges in requirements.txt


## Pipeline Flow
```
symTyper.py -t 6 clade -i sample.fasta -s sample.ids --hmmdb  database_20140212/HMMER_ITS2_DB/All_Clades.hmm
symTyper.py -t 6 subtype -H hmmer_hits/ -s %s -b blast_output/ -r blastResults/ -f fasta --blastdb database_20140212/blast_DB/ITS2_Database_04_23_13.fas
symTyper.py -t 6  resolveMultipleHits -s sample.ids -m blastResults/MULTIPLE/ -c resolveMultiples/
symTyper.py -t 6 buildPlacementTree -c resolveMultiples/correctedMultiplesHits/corrected -n  database_20140212/clades_phylogenies -o placementInfo
symTyper.py -t 6 stats --outputs_dir . -i sample.fasta --out_file ./outputfile
symTyper.py -t 6 makeBiom --outputs_dir .
```

## Output
All output is generated relative to the directory in which the script is executed.  Each step in the pipeline depends on specific folder/file structure in order to
operate correctly. 

## Command arguments


### clade
```
usage: symTyper.py clade [-h] -s SAMPLESFILE -i INFILE [-e EVALUE] [-d EVALDIFFERENCE] --hmmdb HMMDB

optional arguments:
  -h, --help            show this help message and exit
  -s SAMPLESFILE, --samplesFile SAMPLESFILE
                        Samples file
  -i INFILE, --inFile INFILE
                        Input fasta file
  -e EVALUE, --evalue EVALUE
  -d EVALDIFFERENCE, --evalDifference EVALDIFFERENCE
                        Eval difference between first and second hits
  --hmmdb HMMDB         Path to the hmm database
```
### subtype
```
usage: symTyper.py subtype [-h] -s SAMPLESFILE -H HITSDIR -b BLASTOUTDIR -r BLASTRESULTS -f FASTAFILESDIR --blastdb BLASTDB

optional arguments:
  -h, --help            show this help message and exit
  -s SAMPLESFILE, --samplesFile SAMPLESFILE
                        Samples file
  -H HITSDIR, --hitsDir HITSDIR
                        hmmer fasta hits ouput directory
  -b BLASTOUTDIR, --blastOutDir BLASTOUTDIR
                        blast ouput directory
  -r BLASTRESULTS, --blastResults BLASTRESULTS
                        parsed blast results directory
  -f FASTAFILESDIR, --fastaFilesDir FASTAFILESDIR
                        Split fasta files directory
  --blastdb BLASTDB     Path to the blast database
```

### resolveMultipleHits
```
usage: symTyper.py resolveMultipleHits [-h] -s SAMPLESFILE -m MULTIPLEDIR -c CLUSTERSDIR

optional arguments:
  -h, --help            show this help message and exit
  -s SAMPLESFILE, --samplesFile SAMPLESFILE
                        Samples file
  -m MULTIPLEDIR, --multipleDir MULTIPLEDIR
                        Directory containing fasta sequences that yielded
                        multiple hits
  -c CLUSTERSDIR, --clustersDir CLUSTERSDIR
                        Dir that will contain cluster information
```

### buildPlacementTree
```
usage: symTyper.py buildPlacementTree [-h] -c CORRECTEDRESULTSDIR -n NEWICKFILESDIR -o OUTPUTDIR

optional arguments:
  -h, --help            show this help message and exit
  -c CORRECTEDRESULTSDIR, --correctedResultsDir CORRECTEDRESULTSDIR
                        Directory containing corrected Clade placements
  -n NEWICKFILESDIR, --newickFilesDir NEWICKFILESDIR
                        Newick directory with files having format info_clade.nwk
  -o OUTPUTDIR, --outputDir OUTPUTDIR
                        Dir that will contain the newick and interenal nodes information
```

### stats
```
usage: symTyper.py stats [-h] -i INFILE --outputs_dir OUTPUTS_DIR --out_file OUT_FILE

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --inFile INFILE
                        Input fasta file
  --outputs_dir OUTPUTS_DIR
                        Path to the directory contains the output files
  --out_file OUT_FILE   Output stats files where results will be printed
```

### makeBiom
```
usage: symTyper.py makeBiom [-h] --outputs_dir OUTPUTS_DIR

optional arguments:
  -h, --help            show this help message and exit
  --outputs_dir OUTPUTS_DIR
                        Path to the directory contains the output files

```

