import React from 'react';
import { useState } from 'react';
import UploadZone from '../components/UploadZone';
import BookieSelector from '../components/BookieSelector';
import Spinner from '../components/Spinner';
import ResultDisplay from '../components/ResultDisplay';
import AdBanner from '../components/AdBanner';
import axios from 'axios';

export default function Home() {
  const [screenshot, setScreenshot] = useState(null);
  const [bookie, setBookie] = useState('sportybet');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleConvert = async () => {
    if (!screenshot) return;

    const formData = new FormData();
    formData.append('screenshot', screenshot);
    formData.append('betUrl', ''); // Placeholder for optional URL
    formData.append('bookie', bookie);

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await axios.post('https://multibooker.onrender.com/upload-bet', formData);
      setResult(res.data);
    } catch (err) {
      setError('Something went wrong. Try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-10 px-4">
      <h1 className="text-2xl font-bold text-center mb-6">🎯 Multibooker – Convert Stake Tickets</h1>

      <UploadZone onFileAccepted={setScreenshot} />

      <div className="mt-4">
        <BookieSelector selected={bookie} onChange={setBookie} />
      </div>

      <button
        onClick={handleConvert}
        className="mt-4 w-full bg-blue-600 text-white font-semibold py-2 px-4 rounded hover:bg-blue-700"
        disabled={loading}
      >
        {loading ? 'Processing...' : 'Convert Bet Slip'}
      </button>

      {loading && <Spinner />}

      {error && <div className="mt-4 text-red-500">{error}</div>}

      {result && (
        <>
          <AdBanner />
          <ResultDisplay bets={result.parsed_bets || []} mapped={result.mapped_bets || []} />
        </>
      )}
    </div>
  );
}