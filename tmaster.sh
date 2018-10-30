

# task01    SMALL   BaumWelch
# task02    SMALL   Viterbi
# task03    BIG     BaumWelch
# task04    BIG     Viterbi


cp task01.py abt_constants.py

msg='--*---GIX Tue----*----   multinomial (new init + commented checker)  6 state BW: task01 '
python tl_abt2hmm.py  0.00 "$msg" & python tl_abt2hmm.py  0.1 "$msg"& python tl_abt2hmm.py  0.2 "$msg"& python tl_abt2hmm.py  0.50 "$msg" & python tl_abt2hmm.py  6.0 "$msg" 
 
 
cp task02.py abt_constants.py

msg='--*---GIX Tue----*----   multinomial (new init + commented checker)  6 state Vit: task02 '
python tl_abt2hmm.py  0.00 "$msg" & python tl_abt2hmm.py  0.1 "$msg"& python tl_abt2hmm.py  0.2 "$msg"& python tl_abt2hmm.py  0.50 "$msg" & python tl_abt2hmm.py  6.0 "$msg" 
 

cp task03.py abt_constants.py

msg='--*---GIX Tue----*----   multinomial (new init + commented checker)  16 state BW: task03'
python tl_abt2hmm.py  0.00 "$msg" & python tl_abt2hmm.py  0.1 "$msg"& python tl_abt2hmm.py  0.2 "$msg"& python tl_abt2hmm.py  0.50 "$msg" & python tl_abt2hmm.py  6.0 "$msg" 
 

cp task04.py abt_constants.py

msg='--*---GIX Tue----*----   multinomial (new init + commented checker)  16 state Vit: task04'
python tl_abt2hmm.py  0.00 "$msg" & python tl_abt2hmm.py  0.1 "$msg"& python tl_abt2hmm.py  0.2 "$msg"& python tl_abt2hmm.py  0.50 "$msg" & python tl_abt2hmm.py  6.0 "$msg" 
 
