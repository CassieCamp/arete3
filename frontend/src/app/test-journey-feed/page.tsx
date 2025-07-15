'use client';

import { useJourneyFeed } from '@/hooks/journey/useJourneyFeed';
import { useEffect } from 'react';

const TestJourneyFeedPage = () => {
  const { data, loading, error, refetch } = useJourneyFeed({
    categories: ['understanding_myself'],
    limit: 5,
  });

  useEffect(() => {
    console.log('--- Journey Feed Hook Test ---');
    console.log('Loading:', loading);
    console.log('Error:', error);
    console.log('Data:', data);
    console.log('--------------------------');
  }, [data, loading, error]);

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>Journey Feed Hook Test Page</h1>
      <button onClick={() => refetch()} disabled={loading}>
        {loading ? 'Reloading...' : 'Refetch Feed'}
      </button>
      
      <h2>Status</h2>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      
      <h2>Data</h2>
      {data ? (
        <pre style={{ background: '#f4f4f4', padding: '1rem', borderRadius: '8px' }}>
          {JSON.stringify(data, null, 2)}
        </pre>
      ) : (
        <p>No data loaded yet.</p>
      )}
    </div>
  );
};

export default TestJourneyFeedPage;