'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import '@fontsource/roboto';
import UploadForm from './components/UploadForm';



// TODO: display error and success messages

const HomePage: React.FC = () => {
  return (
    <div
      className='bg-background-800 h-screen text-white font-roboto content-center justify-items-center'
    >
      <h1
        className='pt-6 text-center text-7xl'
      >
        ORCHESTRIFY
      </h1>
      <p className='text-center text-accent-200 pt-8'>Create an accompaniament for a midi file!</p>
      {/* TODO: at the beginning fetch models and give choice of them */}
      <UploadForm />

      {
      // midiUrl && (
      //   <div className='flex gap-2 mt-10'>
      //     {/* TODO: this does not work */}
      //     <button
      //       onClick={() => {
      //         const audio = new Audio(midiUrl);
      //         audio.play();
      //       }}
      //       className='bg-accent-300 text-center w-40 p-2 rounded-lg'
      //     >
      //       Play MIDI
      //     </button>
      //     <button
      //       className='bg-accent-300 text-center w-40 p-2 rounded-lg'
      //     ><a
      //       href={midiUrl}
      //       download="generated.mid"
      //     >
      //       Download MIDI
      //     </a></button>
      //   </div>
      // )
      }
    </div>
  );
};

export default HomePage;
