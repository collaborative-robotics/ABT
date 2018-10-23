

# task01    SMALL   BaumWelch
# task02    SMALL   Viterbi
# task03    BIG     BaumWelch
# task04    BIG     Viterbi


cp task01.py abt_constants.py

msg='-*-*-*-*   New: multinomialHMM()   6-state BW: task01 6-State BW New B-pert'
python tl_abt2hmm.py  0.00 "$msg" & python tl_abt2hmm.py  0.1 "$msg"& python tl_abt2hmm.py  0.2 "$msg"& python tl_abt2hmm.py  0.50 "$msg" & python tl_abt2hmm.py  6.0 "$msg" 
 
 
cp task02.py abt_constants.py

msg='-*-*-*-*   New: multinomialHMM()   6-state BW: task02 6-state Vit New B-pert'
python tl_abt2hmm.py  0.00 "$msg" & python tl_abt2hmm.py  0.1 "$msg"& python tl_abt2hmm.py  0.2 "$msg"& python tl_abt2hmm.py  0.50 "$msg" & python tl_abt2hmm.py  6.0 "$msg" 
 

cp task03.py abt_constants.py

msg='-*-*-*-*   New: multinomialHMM()   6-state BW: task03 16-state BW New B-pert'
python tl_abt2hmm.py  0.00 "$msg" & python tl_abt2hmm.py  0.1 "$msg"& python tl_abt2hmm.py  0.2 "$msg"& python tl_abt2hmm.py  0.50 "$msg" & python tl_abt2hmm.py  6.0 "$msg" 
 

cp task04.py abt_constants.py

msg='-*-*-*-*   New: multinomialHMM()   6-state BW: task04 16-state Vit New B-pert'
python tl_abt2hmm.py  0.00 "$msg" & python tl_abt2hmm.py  0.1 "$msg"& python tl_abt2hmm.py  0.2 "$msg"& python tl_abt2hmm.py  0.50 "$msg" & python tl_abt2hmm.py  6.0 "$msg" 
 
