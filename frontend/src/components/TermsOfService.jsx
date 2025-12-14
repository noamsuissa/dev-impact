import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import TerminalButton from './common/TerminalButton';

const TermsOfService = () => {
    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);

    return (
        <div className="min-h-screen p-5 md:p-10 max-w-4xl mx-auto">
            <div className="fade-in mb-8">
                <Link to="/">
                    <TerminalButton>&lt; Back to Home</TerminalButton>
                </Link>
            </div>

            <div className="fade-in space-y-8 text-terminal-text">
                <div>
                    <h1 className="text-3xl font-bold mb-2">&gt; Terms of Service</h1>
                    <div className="text-terminal-gray">Last Updated: {new Date().toLocaleDateString()}</div>
                </div>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 1. Acceptance of Terms</h2>
                    <p>
                        By accessing or using dev-impact ("we," "our," or "us"), you agree to be bound by these Terms of Service.
                        If you do not agree to these terms, please do not use our service.
                    </p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 2. Description of Service</h2>
                    <p>
                        dev-impact provides a platform for developers to generate professional portfolios and resumes based on their GitHub data and manual inputs.
                        We reserve the right to modify, suspend, or discontinue the service at any time.
                    </p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 3. User Accounts</h2>
                    <p className="mb-2">
                        You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account.
                        You agree to notify us immediately of any unauthorized use of your account.
                    </p>
                    <p>
                        We reserve the right to terminate or suspend access to our service immediately, without prior notice or liability, for any reason whatsoever, including without limitation if you breach the Terms.
                    </p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 4. User Content</h2>
                    <p className="mb-2">
                        You retain ownership of all content you submit to the service (e.g., project descriptions, profile data).
                        By submitting content, you grant us a worldwide, non-exclusive, royalty-free license to use, reproduce, modify, and display your content for the purpose of operating and improving the service.
                    </p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 5. Prohibited Conduct</h2>
                    <p className="mb-2">You agree not to use the service to:</p>
                    <ul className="list-disc pl-5 space-y-2 text-terminal-gray">
                        <li>Violate any applicable laws or regulations.</li>
                        <li>Infringe upon the rights of others.</li>
                        <li>Distribute malware or malicious code.</li>
                        <li>Interfere with or disrupt the integrity or performance of the service.</li>
                    </ul>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 6. Subscriptions and Payments</h2>
                    <p>
                        Some features of the service may require payment of fees. All fees are non-refundable unless otherwise required by law.
                        We use Stripe for secure payment processing and do not store your full credit card information.
                    </p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 7. Limitation of Liability</h2>
                    <p>
                        In no event shall dev-impact, nor its directors, employees, partners, agents, suppliers, or affiliates, be liable for any indirect, incidental, special, consequential or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses, resulting from your access to or use of or inability to access or use the service.
                    </p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 8. Governing Law</h2>
                    <p>
                        These Terms shall be governed and construed in accordance with the laws of Quebec, Canada, without regard to its conflict of law provisions.
                    </p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 9. Contact Us</h2>
                    <p className="mb-2">
                        If you have any questions about these Terms, please contact us at:
                    </p>
                    <div className="bg-terminal-bg-lighter p-4 rounded border border-terminal-border/50">
                        <p className="text-terminal-gray">Email: privacy@dev-impact.io</p>
                    </div>
                </section>

                <div className="pt-8 border-t border-terminal-border mt-8 text-center text-terminal-gray text-sm">
                    &copy; {new Date().getFullYear()} dev-impact. All rights reserved.
                </div>
            </div>
        </div>
    );
};

export default TermsOfService;
