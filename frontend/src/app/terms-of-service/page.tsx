"use client";

import { useEffect } from 'react';

const TermsOfServicePage = () => {
  const termsUrl = "https://app.termly.io/document/terms-of-use/904f0713-1d63-4984-b03c-7af895d68846";

  useEffect(() => {
    window.location.href = termsUrl;
  }, []);

  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold mb-4">Redirecting to Terms of Service...</h1>
      <p>
        If you are not automatically redirected, please{' '}
        <a href={termsUrl} className="text-blue-500 underline">
          click here
        </a>
        .
      </p>
    </main>
  );
};

export default TermsOfServicePage;