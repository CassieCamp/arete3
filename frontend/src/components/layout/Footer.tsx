import Link from 'next/link';

const Footer = () => {
  return (
    <footer className="bg-primary text-primary-foreground py-8">
      <div className="container mx-auto px-4 text-center">
        <p className="mb-6 text-sm">
          © 2025 Arete.Coach by Cassie Camp, LLC
        </p>
        <div className="flex justify-center space-x-4 mb-2 text-sm">
          <a href="mailto:arete@cassiecamp.com" className="hover:underline">
            Contact Us
          </a>
          <span aria-hidden="true">•</span>
          <Link href="/security" className="hover:underline">
            Security
          </Link>
          <span aria-hidden="true">•</span>
          <Link href="/about" className="hover:underline">
            About Arete
          </Link>
        </div>
        <div className="flex justify-center space-x-4 text-sm">
          <a href="https://app.termly.io/document/privacy-policy/958d1eac-803f-4251-84ec-730883637074" target="_blank" rel="noopener noreferrer" className="hover:underline">
            Privacy Policy
          </a>
          <span aria-hidden="true">•</span>
          <a href="https://app.termly.io/document/terms-of-use/904f0713-1d63-4984-b03c-7af895d68846" target="_blank" rel="noopener noreferrer" className="hover:underline">
            Terms of Service
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;