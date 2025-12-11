import React from 'react';
import { XCircle, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import TerminalButton from './common/TerminalButton';

const SubscriptionCancel = () => {
    return (
        <div className="min-h-screen bg-terminal-bg flex items-center justify-center p-4">
            <div className="max-w-2xl w-full">
                <div className="bg-terminal-bg-lighter border border-terminal-orange p-8 text-center">
                    {/* Cancel Icon */}
                    <div className="flex justify-center mb-6">
                        <XCircle size={64} className="text-terminal-orange" />
                    </div>

                    {/* Header */}
                    <h1 className="text-3xl text-terminal-orange mb-4">
                        &gt; Checkout Cancelled
                    </h1>

                    {/* Message */}
                    <div className="space-y-4 mb-8">
                        <p className="text-terminal-text text-lg">
                            No worries! Your subscription was not activated.
                        </p>
                        <p className="text-terminal-gray">
                            You can upgrade to Pro anytime from your dashboard. If you have any questions or concerns, feel free to reach out to our support team.
                        </p>
                    </div>

                    {/* CTAs */}
                    <div className="flex gap-4 justify-center">
                        <Link to="/dashboard">
                            <TerminalButton className="border-terminal-border text-terminal-text hover:border-terminal-orange">
                                <ArrowLeft size={16} className="inline mr-2" /> Back to Dashboard
                            </TerminalButton>
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SubscriptionCancel;
