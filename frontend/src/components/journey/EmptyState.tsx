import React from 'react';

const EmptyState: React.FC = () => {
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
      
      <style jsx>{`
        .animate-fade-in {
          animation: fadeIn 1.5s ease-in-out;
        }
        
        .glow-text {
          text-shadow: 0 0 8px rgba(255, 255, 255, 0.4),
                       0 0 16px rgba(255, 255, 255, 0.3),
                       0 0 24px rgba(255, 255, 255, 0.2);
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
      `}</style>
    </>
  );
};

export default EmptyState;