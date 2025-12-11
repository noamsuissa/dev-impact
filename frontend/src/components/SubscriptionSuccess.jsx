import React from 'react';
import { CheckCircle, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import TerminalButton from './common/TerminalButton';

const SubscriptionSuccess = () => {
    return (
        <div className="min-h-screen bg-terminal-bg flex items-center justify-center p-4">
            <div className="max-w-2xl w-full">
                <div className="bg-terminal-bg-lighter border border-terminal-green p-8 text-center">
                    {/* Success Icon */}
                    <div className="flex justify-center mb-6">
                        <CheckCircle size={64} className="text-terminal-green" />
                    </div>

                    {/* Header */}
                    <h1 className="text-3xl text-terminal-green mb-4">
                        &gt; Payment Successful!
                    </h1>

                    {/* Message */}
                    <div className="space-y-4 mb-8">
                        <p className="text-terminal-text text-lg">
                            Welcome to <span className="text-terminal-orange font-semibold">Dev Impact Pro</span>!
                        </p>
                        <p className="text-terminal-gray">
                            Your subscription is now active. You now have access to:
                        </p>
                        <ul className="text-terminal-text text-left max-w-md mx-auto space-y-2">
                            <li className="flex items-start gap-2">
                                <span className="text-terminal-green">✓</span>
                                <span>Unlimited public profiles</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <span className="text-terminal-green">✓</span>
                                <span>Custom domain for your profiles</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <span className="text-terminal-green">✓</span>
                                <span>5GB total storage</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <span className="text-terminal-green">✓</span>
                                <span>Advanced analytics and metrics</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <span className="text-terminal-green">✓</span>
                                <span>Priority support</span>
                            </li>
                        </ul>
                    </div>

                    {/* CTA */}
                    <Link to="/dashboard">
                        <TerminalButton className="border-terminal-green text-terminal-green hover:bg-terminal-green hover:text-terminal-bg">
                            Go to Dashboard <ArrowRight size={16} className="inline ml-2" />
                        </TerminalButton>
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default SubscriptionSuccess;
