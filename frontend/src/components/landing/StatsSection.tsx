import React from 'react';

const StatsSection: React.FC = () => {
  return (
    <section className="bg-background py-16 sm:py-24">
      <div className="container mx-auto px-4">
        <h2 className="font-heading text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground text-center mb-12">
          Coaching By The Numbers
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12">
          
          {/* Card 1 */}
          <div className="bg-card p-8 rounded-lg shadow-md flex flex-col text-center">
            <p className="font-mono text-6xl lg:text-7xl font-bold text-primary mb-4">7x ROI</p>
            <h3 className="font-heading text-2xl font-semibold text-card-foreground mb-3">Proven ROI Impact</h3>
            <p className="text-muted-foreground flex-grow">
              A global study by PricewaterhouseCoopers found the mean ROI for companies investing in coaching was 7 times the initial investment, with over 25% reporting 10-49 times ROI.
            </p>
            <a href="https://coachingfederation.org/resources/research/global-coaching-study/" target="_blank" rel="noopener noreferrer" className="text-sm text-accent-foreground hover:underline mt-4">
              PwC ROI Study
            </a>
          </div>

          {/* Card 2 */}
          <div className="bg-card p-8 rounded-lg shadow-md flex flex-col text-center">
            <p className="font-mono text-6xl lg:text-7xl font-bold text-primary mb-4">80%</p>
            <h3 className="font-heading text-2xl font-semibold text-card-foreground mb-3">Harvard Research Validation</h3>
            <p className="text-muted-foreground flex-grow">
              The Institute of Coaching at Harvard Medical School found that 80% of people who receive coaching report increased self-confidence, and over 70% benefit from improved work performance and relationships.
            </p>
            <a href="https://instituteofcoaching.org/coaching-overview/coaching-benefits" target="_blank" rel="noopener noreferrer" className="text-sm text-accent-foreground hover:underline mt-4">
              Harvard Medical School Research
            </a>
          </div>

          {/* Card 3 */}
          <div className="bg-card p-8 rounded-lg shadow-md flex flex-col text-center">
            <p className="font-mono text-6xl lg:text-7xl font-bold text-primary mb-4">$2T+</p>
            <h3 className="font-heading text-2xl font-semibold text-card-foreground mb-3">Trillion-Dollar Validation</h3>
            <p className="text-muted-foreground flex-grow">
              According to Eric Schmidt, Google and Apple owe much of their trillion-dollar valuations to their business coach, Bill Campbell.*
            </p>
            <a href="https://www.trilliondollarcoach.com/" target="_blank" rel="noopener noreferrer" className="text-sm text-accent-foreground hover:underline mt-4">
              Trillion Dollar Coach
            </a>
            <p className="text-xs text-muted-foreground/70 mt-4">
              *No relation to Bill Campbell (unfortunately!), but maybe great coaching is just in the Campbell DNA.
            </p>
          </div>

        </div>
      </div>
    </section>
  );
};

export default StatsSection;