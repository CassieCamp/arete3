import React from 'react';
import { useRouter } from 'next/navigation';

const EmptyState: React.FC = () => {
  const router = useRouter();

  const handleAddReflection = () => {
    router.push('/member/journey/reflection');
  };

  return (
    <>
      <div className="flex items-center justify-center min-h-[400px] h-full p-8">
        <div className="text-center max-w-4xl">
          <div className="bg-slate-900/90 backdrop-blur-sm rounded-2xl p-8 md:p-12 shadow-2xl">
            <p className="text-4xl md:text-5xl font-serif italic text-white leading-relaxed tracking-wide animate-fade-in">
              Your journey begins with reflection.{' '}
              <span className="text-white font-medium glow-text">
                Add your first reflection to get started.
              </span>
            </p>
          </div>
        </div>
      </div>
      
      <button className="cta-button animate-fade-in-delayed" onClick={handleAddReflection}>
        <div className="plus-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
      </button>
      
      <style jsx>{`
        .animate-fade-in {
          animation: fadeIn 1.5s ease-in-out;
        }
        
        .animate-fade-in-delayed {
          animation: fadeIn 1.5s ease-in-out 0.5s both;
        }
        
        .glow-text {
          text-shadow: 0 0 8px rgba(255, 255, 255, 0.4),
                       0 0 16px rgba(255, 255, 255, 0.3),
                       0 0 24px rgba(255, 255, 255, 0.2);
        }
        
        .cta-button {
          position: fixed;
          bottom: 100px;
          right: 24px;
          width: 64px;
          height: 64px;
          border-radius: 50%;
          background: #1a1a2e;
          color: #ffffff;
          border: 2px solid #ffffff;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          animation: breathe 2.5s ease-in-out infinite;
          box-shadow:
            0 0 0 0 rgba(255, 255, 255, 0.6),
            0 0 20px rgba(255, 255, 255, 0.5),
            0 0 40px rgba(255, 255, 255, 0.4),
            0 0 60px rgba(255, 255, 255, 0.3),
            0 4px 12px rgba(0, 0, 0, 0.3);
          z-index: 50;
          font-weight: bold;
        }
        
        .cta-button:hover {
          transform: scale(1.1);
          box-shadow:
            0 0 0 4px rgba(255, 255, 255, 0.8),
            0 0 30px rgba(255, 255, 255, 0.7),
            0 0 60px rgba(255, 255, 255, 0.5),
            0 0 90px rgba(255, 255, 255, 0.3),
            0 8px 24px rgba(0, 0, 0, 0.4);
          animation-play-state: paused;
        }
        
        .cta-button:active {
          transform: scale(1.05);
        }
        
        .plus-icon {
          transition: transform 0.2s ease;
        }
        
        .cta-button:hover .plus-icon {
          transform: rotate(90deg);
        }
        
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes breathe {
          0%, 100% {
            transform: scale(1);
            box-shadow:
              0 0 0 0 rgba(255, 255, 255, 0.6),
              0 0 20px rgba(255, 255, 255, 0.5),
              0 0 40px rgba(255, 255, 255, 0.4),
              0 0 60px rgba(255, 255, 255, 0.3),
              0 4px 12px rgba(0, 0, 0, 0.3);
          }
          50% {
            transform: scale(1.05);
            box-shadow:
              0 0 0 2px rgba(255, 255, 255, 0.7),
              0 0 25px rgba(255, 255, 255, 0.6),
              0 0 50px rgba(255, 255, 255, 0.5),
              0 0 75px rgba(255, 255, 255, 0.4),
              0 6px 16px rgba(0, 0, 0, 0.4);
          }
        }
      `}</style>
    </>
  );
};

export default EmptyState;