'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { useDropzone } from 'react-dropzone';
import { Midi } from '@tonejs/midi'
import { error } from 'console';

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

interface FormValues {
  density: string;
  model: string;
  file: File | null;
}

const validationSchema = Yup.object({
  density: Yup.number()
    .min(0, 'Density must be at least 0')
    .max(1, 'Density must not exceed 1')
    .required('Density is required'),
  model: Yup.string().required('Model selection is required'),
  file: Yup.mixed().required('File is required'),
});


const UploadForm: React.FC = () => {
  const [serverResponse, setServerResponse] = useState<string | null>(null);
  const [models, setModels] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/models', {
      method: 'GET'
    })
    .then(response => response.json())
    .then(jsonResponse => {
      setModels(jsonResponse.models) // todo: error handling
    });
  }, [])

  return (
    <div className='m-8'>
      <Formik<FormValues>
        initialValues={{
          density: '',
          model: '',
          file: null,
        }}
        validationSchema={validationSchema}
        onSubmit={async (values, { setSubmitting, resetForm }) => {
          const formData = new FormData();
          formData.append('model', values.model);
          formData.append('density', values.density.toString());
          formData.append('file', values.file as File);

          try {
            const response = await fetch('http://localhost:8000/generate', {
              method: 'POST',
              body: formData,
            });

            if (!response.ok) {
              throw new Error(`Server responded with status ${response.status}`);
            }

            const midiBlob = await response.blob();
            const midiUrl = URL.createObjectURL(midiBlob);

            setServerResponse(midiUrl);
          } catch(err: any) {
            setServerResponse(`Error: ${err.message}`);
          } finally {
            setSubmitting(false);
            resetForm();
          }
        }}
        >
          {({ setFieldValue, isSubmitting, values }) => {
          const { getRootProps, getInputProps, isDragActive } = useDropzone({
            onDrop: (acceptedFiles: File[]) => {
              if (acceptedFiles.length > 0) {
                setFieldValue('file', acceptedFiles[0]);
              }
            },
            multiple: false,
            accept: '.midi,.mid',
          });

          return (
            <Form className='justify-items-center font-roboto'>
              <div className='m-4'>
                <div className='flex gap-4'>
                  <label htmlFor="density" >
                    Density (0 to 1)
                  </label>
                  <Field
                    className='rounded border-none text-black pl-2'
                    type="number"
                    id="density"
                    name="density"
                    step="0.01"
                  />
                </div>
                <ErrorMessage name="density" component="div" className='text-primary-300 text-center mt-2'/>
              </div>

              <div className='m-4'>
                <div className='flex gap-4'>
                  <label htmlFor="model">
                    Select Model:
                  </label>
                  <Field
                    className='rounded border-none text-black px-2'
                    as="select"
                    id="model"
                    name="model"
                  >
                    <option value="" label="Select model" />
                    {models.map(model =>
                      <option key={`model-${model}`} value={model} label="Lakh" />
                    )}
                  </Field>
                </div>
                <ErrorMessage name="model" component="div" className='text-primary-300 text-center mt-2'/>
              </div>

              <div
              className='h-56 bg-[hsl(245,23%,72%,20%)] m-6 p-8 text-center content-center rounded-lg w-full'
                {...getRootProps()}
              >
                <input {...getInputProps()} />
                {values.file ? (
                  <p>File: {(values.file as File).name}</p>
                ) : (
                  <p>Drag and drop a file here, or click to select one</p>
                )}
              </div>
              <ErrorMessage name="file" component="div" />

              <button
                type="submit"
                disabled={isSubmitting}
                className='bg-accent-300 text-center w-40 p-2 rounded-lg'
              >
                {isSubmitting ? 'LOADING...' : 'GENERATE'}
              </button>

              {/* Server Response */}
              {serverResponse && (
                <div              >
                  {serverResponse.startsWith('Error') ? (
                    serverResponse
                  ) : (
                    <div className='flex gap-4'>
                      <div className='bg-secondary-300 text-center w-40 p-2 rounded-lg my-10'>
                        {/* TODO: actually play */}
                          PLAY
                      </div>
                      <div className='bg-secondary-300 text-center w-40 p-2 rounded-lg my-10'>
                        <a
                          href={serverResponse}
                          download="generated.mid"
                        >
                          DOWNLOAD
                        </a>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </Form>
          );
        }}
        </Formik>
      </div>
  )
}

export default UploadForm;
