#!/usr/bin/python
#
#   Test observation stats 
#    generated

import sys
import os
import glob
import time

REALMODE = False

vit_dir = 'vit_output/'
bw_dir = 'bw_output/'

seqdir  = 'sequences/'

#urunid = str(uuid.uuid4())  # a unique hash code for this run 

##if these don't exist, create them 
#for ndir in [datadir, seqdir]:
    #if not (os.path.exists(os.path.dirname(ndir))):
        #os.mkdir(ndir)





#  Metadata file cleanup and sorting
#
metadata_name = 'metadata.txt'
# Metadata file format:  each line: (comma sep)
#
#  0) date and time stamp
#  1) name of data file
#  2) ownname  (name of the top level file)
#  3) git hash (1st 10 chars of current git hash)
#  4) number of HMM / BT states
#  5) text field (comment)
#


#  Purge Empty data files



#datafile_name = datadir+'data_'+urunid+'.csv'  # a unique filename


ndel = 0

# purge zero length files (from crashed or ^c'ed runs)
for dir in [vit_dir, bw_dir]:
    dirlist = glob.glob(dir+'*')
    for f in dirlist:
        d = os.stat(f)  # check file size
        if int(d.st_size) < 1:
            #print 'ZERO SIZE: ',f
            print 'Planning to remove:          ', f,' because ', d.st_size , 'bytes'
            if(REALMODE):
                os.remove(f)
            ndel += 1
      

################################################
##   Delete Sequence data more than 1 wk old
current_time = time.time()
for f in glob.glob(seqdir+'*'):
    creation_time = os.path.getctime(f)
    if (current_time - creation_time) // (24 * 3600) >= 7:
        if(REALMODE):
            os.unlink(f)
        print 'designating {} to be removed'.format(f)
        ndel += 1
        
        
        
print '\n\n\n'
if not REALMODE:
    print '         Fake mode - no actual deletions '
print 'Deleted: ', ndel, ' files'
