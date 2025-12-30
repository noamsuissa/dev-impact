import React, { useState } from 'react';
import { X, Check, Rocket, Lock } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import WaitlistModal from './WaitlistModal';
import { subscriptions } from '../utils/client';
import { Sparkles } from 'lucide-react';

const enablePayments = import.meta.env.VITE_ENABLE_PAYMENTS === 'true';


const UpgradeModal = ({ isOpen, onClose, title, message, isLimitReached = false }) => {
    const [isWaitlistModalOpen, setIsWaitlistModalOpen] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState(null);

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

    const plan = {
        name: 'Pro',
        price: '$7',
        period: 'per month',
    };

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

            // Create checkout session
            const { checkout_url } = await subscriptions.createCheckoutSession(successUrl, cancelUrl);

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

                        {/* Pro Plan Details */}
                        <div>
                            <div className="mb-4">
                                <div className="inline-block px-2 py-0.5 rounded bg-terminal-orange text-terminal-bg text-lg mb-2">
                                    {plan.name}
                                </div>
                                {!enablePayments ? (
                                    <div className="text-xl mb-2">
                                        <span className="inline-block px-2 py-0.5 rounded bg-terminal-orange/20 text-terminal-orange">
                                            Coming Soon
                                        </span>
                                    </div>
                                ) : (
                                    <div className="flex items-baseline gap-2 mb-2">
                                        <span className="text-3xl text-terminal-orange">{plan.price}</span>
                                        {plan.period && (
                                            <span className="text-terminal-gray text-sm">/{plan.period}</span>
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
