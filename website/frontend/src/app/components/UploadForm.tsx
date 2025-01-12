"use client";

import React, { useState, useEffect } from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import { useDropzone } from "react-dropzone";
import { toast, ToastContainer, ToastOptions } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const MAX_FILE_SIZE = 50 * 1024; // 5KB

interface FormValues {
  density: string;
  model: string;
  file: File | null;
}

export interface MidiData {
  blob: Blob;
  fileName: string | null;
  fileUrl: string;
}

interface UploadFormProps {
  onFormSubmit: (res: MidiData) => void;
}

const validationSchema = Yup.object({
  density: Yup.number()
    .min(0, "Density must be at least 0")
    .max(1, "Density must not exceed 1")
    .required("Density is required"),
  model: Yup.string().required("Model selection is required"),
  file: Yup.mixed()
    .required("File is required")
    .test(
      "fileSize",
      "File size is too large, maximum size is 50 kB",
      (value: any) => {
        return value && value.size <= MAX_FILE_SIZE;
      },
    ),
});

const toastErrorParams: ToastOptions = {
  position: "top-center",
  autoClose: 5000,
  closeOnClick: true,
  pauseOnHover: true,
  hideProgressBar: true,
};

const UploadForm: React.FC<UploadFormProps> = ({ onFormSubmit }) => {
  const [models, setModels] = useState<Array<string>>([]);

  useEffect(() => {
    fetch("http://localhost:8000/models", {
      method: "GET",
    })
      .then((response) => response.json())
      .then((jsonResponse) => {
        setModels(jsonResponse.models);
      })
      .catch(() => {
        toast.error("Failed to fetch models list", toastErrorParams);
      });
  }, []);

  return (
    <div className="m-8">
      <Formik<FormValues>
        initialValues={{
          density: "",
          model: "",
          file: null,
        }}
        validationSchema={validationSchema}
        onSubmit={async (values, { setSubmitting, resetForm }) => {
          const formData = new FormData();
          const file = values.file as File;
          formData.append("model", values.model);
          formData.append("density", values.density.toString());
          formData.append("file", file);

          try {
            const response = await fetch("http://localhost:8000/generate", {
              method: "POST",
              body: formData,
            });

            if (!response.ok) {
              const responseJson = await response.json();
              toast.error(
                `Error generating file: ${responseJson.detail}`,
                toastErrorParams,
              );
              return;
            }

            const midiResBlob = await response.blob();
            const midiUrl = URL.createObjectURL(midiResBlob);

            onFormSubmit({
              blob: midiResBlob,
              fileName: file.name,
              fileUrl: midiUrl,
            });
          } catch (err: any) {
            console.log(err);
            toast.error(`Failed to generate midi file`, toastErrorParams);
          } finally {
            setSubmitting(false);
            resetForm();
          }
        }}
      >
        {({ setFieldValue, isSubmitting, values }) => {
          const { getRootProps, getInputProps } = useDropzone({
            onDrop: (acceptedFiles: File[]) => {
              if (acceptedFiles.length > 0) {
                setFieldValue("file", acceptedFiles[0]);
              }
            },
            multiple: false,
            accept: { "audio/midi": [".midi", ".mid"] },
          });

          return (
            <Form className="justify-items-center font-roboto">
              <div className="m-4">
                <div className="flex gap-4">
                  <label htmlFor="density">Density (0 to 1)</label>
                  <Field
                    className="rounded border-none text-black pl-2"
                    type="number"
                    id="density"
                    name="density"
                    step="0.01"
                  />
                </div>
                <ErrorMessage
                  name="density"
                  component="div"
                  className="text-primary-300 text-center mt-2"
                />
              </div>

              <div className="m-4">
                <div className="flex gap-4">
                  <label htmlFor="model">Select Model:</label>
                  <Field
                    className="rounded border-none text-black px-2"
                    as="select"
                    id="model"
                    name="model"
                  >
                    <option value="" label="Select model" />
                    {models.map((model) => (
                      <option
                        key={`model-${model}`}
                        value={model}
                        label={model}
                      />
                    ))}
                  </Field>
                </div>
                <ErrorMessage
                  name="model"
                  component="div"
                  className="text-primary-300 text-center mt-2"
                />
              </div>

              <div
                className="h-56 bg-[hsl(245,23%,72%,20%)] mt-6 p-8 text-center content-center rounded-lg w-full"
                {...getRootProps()}
              >
                <input {...getInputProps()} />
                {values.file ? (
                  <p>File: {(values.file as File).name}</p>
                ) : (
                  <p>Drag and drop a file here, or click to select one</p>
                )}
              </div>
              <ErrorMessage
                name="file"
                component="div"
                className="text-primary-300 text-center"
              />

              <button
                type="submit"
                disabled={isSubmitting}
                className="bg-accent-300 text-center w-40 p-2 rounded-lg my-6"
              >
                {isSubmitting ? "LOADING..." : "GENERATE"}
              </button>
            </Form>
          );
        }}
      </Formik>
      <ToastContainer />
    </div>
  );
};

export default UploadForm;
