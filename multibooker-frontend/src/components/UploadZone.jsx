import React from 'react';

import { useDropzone } from 'react-dropzone';

export default function UploadZone({ onFileAccepted }) {
  const { getRootProps, getInputProps } = useDropzone({
    accept: { 'image/*': [] },
    maxFiles: 1,
    onDrop: acceptedFiles => onFileAccepted(acceptedFiles[0])
  });

  return (
    <div {...getRootProps()} className="border-2 border-dashed border-gray-400 rounded-lg p-6 text-center cursor-pointer hover:border-blue-500">
      <input {...getInputProps()} />
      <p className="text-gray-600">Drag & drop or click to upload a screenshot</p>
    </div>
  );
}
