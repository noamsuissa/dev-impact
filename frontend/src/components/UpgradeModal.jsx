import React, { useState } from 'react';
import { X, Check, Sparkles } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import WaitlistModal from './WaitlistModal';

const UpgradeModal = ({ isOpen, onClose, title = 'Upgrade to Pro', message = "You've reached the limit of 3 profiles on the free plan." }) => {
    const [isWaitlistModalOpen, setIsWaitlistModalOpen] = useState(false);

    const proFeatures = [
        'Everything in Free, plus:',
        'Unlimited public profiles',
        'Custom domain for your public profiles',
        '5GB total storage',
        'Advanced analytics and metrics',
        'Priority support',
        'Early access to new features'
    ];

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
                    {/* Coming Soon Badge */}
                    <div className="absolute top-4 right-4">
                        <span className="bg-terminal-orange/80 text-terminal-bg px-3 py-1 rounded text-xs shadow">
                            Coming Soon
                        </span>
                    </div>

                    {/* Header */}
                    <div className="flex items-center justify-between mb-6 mt-2">
                        <div className="text-xl text-terminal-orange flex items-center gap-2">
                            <Sparkles size={20} />
                            <span>&gt; {title}</span>
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
                                {message}
                            </div>
                        </div>

                        {/* Pro Plan Details */}
                        <div>
                            <div className="mb-4">
                                <div className="inline-block px-2 py-0.5 rounded bg-terminal-orange text-terminal-bg text-lg mb-2">
                                    Pro
                                </div>
                                <div className="flex items-baseline gap-2 mb-2">
                                    <span className="text-3xl text-terminal-orange">$7</span>
                                    <span className="text-terminal-gray text-sm">/per month</span>
                                </div>
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
                            <TerminalButton
                                onClick={() => setIsWaitlistModalOpen(true)}
                                className="w-full text-center border-terminal-orange bg-terminal-orange text-terminal-bg hover:bg-terminal-orange-light"
                            >
                                [Join Waitlist]
                            </TerminalButton>
                            <div className="text-terminal-gray text-xs text-center mt-3">
                                Dev Impact Pro is coming soon. Join the waitlist to be notified when it launches.
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
