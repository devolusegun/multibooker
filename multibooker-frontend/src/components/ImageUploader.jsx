import React, { useState } from 'react';

function ImageUploader({ onSubmit }) {
  const [file, setFile] = useState(null);

  const handleUpload = (e) => {
    e.preventDefault(); // 🔒 Prevent accidental GET request
    if (file) {
      onSubmit(file);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept="image/*"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button
        onClick={(e) => handleUpload(e)}
        className="ml-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Upload
      </button>
    </div>
  );
}

export default ImageUploader;