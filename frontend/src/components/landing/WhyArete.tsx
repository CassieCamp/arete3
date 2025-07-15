import { Check } from 'lucide-react';

const ForLeaders = () => (
  <div>
    <h3 className="text-2xl font-semibold text-foreground mb-6">For Leaders</h3>
    <ul className="space-y-4">
      <li className="flex items-start">
        <Check className="w-5 h-5 text-primary mr-3 mt-1 flex-shrink-0" />
        <div>
          <h4 className="font-semibold">Never lose your growth again</h4>
          <p className="text-muted-foreground">All coaching sessions, insights, and breakthroughs in one continuous journey feed</p>
        </div>
      </li>
      <li className="flex items-start">
        <Check className="w-5 h-5 text-primary mr-3 mt-1 flex-shrink-0" />
        <div>
          <h4 className="font-semibold">Your leadership toolkit in one place</h4>
          <p className="text-muted-foreground">Values, goals, and coaching resources accessible whenever you need them</p>
        </div>
      </li>
      <li className="flex items-start">
        <Check className="w-5 h-5 text-primary mr-3 mt-1 flex-shrink-0" />
        <div>
          <h4 className="font-semibold">See your ROI story unfold</h4>
          <p className="text-muted-foreground">AI generates compelling impact narratives from your coaching documentation to share with stakeholders or for personal reflection</p>
        </div>
      </li>
      <li className="flex items-start">
        <Check className="w-5 h-5 text-primary mr-3 mt-1 flex-shrink-0" />
        <div>
          <h4 className="font-semibold">Seamless coach collaboration</h4>
          <p className="text-muted-foreground">Easy scheduling, billing, and session management so you focus on growth, not admin</p>
        </div>
      </li>
    </ul>
  </div>
);

const ForCoaches = () => (
  <div>
    <h3 className="text-2xl font-semibold text-foreground mb-6">For Coaches</h3>
    <ul className="space-y-4">
      <li className="flex items-start">
        <Check className="w-5 h-5 text-primary mr-3 mt-1 flex-shrink-0" />
        <div>
          <h4 className="font-semibold">See the full client story</h4>
          <p className="text-muted-foreground">Every touchpoint and breakthrough in one dashboard so you start each session informed</p>
        </div>
      </li>
      <li className="flex items-start">
        <Check className="w-5 h-5 text-primary mr-3 mt-1 flex-shrink-0" />
        <div>
          <h4 className="font-semibold">Effortless session prep</h4>
          <p className="text-muted-foreground">AI-generated client summaries and progress insights delivered before you meet</p>
        </div>
      </li>
      <li className="flex items-start">
        <Check className="w-5 h-5 text-primary mr-3 mt-1 flex-shrink-0" />
        <div>
          <h4 className="font-semibold">Demonstrate your impact</h4>
          <p className="text-muted-foreground">AI creates ROI stories from client documentation to showcase coaching effectiveness for renewals and referrals</p>
        </div>
      </li>
      <li className="flex items-start">
        <Check className="w-5 h-5 text-primary mr-3 mt-1 flex-shrink-0" />
        <div>
          <h4 className="font-semibold">Practice management simplified</h4>
          <p className="text-muted-foreground">Scheduling, payments, and client communication in one professional platform</p>
        </div>
      </li>
    </ul>
  </div>
);

const WhyArete = () => {
  return (
    <section className="py-16 px-4 bg-background">
      <div className="container mx-auto max-w-6xl">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold font-serif text-foreground">Why Arete</h2>
        </div>

        <div className="max-w-3xl mx-auto bg-muted/50 p-8 rounded-lg text-center mb-16">
            <h3 className="text-2xl font-semibold text-foreground mb-4">AI amplification, not replacement</h3>
            <p className="text-lg text-muted-foreground">
                Get support between sessions while maintaining the human connection that drives real change
            </p>
        </div>

        <div className="grid md:grid-cols-2 gap-12">
          <ForLeaders />
          <ForCoaches />
        </div>
      </div>
    </section>
  );
};

export default WhyArete;