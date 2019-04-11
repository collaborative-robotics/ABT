#!/bin/sh
#
#    Run all the hmm tests 
#

set -e  #  have to use >bash test_all.sh  
        #   NOT  >source test_all.sh

python test_hmm_init.py
python test_hmm_pert.py
python test_hmm_rand_pert.py
python test_obs_stats.py  TSTstatelog.txt
python test_random.py
python test_seq_stats.py  TSTstatelog.txt
python test_forward.py
python test_decode_eval.py

echo '---------------------------------------------------------------'
echo '   (hmm-bt software)'
echo ''
echo '       ALL test_all.sh TESTS PASSED '
echo ''
echo ''
echo '---------------------------------------------------------------'




