import os
import sys

import pygame
from mido import MidiFile
from midi2audio import FluidSynth

from utils.score import Make_score
from utils.track import make_track

def Write_MID(score,meta_time,save_path):
    mid = MidiFile()
    track1 = make_track(score,meta_time)
    mid.tracks.append(track1)
    mid.save(save_path)

def make_midi(music_mung_path,save_path,meta_time,musical = 'Acoustic_Grand_Piano'):
    score = Make_score(music_mung_path,musical)
    Write_MID(score,meta_time,save_path)

if __name__ == '__main__':
    mung_path = 'runs/detect/exp19/mung/000002.txt'
    meta_time = 60 * 60 * 10 / 75
    save_path = "mid_file/000002.mid"
    make_midi(mung_path,save_path,meta_time)
    os._exit(0)
