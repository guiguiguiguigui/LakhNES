from __future__ import print_function
import sys

from tx1_midi import tx1_to_midi
from tx2_midi import tx2_to_midi


tx_in_fp= sys.argv[1]


if 'tx1' in tx_in_fp:
  with open(tx_in_fp, 'r') as f:
    tx1 = f.read()
  midi = tx1_to_midi(tx1)
else:
  with open(tx2_fp, 'r') as f:
    tx2 = f.read()
  midi = tx2_to_midi(tx2)


mid_out_fp ="."+ tx_in_fp.split('.')[1]+".mid"
with open(mid_out_fp, 'wb') as f:
  f.write(midi)

