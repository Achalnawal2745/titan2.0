// Search Component
'use client';
import { useState } from 'react';

export function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    const res = await fetch(`/api/search?q=${query}`);
    setResults(await res.json());
  };

  return (
    <div>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <button onClick={handleSearch}>Search</button>
      {results.map((r: any) => <div key={r.id}>{r.title}</div>)}
    </div>
  );
}
