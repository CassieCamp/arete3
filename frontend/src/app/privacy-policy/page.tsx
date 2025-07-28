"use client";

import { useEffect } from 'react';

const PrivacyPolicyPage = () => {
  const policyUrl = "https://app.termly.io/document/privacy-policy/958d1eac-803f-4251-84ec-730883637074";

  useEffect(() => {
    window.location.href = policyUrl;
  }, []);

  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold mb-4">Redirecting to Privacy Policy...</h1>
      <p>
        If you are not automatically redirected, please{' '}
        <a href={policyUrl} className="text-blue-500 underline">
          click here
        </a>
        .
      </p>
    </main>
  );
};

export default PrivacyPolicyPage;