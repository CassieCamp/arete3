import LandingHeader from '@/components/layout/LandingHeader';

const SecurityPage = () => {
  return (
    <div>
      <LandingHeader />
      <main className="p-8 flex justify-center">
        <div className="prose prose-invert max-w-4xl">
          <h1>Security & Data Protection</h1>

          <h2>Data Encryption</h2>
          <p>All data is encrypted in transit and at rest using industry-standard protocols. Session transcripts and personal information are protected with enterprise-grade security.</p>

          <h2>Infrastructure Partners</h2>
          <ul>
            <li><strong>Authentication:</strong> Clerk (SOC 2 Type II certified)</li>
            <li><strong>Database:</strong> MongoDB Atlas (ISO 27001 certified)</li>
            <li><strong>Backend:</strong> Render (SOC 2 compliant hosting)</li>
            <li><strong>Frontend:</strong> Vercel (enterprise security standards)</li>
            <li><strong>Domain:</strong> GoDaddy with SSL certification</li>
          </ul>

          <h2>AI Data Processing</h2>
          <ul>
            <li>Session transcripts and other documents uploaded by users are processed securely by certified AI providers</li>
            <li>All AI processing follows strict data protection protocols</li>
            <li>No training data is retained by AI services</li>
          </ul>

          <h2>Compliance</h2>
          <ul>
            <li>GDPR compliant for EU users</li>
            <li>CCPA compliant for California residents</li>
            <li>Regular security assessments and monitoring</li>
          </ul>

          <h2>Data Access</h2>
          <ul>
            <li>Only you and your coach have access to your session data</li>
            <li>Multi-factor authentication required for all accounts</li>
            <li>Granular access controls and audit logging</li>
          </ul>

          <h2>Questions?</h2>
          <p>Contact us at <a href="mailto:arete@cassiecamp.com">arete@cassiecamp.com</a> for security inquiries.</p>
        </div>
      </main>
    </div>
  );
};

export default SecurityPage;