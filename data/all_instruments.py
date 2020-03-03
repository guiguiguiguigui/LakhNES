import itertools
import os

import pretty_midi
pretty_midi.pretty_midi.MAX_TICK = 1e16
import random
import json

nes_ins_name_to_min_pitch = {
    'p1': 33,
    'p2': 33,
    'tr': 21
}
nes_ins_name_to_max_pitch = {
    'p1': 108,
    'p2': 108,
    'tr': 108
}


def instrument_is_monophonic(ins):
  # Ensure sorted
  notes = ins.notes
  last_note_start = -1
  for n in notes:
    assert n.start >= last_note_start
    last_note_start = n.start

  monophonic = True
  for i in range(len(notes) - 1):
    n0 = notes[i]
    n1 = notes[i + 1]
    if n0.end > n1.start:
      monophonic = False
      break
  return monophonic


def all_instruments(
    midi_fp,
    output_dir,
    min_num_instruments=1,
    filter_mid_len_below_seconds=5.,
    filter_mid_len_above_seconds=600.,
    filter_mid_bad_times=True,
    filter_ins_max_below=21,
    filter_ins_min_above=108,
    filter_ins_duplicate=True,
    output_include_drums=True,
    output_max_num=16,
    output_max_num_seconds=180.):
  midi_name = os.path.split(midi_fp)[1].split('.')[0]

  if min_num_instruments <= 0:
    raise ValueError()

  # Ignore unusually large MIDI files (only ~25 of these in the dataset)
  if os.path.getsize(midi_fp) > (512 * 1024): #512K
    return

  try:
    midi = pretty_midi.PrettyMIDI(midi_fp)
  except:
    return

  # Filter MIDIs with extreme length
  midi_len = midi.get_end_time()
  if midi_len < filter_mid_len_below_seconds or midi_len > filter_mid_len_above_seconds:
    return

  # Filter out negative times and quantize to audio samples
  for ins in midi.instruments:
    for n in ins.notes:
      if filter_mid_bad_times:
        if n.start < 0 or n.end < 0 or n.end < n.start:
          return
      n.start = round(n.start * 44100.) / 44100.
      n.end = round(n.end * 44100.) / 44100.

  instruments = midi.instruments

  # Filter out drum instruments
  drums = [i for i in instruments if i.is_drum]
  instruments = [i for i in instruments if not i.is_drum]

  # Filter out instruments with bizarre ranges
  instruments_normal_range = []
  for ins in instruments:
    pitches = [n.pitch for n in ins.notes]
    min_pitch = min(pitches)
    max_pitch = max(pitches)
    if max_pitch >= filter_ins_max_below and min_pitch <= filter_ins_min_above:
      instruments_normal_range.append(ins)
  instruments = instruments_normal_range
  if len(instruments) < min_num_instruments:
    return

  # Sort notes for polyphonic filtering and proper saving
  for ins in instruments:
    ins.notes = sorted(ins.notes, key=lambda x: x.start)
  if output_include_drums:
    for ins in drums:
      ins.notes = sorted(ins.notes, key=lambda x: x.start)

  # Filter out polyphonic instruments
  monophonic = []
  polyphonic = []
  for i in instruments:
    if instrument_is_monophonic(i):
      monophonic.append(i.name)
    else:
      polyphonic.append(i.name)
  dr = [i.name for i in drums]
  
  out_fp = '{}.json'.format(midi_name)
  out_fp = os.path.join(output_dir, out_fp)

  names = {"mono":monophonic, "poly":polyphonic, "drums":dr}
  with open(out_fp, 'w') as f:
    json.dump(names, f)



if __name__ == '__main__':
  import glob
  import shutil
  import multiprocessing

  import numpy as np
  import pretty_midi
  from tqdm import tqdm

  midi_fps = glob.glob('./lakh/clean_midi/*/*.mid*')
  out_dir = './out/inst'

  if os.path.isdir(out_dir):
    shutil.rmtree(out_dir)
  os.makedirs(out_dir)

  def _task(x):
    all_instruments(x, out_dir)

  with multiprocessing.Pool(4) as p:
    r = list(tqdm(p.imap(_task, midi_fps), total=len(midi_fps)))
