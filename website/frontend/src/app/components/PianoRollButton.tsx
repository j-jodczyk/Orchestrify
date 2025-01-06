"use clinet";

import React, { useState } from "react";
import { toast, ToastContainer, ToastOptions } from "react-toastify";

interface PianoRollButtonProps {
  midiBlob: Blob | null;
  handleFetchPianoRoll: (iframeUrl: string) => void;
}

const toastErrorParams: ToastOptions = {
  position: "top-center",
  autoClose: 5000,
  closeOnClick: true,
  pauseOnHover: true,
  hideProgressBar: true,
};

const PianoRollButton: React.FC<PianoRollButtonProps> = ({
  midiBlob,
  handleFetchPianoRoll,
}) => {
  const fetchPianoRoll = async () => {
    if (!midiBlob) {
      return;
    }
    const formData = new FormData();
    formData.append("file", midiBlob, "generated.mid");
    try {
      const pianorollResponse = await fetch("http://localhost:8000/pianoroll", {
        method: "POST",
        body: formData,
      });

      if (!pianorollResponse.ok) {
        const responseJson = await pianorollResponse.json();
        toast.error(
          `Error fetching pianoroll: ${responseJson.detail}`,
          toastErrorParams,
        );
        return;
      }

      const pianoRollHTMLContent = await pianorollResponse.text();
      const blob = new Blob([pianoRollHTMLContent], { type: "text/html" });
      const blobUrl = URL.createObjectURL(blob);
      handleFetchPianoRoll(blobUrl);
    } catch (err: any) {
      console.log(err);
      toast.error("Failed to fetch pianoroll", toastErrorParams);
    }
  };

  return (
    <div>
      <button
        className={`text-center w-40 p-2 rounded-lg my-10 ${midiBlob ? "bg-secondary-300" : "bg-secondary-700"} `}
        onClick={fetchPianoRoll}
        disabled={!midiBlob}
      >
        PIANOROLL
      </button>
      <ToastContainer />
    </div>
  );
};

export default PianoRollButton;
