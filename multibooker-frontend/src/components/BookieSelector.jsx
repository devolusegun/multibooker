import React from 'react';

export default function BookieSelector({ selected, onChange }) {
    return (
      <div className="my-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Choose Bookie:</label>
        <select
          value={selected}
          onChange={e => onChange(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded"
        >
          <option value="sportybet">SportyBet</option>
          <option value="bet9ja">Bet9ja</option>
        </select>
      </div>
    );
  }
  