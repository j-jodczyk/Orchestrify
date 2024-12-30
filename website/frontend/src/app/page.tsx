'use client';

import { useState } from 'react';
import '@fontsource/roboto';
import UploadForm, { MidiData } from './components/UploadForm';
import PlayButton from './components/PlayButton';


const HomePage: React.FC = () => {
  const [midiData, setMidiData] = useState<MidiData|null>(null);

  const onFormSubmit = async (respData: MidiData) => {
    setMidiData(respData);
  }

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
      <UploadForm onFormSubmit={onFormSubmit}/>
      {midiData && (
        <div>
          <p>Generated accompaniament for original file {midiData.fileName}</p>
          <div className='flex gap-4 justify-center'>
            <PlayButton midiBlob={midiData.blob} />
            <div className='bg-secondary-300 text-center w-40 p-2 rounded-lg my-10'>
              <a
                href={midiData.fileUrl}
                download="generated.mid"
              >
                DOWNLOAD
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;
