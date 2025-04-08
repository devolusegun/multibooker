import React, { useState } from 'react';
import ImageUploader from '../components/ImageUploader';
import axios from 'axios';

const API_URL = "https://multibooker.onrender.com/upload-bet";

function Home() {
  const [bookie, setBookie] = useState("bet9ja");
  const [response, setResponse] = useState(null);

  const handleSubmit = async (file) => {
    const formData = new FormData();
    formData.append("screenshot", file);
    formData.append("bookie", bookie);
    formData.append("betUrl", "");

    try {
      const res = await axios.post(API_URL, formData);
      setResponse(res.data);
    } catch (err) {
      console.error(err);
      alert("Error uploading or processing slip.");
    }
  };

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">🎯 Multibooker MVP</h1>
      <div>
        <label className="block mb-2 font-medium">Choose Bookie:</label>
        <select
          className="border rounded p-2"
          value={bookie}
          onChange={(e) => setBookie(e.target.value)}
        >
          <option value="bet9ja">Bet9ja</option>
          <option value="sportybet">SportyBet</option>
        </select>
      </div>
      <ImageUploader onSubmit={handleSubmit} />
      {response && (
        <pre className="bg-white p-4 rounded shadow overflow-x-auto text-sm">
          {JSON.stringify(response, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default Home;