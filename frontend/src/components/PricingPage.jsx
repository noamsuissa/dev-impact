import React from 'react';
import { Link } from 'react-router-dom';
import { Check, ArrowLeft } from 'lucide-react';
import TerminalButton from './common/TerminalButton';

const WAITLIST_URL = 'https://forms.gle/your-waitlist-form-link'; // Replace with actual waitlist form

const PricingPage = () => {
  const plans = [
    {
      name: 'Hobby',
      price: '$0',
      period: 'forever',
      description: 'Perfect for getting started',
      features: [
        'Unlimited impact projects',
        '3 public skillset-specific profiles',
        'Public profiles available at <your-username>.dev-impact.com',
        '50MB total storage',
        'Github integration',
        'Basic metrics tracking',
        'Export to various formats',
        'Includes "Powered by dev-impact" badge'
      ],
      cta: 'Get Started',
      ctaLink: '/signup',
      highlight: false,
      comingSoon: false
    },
    {
      name: 'Pro',
      price: '$7',
      period: 'per month',
      description: 'For serious developers',
      features: [
        'Everything in Free, plus:',
        'Unlimited public profiles',
        'Custom domain for your public profiles',
        '5GB total storage',
        'Advanced analytics and metrics',
        'Priority support',
        'Early access to new features'
      ],
      cta: 'Upgrade to Pro',
      ctaLink: '/signup?plan=pro',
      highlight: true,
      comingSoon: true // signals to use join waitlist, not disable!
    }
  ];

  return (
    <div className="min-h-screen p-5">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-10">
          <Link to="/" className="inline-flex items-center gap-2 text-terminal-text hover:text-terminal-orange transition-colors mb-5">
            <ArrowLeft size={16} />
            <span>Back to home</span>
          </Link>
          <div className="fade-in">
            <div className="text-2xl mb-2">&gt; Pricing</div>
            <div className="text-terminal-gray">
              Choose the plan that fits your needs. Upgrade or downgrade at any time.
            </div>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-10">
          {plans.map((plan, index) => {
            const isComingSoon = plan.comingSoon;

            return (
              <div
                key={plan.name}
                className={`fade-in border p-8 flex flex-col h-full relative transition-opacity ${
                  plan.highlight
                    ? 'border-terminal-orange bg-terminal-bg-lighter'
                    : 'border-terminal-border bg-terminal-bg'
                }`}
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                {isComingSoon && (
                  <div className="absolute inset-0 z-10 bg-terminal-bg-lighter bg-opacity-60 flex items-center justify-center pointer-events-none rounded" />
                )}
                <div className="mb-6">
                  <div className="text-xl mb-2">
                    <span className={`inline-block px-2 py-0.5 rounded ${
                      plan.highlight 
                        ? 'bg-terminal-orange text-terminal-bg' 
                        : 'bg-terminal-orange/20 text-terminal-orange'
                    }`}>
                      {plan.name}
                    </span>
                  </div>
                  <div className="flex items-baseline gap-2 mb-2">
                    <span className="text-3xl text-terminal-orange">{plan.price}</span>
                    {plan.period && (
                      <span className="text-terminal-gray text-sm">/{plan.period}</span>
                    )}
                  </div>
                  <div className="text-terminal-gray text-sm">{plan.description}</div>
                </div>

                <ul className="space-y-3 mb-8 flex-1">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-3">
                      <Check
                        size={18}
                        className={`flex-shrink-0 mt-0.5 ${
                          plan.highlight ? 'text-terminal-green' : 'text-terminal-orange'
                        }`}
                      />
                      <span className="text-terminal-text text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>

                {isComingSoon ? (
                  <a
                    href={WAITLIST_URL}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-auto z-20"
                  >
                    <TerminalButton
                      className={`w-full text-center border-terminal-orange bg-terminal-orange text-terminal-bg hover:bg-terminal-orange-light`}
                    >
                      [Join Waitlist]
                    </TerminalButton>
                  </a>
                ) : (
                  <Link to={plan.ctaLink} className="mt-auto">
                    <TerminalButton
                      className={`w-full text-center ${
                        plan.highlight
                          ? 'bg-terminal-orange border-terminal-orange text-terminal-bg hover:bg-terminal-orange-light'
                          : ''
                      }`}
                    >
                      [{plan.cta}]
                    </TerminalButton>
                  </Link>
                )}
                {isComingSoon && (
                  <div className="absolute top-4 right-4 z-20">
                    <span className="bg-terminal-orange/80 text-terminal-bg px-3 py-1 rounded text-xs shadow">
                      Coming Soon
                    </span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* FAQ Section */}
        <div className="fade-in border border-terminal-border p-8 bg-terminal-bg">
          <div className="text-xl mb-6">
            <span className="inline-block px-2 py-0.5 rounded bg-terminal-orange/20 text-terminal-orange">
              &gt; Frequently Asked Questions
            </span>
          </div>
          <div className="space-y-6">
            <div>
              <div className="text-terminal-orange mb-2">Q: Can I change plans later?</div>
              <div className="text-terminal-gray text-sm">
                A: Yes! You can upgrade or downgrade at any time. Changes take effect immediately.
              </div>
            </div>
            <div>
              <div className="text-terminal-orange mb-2">Q: What payment methods do you accept?</div>
              <div className="text-terminal-gray text-sm">
                A: We accept all major credit cards and PayPal. All payments are processed securely.
              </div>
            </div>
            <div>
              <div className="text-terminal-orange mb-2">Q: Do you offer refunds?</div>
              <div className="text-terminal-gray text-sm">
                A: Yes, we offer a 30-day money-back guarantee. If you're not satisfied, we'll refund your payment.
              </div>
            </div>
            <div>
              <div className="text-terminal-orange mb-2">Q: What happens to my data if I cancel?</div>
              <div className="text-terminal-gray text-sm">
                A: Your data remains accessible. You can export everything before canceling, and we'll keep your account active for 30 days after cancellation.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;

