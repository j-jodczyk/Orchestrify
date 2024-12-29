'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import '@fontsource/roboto';

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

const HomePage: React.FC = () => {
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<Blob | null>(null);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setError(null);
    setSuccessMessage(null);

    if (rejectedFiles.length > 0) {
      setError("File rejected. Please ensure it meets all requirements.");
      return;
    }

    const file = acceptedFiles[0];
    if(!file) {
      setError("No file uploaded.")
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setError("File is too large. Maximum size is 5MB.");
      return;
    }

    if (!file.type.startsWith('audio/midi') && !/\.(midi|mid)$/i.test(file.name)) {
      setError('Invalid file type. Only MIDI files are allowed.');
      return;
    }

    setSuccessMessage(`File "${file.name}" uploaded successfully!`);
    setUploadedFile(file);
  }, []);

  const onClick = useCallback(async () => {
    console.log("hello")
    if (!uploadedFile) {
      setError("No file uploaded.")
      return;
    }

    const formData = new FormData();
    formData.append('model', 'Lakh');
    formData.append('density', '0.5');
    formData.append('file', uploadedFile);

    try {
      const response = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }

      const result = await response.json();
      setSuccessMessage(`File uploaded and processed successfully! Response: ${JSON.stringify(result)}`);
      console.log('Response:', result);
    } catch(err: any) {
      setError(`Failed to upload and process the file: ${err.message}`);
    }
  }, []);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    multiple: false,
    maxSize: MAX_FILE_SIZE,
    accept: {
      'audio/midi': ['.midi', '.mid'],
    },
  });

  return (
    <div
      className='bg-background-800 h-screen text-white font-roboto content-center justify-items-center'
    >
      <h1
        className='pt-8 text-center text-5xl'
      >
        ORCHESTRIFY
      </h1>
      <p className='text-center text-accent-200 pt-8'>Create an accompaniament for a midi file!</p>
      {/* TODO: at the beginning fetch models and give choice of them */}
      <div
        className='h-1/5 bg-[hsl(245,23%,72%,20%)] m-8 p-8 text-center content-center rounded-lg'
        {...getRootProps()}
      >
        <input {...getInputProps()} />
          <p>Drop the files here, or click to select from device...</p>
      </div>
      <button
        disabled={uploadedFile==null}
        className='bg-primary-500 text-center w-40 p-2 rounded-lg'
        onClick={onClick}
        // todo: button should have a different color when disabled
      >GENERATE</button>
    </div>
  );
};

export default HomePage;
