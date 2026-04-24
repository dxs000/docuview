'use client';

import { useEffect, useState } from 'react';

type Health = { status: string; db?: string; detail?: string };

export default function Home() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const url = process.env.NEXT_PUBLIC_API_URL ?? '';
    fetch(`${url}/health`)
      .then((r) => r.json())
      .then((data) => setHealth(data))
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <main className="min-h-screen p-8 font-mono">
      <h1 className="text-2xl font-bold mb-4">docuview</h1>
      <section>
        <h2 className="text-lg mb-2">API health</h2>
        {error && <pre className="text-red-600">{error}</pre>}
        {health && (
          <pre className="bg-gray-100 dark:bg-gray-900 p-4 rounded">
            {JSON.stringify(health, null, 2)}
          </pre>
        )}
        {!health && !error && <p>loading…</p>}
      </section>
    </main>
  );
}
