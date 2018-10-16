msg='9979999   BW testing for convergence rate etc.'
python tl_bw_test.py  0.00 "$msg" & python tl_bw_test.py  0.1 "$msg"& python tl_bw_test.py  0.2 "$msg"& python tl_bw_test.py  0.50 "$msg" & python tl_bw_test.py  6.0 "$msg" &
 
