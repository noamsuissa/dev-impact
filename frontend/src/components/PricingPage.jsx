import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Check, ArrowLeft } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import WaitlistModal from './WaitlistModal';
import UpgradeModal from './UpgradeModal';
import { useMetaTags } from '../hooks/useMetaTags';

import { useAuth } from '../hooks/useAuth';

const PricingPage = () => {
  // Set meta tags for pricing page
  useMetaTags({
    title: 'Pricing - dev-impact',
    description: 'Choose the right plan for your developer portfolio. Free Hobby plan available, or upgrade to Pro for unlimited portfolios, custom domains, and advanced features.',
    image: 'https://www.dev-impact.io/og-image-2.png',
    imageSecureUrl: 'https://www.dev-impact.io/og-image-2.png',
    url: 'https://www.dev-impact.io/pricing',
    type: 'website',
    author: 'dev-impact',
    siteName: 'dev-impact'
  });
  const [isWaitlistModalOpen, setIsWaitlistModalOpen] = useState(false);
  const [isUpgradeModalOpen, setIsUpgradeModalOpen] = useState(false);
  const [billingPeriod, setBillingPeriod] = useState('monthly'); // 'monthly' or 'yearly'
  const { user } = useAuth();
  const navigate = useNavigate();
  const enablePayments = import.meta.env.VITE_ENABLE_PAYMENTS === 'true';

  const getProPlanPrice = () => {
    if (billingPeriod === 'yearly') {
      return { price: '$8', period: 'per month', billed: '$96 billed yearly' };
    }
    return { price: '$10', period: 'per month', billed: null };
  };

  const plans = [
    {
      name: 'Hobby',
      price: '$0',
      period: 'forever',
      description: 'Perfect for getting started',
      features: [
        '10 impact projects',
        '1 public portfolio',
        'Public portfolio available at <your-username>.dev-impact.io',
        '50MB total storage',
        'Bronze-centered badge awards system [coming soon]',
        'Basic Github integration',
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
      getPrice: getProPlanPrice,
      description: 'For serious developers',
      features: [
        'Everything in Free, plus:',
        'Integrated LLM in your public portfolios',
        'Unlimited public portfolios',
        'Custom domain for your public portfolios',
        '5GB total storage',
        'Multi-tier badge awards system',
        'Advanced analytics and metrics tracking',
        'Priority support',
        'Early access to new features'
      ],
      cta: 'Upgrade to Pro',
      ctaLink: '/signup?plan=pro',
      highlight: true,
      comingSoon: !enablePayments
    }
  ];

  const handleProPlanClick = (e) => {
    e.preventDefault();

    if (!enablePayments) {
      setIsWaitlistModalOpen(true);
      return;
    }

    // Check if user is authenticated
    if (user) {
      // User is logged in - show upgrade modal with billing period
      setIsUpgradeModalOpen(true);
    } else {
      // User is not logged in - redirect to signup with plan parameter
      navigate('/signup?plan=pro');
    }
  };

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

        {/* Billing Period Toggle - only show when payments enabled */}
        {enablePayments && (
          <div className="mb-6 flex justify-center">
            <div className="inline-flex items-center gap-3 border border-terminal-border p-1 rounded bg-terminal-bg">
              <button
                onClick={() => setBillingPeriod('monthly')}
                className={`px-4 py-2 rounded text-sm transition-colors ${
                  billingPeriod === 'monthly'
                    ? 'bg-terminal-orange text-terminal-bg'
                    : 'text-terminal-text hover:text-terminal-orange'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingPeriod('yearly')}
                className={`px-4 py-2 rounded text-sm transition-colors ${
                  billingPeriod === 'yearly'
                    ? 'bg-terminal-orange text-terminal-bg'
                    : 'text-terminal-text hover:text-terminal-orange'
                }`}
              >
                Yearly
                <span className="ml-1 text-xs text-terminal-green">Save 20%</span>
              </button>
            </div>
          </div>
        )}

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-10">
          {plans.map((plan, index) => {
            const isComingSoon = plan.comingSoon;
            const priceInfo = plan.getPrice ? plan.getPrice() : { price: plan.price, period: plan.period, billed: null };

            return (
              <div
                key={plan.name}
                className={`fade-in border p-8 flex flex-col h-full relative transition-opacity ${plan.highlight
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
                    <span className={`inline-block px-2 py-0.5 rounded ${plan.highlight
                      ? 'bg-terminal-orange text-terminal-bg'
                      : 'bg-terminal-orange/20 text-terminal-orange'
                      }`}>
                      {plan.name}
                    </span>
                  </div>
                  {isComingSoon ? (
                    <div className="text-xl mb-2">
                      <span className="inline-block px-2 py-0.5 rounded bg-terminal-orange/20 text-terminal-orange">
                        Coming Soon
                      </span>
                    </div>
                  ) : (
                    <div className="mb-2">
                      <div className="flex items-baseline gap-2">
                        <span className="text-3xl text-terminal-orange">{priceInfo.price}</span>
                        {priceInfo.period && (
                          <span className="text-terminal-gray text-sm">/{priceInfo.period}</span>
                        )}
                      </div>
                      {priceInfo.billed && (
                        <div className="text-terminal-gray text-xs mt-1">{priceInfo.billed}</div>
                      )}
                    </div>
                  )}
                  <div className="text-terminal-gray text-sm">{plan.description}</div>
                </div>

                <ul className="space-y-3 mb-8 flex-1">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-3">
                      <Check
                        size={18}
                        className={`flex-shrink-0 mt-0.5 ${plan.highlight ? 'text-terminal-green' : 'text-terminal-orange'
                          }`}
                      />
                      <span className="text-terminal-text text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>

                {isComingSoon ? (
                  <div className="mt-auto z-20">
                    <TerminalButton
                      onClick={() => setIsWaitlistModalOpen(true)}
                      className={`w-full text-center border-terminal-orange bg-terminal-orange text-terminal-bg hover:bg-terminal-orange-light`}
                    >
                      [Join Waitlist]
                    </TerminalButton>
                  </div>
                ) : plan.highlight ? (
                  <div className="mt-auto">
                    <TerminalButton
                      onClick={handleProPlanClick}
                      className="w-full text-center bg-terminal-orange border-terminal-orange text-terminal-bg hover:bg-terminal-orange-light"
                    >
                      [{plan.cta}]
                    </TerminalButton>
                  </div>
                ) : (
                  <Link to={plan.ctaLink} className="mt-auto">
                    <TerminalButton
                      className="w-full text-center"
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
            {enablePayments ? (
              // FAQ when payments are enabled
              <>
                <div>
                  <div className="text-terminal-orange mb-2">Q: Can I change plans later?</div>
                  <div className="text-terminal-gray text-sm">
                    A: Yes! You can upgrade or downgrade at any time. Changes take effect immediately.
                  </div>
                </div>
                <div>
                  <div className="text-terminal-orange mb-2">Q: What payment methods do you accept?</div>
                  <div className="text-terminal-gray text-sm">
                    A: All payments are processed securely through Stripe. We do not store your full credit card information.
                  </div>
                </div>
                <div>
                  <div className="text-terminal-orange mb-2">Q: Do you offer refunds?</div>
                  <div className="text-terminal-gray text-sm">
                    A: Yes, we offer a 30-day money-back guarantee. If you're not satisfied, we'll refund your payment.
                  </div>
                </div>
                <div>
                  <div className="text-terminal-orange mb-2">Q: What happens to my data if I cancel my subscription?</div>
                  <div className="text-terminal-gray text-sm">
                    A: Your data remains accessible and you get downgraded to the Hobby plan.
                  </div>
                </div>
                <div>
                  <div className="text-terminal-orange mb-2">Q: What happens to my data if I delete my account?</div>
                  <div className="text-terminal-gray text-sm">
                    A: Your data is permanently deleted and you cannot access it again.
                  </div>
                </div>
                <div>
                  <div className="text-terminal-orange mb-2">Q: Can I export my data?</div>
                  <div className="text-terminal-gray text-sm">
                    A: Yes, you can export your data at any time.
                  </div>
                </div>
                <div>
                  <div className="text-terminal-orange mb-2">Q: How can I contribute to the project?</div>
                  <div className="text-terminal-gray text-sm">
                    A: You can contribute to the project <a href="https://github.com/noamsuissa/dev-impact" className="text-terminal-orange hover:underline">here</a>.
                  </div>
                </div>
                <div>
                  <div className="text-terminal-orange mb-2">Q: How do I contact you?</div>
                  <div className="text-terminal-gray text-sm">
                    A: You can contact us at <a href="mailto:support@dev-impact.io" className="text-terminal-orange hover:underline">support@dev-impact.io</a>.
                  </div>
                </div>
              </>
            ) : (
              // FAQ when waitlist is enabled (payments disabled)
              <>
                <div>
                  <div className="text-terminal-orange mb-2">Q: What is the waitlist?</div>
                  <div className="text-terminal-gray text-sm">
                    A: The waitlist is for developers who want early access to the Pro plan. Join to be notified when Pro features become available.
                  </div>
                </div>
                <div>
                  <div className="text-terminal-orange mb-2">Q: When will Pro be available?</div>
                  <div className="text-terminal-gray text-sm">
                    A: We're working hard to launch Pro soon. Join the waitlist to be among the first to know when it's ready.
                  </div>
                </div>
                <div>
                  <div className="text-terminal-orange mb-2">Q: What happens when I join the waitlist?</div>
                  <div className="text-terminal-gray text-sm">
                    A: You'll receive an email notification when Pro is available, and you'll have priority access to upgrade.
                  </div>
                </div>
                <div>
                  <div className="text-terminal-orange mb-2">Q: Will I get early access or special pricing?</div>
                  <div className="text-terminal-gray text-sm">
                    A: Waitlist members will be notified first and may receive special launch offers. Stay tuned!
                  </div>
                </div>
                <div>
                  <div className="text-terminal-orange mb-2">Q: Can I still use the free plan?</div>
                  <div className="text-terminal-gray text-sm">
                    A: Absolutely! The Hobby plan is free forever and available to everyone right now.
                  </div>
                </div>
                <div>
                  <div className="text-terminal-orange mb-2">Q: What happens to my data if I delete my account?</div>
                  <div className="text-terminal-gray text-sm">
                    A: Your data is permanently deleted and you cannot access it again.
                  </div>
                </div>
                <div>
                  <div className="text-terminal-orange mb-2">Q: Can I export my data?</div>
                  <div className="text-terminal-gray text-sm">
                    A: Yes, you can export your data at any time.
                  </div>
                </div>
                <div>
                  <div className="text-terminal-orange mb-2">Q: How can I contribute to the project?</div>
                  <div className="text-terminal-gray text-sm">
                    A: You can contribute to the project <a href="https://github.com/noamsuissa/dev-impact" className="text-terminal-orange hover:underline">here</a>.
                  </div>
                </div>
                <div>
                  <div className="text-terminal-orange mb-2">Q: How do I contact you?</div>
                  <div className="text-terminal-gray text-sm">
                    A: You can contact us at <a href="mailto:support@dev-impact.io" className="text-terminal-orange hover:underline">support@dev-impact.io</a>.
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Waitlist Modal */}
      <WaitlistModal
        isOpen={isWaitlistModalOpen}
        onClose={() => setIsWaitlistModalOpen(false)}
      />

      {/* Upgrade Modal */}
      <UpgradeModal
        isOpen={isUpgradeModalOpen}
        onClose={() => setIsUpgradeModalOpen(false)}
        title={enablePayments ? "Upgrade to Pro" : "Join the Waitlist"}
        message={enablePayments
          ? "Unlock the full power of Dev Impact with a Pro subscription."
          : "Get unlimited profiles, 5GB storage, and more with Dev Impact Pro."}
        billingPeriod={billingPeriod}
        onBillingPeriodChange={setBillingPeriod}
      />
    </div>
  );
};

export default PricingPage;
