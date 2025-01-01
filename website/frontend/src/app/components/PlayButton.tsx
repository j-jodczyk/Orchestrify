'use client';

import React from 'react';
import { Midi } from '@tonejs/midi';
import * as Tone from 'tone';

interface PlayButtonProps {
  midiBlob: Blob | null;
}

const PlayButton: React.FC<PlayButtonProps> = ({ midiBlob }) => {

  const playMidi = async () => {
    if (midiBlob) {
      const midiBuffer = await midiBlob.arrayBuffer();
      const midi = new Midi(midiBuffer);
      const now = Tone.now();
      midi.tracks.forEach((track) => {
        track.notes.forEach((note) => {
          Tone.Transport.scheduleOnce(() => {
            const synth = new Tone.Synth().toDestination();
            synth.triggerAttackRelease(note.name, note.duration, now + note.time);
          }, note.time);
        });
      });
      Tone.Transport.start();
    }
  };

  return (
  <button
    className={`text-center w-40 p-2 rounded-lg my-10 ${midiBlob ? 'bg-secondary-300' : 'bg-secondary-700'} `}
    onClick={playMidi}
    disabled={!midiBlob}
  >
    PLAY
  </button>)
};

export default PlayButton;
