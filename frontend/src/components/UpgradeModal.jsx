import React, { useState } from 'react';
import { X, Check, Rocket, Lock } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import WaitlistModal from './WaitlistModal';
import { subscriptions } from '../utils/client';
import { Sparkles } from 'lucide-react';

const enablePayments = import.meta.env.VITE_ENABLE_PAYMENTS === 'true';


const UpgradeModal = ({ isOpen, onClose, title, message, isLimitReached = false, billingPeriod: propBillingPeriod, onBillingPeriodChange }) => {
    const [isWaitlistModalOpen, setIsWaitlistModalOpen] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState(null);
    const [internalBillingPeriod, setInternalBillingPeriod] = useState('monthly');

    // Use prop if provided, otherwise use internal state
    const billingPeriod = propBillingPeriod !== undefined ? propBillingPeriod : internalBillingPeriod;
    const setBillingPeriod = onBillingPeriodChange || setInternalBillingPeriod;

    // Determine content based on context
    const modalTitle = title || (isLimitReached ? "Limit Reached" : "Upgrade to Pro");
    const modalMessage = message || (isLimitReached
        ? "You've reached the limit of the free plan. Upgrade to Pro to continue adding more."
        : "Unlock the full power of Dev Impact with a Pro subscription."
    );

    const proFeatures = [
        'Everything in Free, plus:',
        'Integrated LLM in your public portfolios',
        'Unlimited public portfolios',
        'Custom domain for your public portfolios',
        '5GB total storage',
        'Multi-tier badge awards system',
        'Advanced analytics and metrics tracking',
        'Priority support',
        'Early access to new features'
    ];

    const getPlanPrice = () => {
        if (billingPeriod === 'yearly') {
            return { price: '$8', period: 'per month', billed: '$96 billed yearly' };
        }
        return { price: '$10', period: 'per month', billed: null };
    };

    const planPrice = getPlanPrice();

    const handleUpgrade = async () => {
        if (!enablePayments) {
            setIsWaitlistModalOpen(true);
            return;
        }

        setIsProcessing(true);
        setError(null);

        try {
            // Check if user is already PRO before creating checkout session
            const subInfo = await subscriptions.getSubscriptionInfo();
            if (subInfo?.subscription_type === 'pro') {
                setError('You already have a Pro subscription!');
                setIsProcessing(false);
                return;
            }

            // Get current URL for success/cancel redirects
            const baseUrl = window.location.origin;
            const successUrl = `${baseUrl}/subscription/success`;
            const cancelUrl = `${baseUrl}/subscription/cancel`;

            // Create checkout session with billing period
            const { checkout_url } = await subscriptions.createCheckoutSession(successUrl, cancelUrl, billingPeriod);

            // Redirect to Stripe Checkout
            window.location.href = checkout_url;
        } catch (err) {
            console.error('Failed to create checkout session:', err);
            setError(err.message || 'Failed to start checkout process');
            setIsProcessing(false);
        }
    };


    if (!isOpen) return null;

    return (
        <>
            <div
                className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
                onClick={(e) => {
                    if (e.target === e.currentTarget) {
                        onClose();
                    }
                }}
            >
                <div className="bg-terminal-bg border border-terminal-orange p-8 max-w-lg w-full relative">
                    {/* Coming Soon Badge - only show when payments disabled */}
                    {!enablePayments && (
                        <div className="absolute top-4 right-4">
                            <span className="bg-terminal-orange/80 text-terminal-bg px-3 py-1 rounded text-xs shadow">
                                Coming Soon
                            </span>
                        </div>
                    )}


                    {/* Header */}
                    <div className="flex items-center justify-between mb-6 mt-2">
                        <div className="text-xl text-terminal-orange flex items-center gap-2">
                            <Sparkles size={20} />
                            <span>&gt; {modalTitle}</span>
                        </div>
                        <button
                            onClick={onClose}
                            className="text-terminal-gray hover:text-terminal-orange transition-colors"
                        >
                            <X size={20} />
                        </button>
                    </div>

                    {/* Content */}
                    <div className="space-y-6">
                        {/* Limit Message */}
                        <div className="bg-terminal-orange/10 border border-terminal-orange/30 p-4 rounded">
                            <div className="text-terminal-text text-sm">
                                {modalMessage}
                            </div>
                        </div>

                        {/* Billing Period Toggle - only show when payments enabled */}
                        {enablePayments && (
                            <div className="flex justify-center mb-4">
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

                        {/* Pro Plan Details */}
                        <div>
                            <div className="mb-4">
                                <div className="inline-block px-2 py-0.5 rounded bg-terminal-orange text-terminal-bg text-lg mb-2">
                                    Pro
                                </div>
                                {!enablePayments ? (
                                    <div className="text-xl mb-2">
                                        <span className="inline-block px-2 py-0.5 rounded bg-terminal-orange/20 text-terminal-orange">
                                            Coming Soon
                                        </span>
                                    </div>
                                ) : (
                                    <div className="mb-2">
                                        <div className="flex items-baseline gap-2">
                                            <span className="text-3xl text-terminal-orange">{planPrice.price}</span>
                                            {planPrice.period && (
                                                <span className="text-terminal-gray text-sm">/{planPrice.period}</span>
                                            )}
                                        </div>
                                        {planPrice.billed && (
                                            <div className="text-terminal-gray text-xs mt-1">{planPrice.billed}</div>
                                        )}
                                    </div>
                                )}
                                <div className="text-terminal-gray text-sm">For serious developers</div>
                            </div>

                            {/* Features List */}
                            <ul className="space-y-3">
                                {proFeatures.map((feature, idx) => (
                                    <li key={idx} className="flex items-start gap-3">
                                        <Check
                                            size={18}
                                            className="flex-shrink-0 mt-0.5 text-terminal-green"
                                        />
                                        <span className="text-terminal-text text-sm">{feature}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        {/* CTA */}
                        <div className="pt-4">
                            {/* Error Message */}
                            {error && (
                                <div className="mb-4 bg-red-900/20 border border-red-500/50 p-3 rounded">
                                    <div className="text-red-400 text-sm">{error}</div>
                                </div>
                            )}

                            <TerminalButton
                                onClick={handleUpgrade}
                                disabled={isProcessing}
                                className="w-full text-center border-terminal-orange bg-terminal-orange text-terminal-bg hover:bg-terminal-orange-light"
                            >
                                {isProcessing ? '[Processing...]' : enablePayments ? '[Upgrade to Pro]' : '[Join Waitlist]'}
                            </TerminalButton>
                            <div className="text-terminal-gray text-xs text-center mt-3">
                                {enablePayments
                                    ? 'You will be redirected to Stripe to complete your payment securely.'
                                    : 'Dev Impact Pro is coming soon. Join the waitlist to be notified when it launches.'
                                }
                            </div>
                        </div>

                    </div>
                </div>
            </div>

            {/* Waitlist Modal */}
            <WaitlistModal
                isOpen={isWaitlistModalOpen}
                onClose={() => setIsWaitlistModalOpen(false)}
            />
        </>
    );
};

export default UpgradeModal;
