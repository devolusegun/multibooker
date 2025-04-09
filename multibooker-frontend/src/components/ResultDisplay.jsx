import React from 'react';

export default function ResultDisplay({ bets, mapped }) {
    return (
      <div className="mt-6 space-y-6">
        <div>
          <h2 className="text-lg font-bold mb-2">Parsed Bets</h2>
          {bets.map((bet, idx) => (
            <div key={idx} className="p-3 border rounded mb-2">
              <pre className="text-sm">{JSON.stringify(bet, null, 2)}</pre>
            </div>
          ))}
        </div>
        <div>
          <h2 className="text-lg font-bold mb-2">Mapped Bets</h2>
          {mapped.map((bet, idx) => (
            <div key={idx} className="p-3 border rounded mb-2">
              <pre className="text-sm">{JSON.stringify(bet, null, 2)}</pre>
            </div>
          ))}
        </div>
      </div>
    );
  }  