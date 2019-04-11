#!/bin/sh
#
#    Run all the hmm tests 
#

python test_hmm_pert.py
python test_hmm_rand_pert.py
python test_obs_stats.py  TSTstatelog.txt
python test_random.py
python test_seq_stats.py  TSTstatelog.txt 


