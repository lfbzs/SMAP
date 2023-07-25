from mido import Message, MidiTrack



def make_track(_score,meta_time,program=0):
    track = MidiTrack()
    no=program
    last=0
    for i in range(0,len(_score)):
        ch=_score[i]
        if ch[0] == '$':
            no = int(ch[1:])
            continue
        if ch == 'Rests16':
            track.append(Message('note_off', note=last, velocity=127, time=round(0.25*meta_time),channel=0))
            continue
        if ch == 'Rests8':
            track.append(Message('note_off', note=last, velocity=127, time=round(0.5*meta_time),channel=0))
            continue
        if ch == 'Rests4':
            track.append(Message('note_off', note=last, velocity=127, time=round(1*meta_time),channel=0))
            continue
        if ch == 'Rests2':
            track.append(Message('note_off', note=last, velocity=127, time=round(2*meta_time),channel=0))
            continue
        if ch == 'Rests1':
            track.append(Message('note_off', note=last, velocity=127, time=round(4*meta_time),channel=0))
            continue
        if int(ch[0]):
            track.append(Message('program_change',channel=0,program=no,time=0))
            track.append(Message('note_on', note=int(ch[0]), velocity=64, time=0,channel=0))
            last=int(ch[0])
        try:
            if int(_score[i+1][0]):
                track.append(Message('note_off', note=int(ch[0]), velocity=64,
                                     time=round(0.5*_score[i][1]*meta_time),channel=0))
        except Exception:
            pass
    return track
