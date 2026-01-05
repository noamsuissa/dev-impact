import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import TerminalButton from './common/TerminalButton';
import { useMetaTags } from '../hooks/useMetaTags';

const PrivacyPolicy = () => {
    // Set meta tags for privacy policy page
    useMetaTags({
        title: 'Privacy Policy - dev-impact',
        description: 'Read dev-impact\'s Privacy Policy. Learn how we collect, use, and protect your personal information in compliance with Quebec Law 25.',
        image: 'https://www.dev-impact.io/og-image-2.png',
        imageSecureUrl: 'https://www.dev-impact.io/og-image-2.png',
        url: 'https://www.dev-impact.io/privacy',
        type: 'website',
        author: 'dev-impact',
        siteName: 'dev-impact'
    });

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
                    <h1 className="text-3xl font-bold mb-2">&gt; Privacy Policy</h1>
                    <div className="text-terminal-gray">Last Updated: {new Date().toLocaleDateString()}</div>
                </div>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 1. Introduction</h2>
                    <p className="mb-4">
                        dev-impact ("we," "our," or "us") respects your privacy. This Privacy Policy describes how we collect, use, and share your personal information when you use our website and services.
                    </p>
                    <p>
                        We represent that the processing of your personal data complies with the requirements of the
                        <strong> Act Respecting the Protection of Personal Information in the Private Sector </strong> (Quebec Law 25).
                    </p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 2. Information We Collect</h2>
                    <ul className="list-disc pl-5 space-y-2 text-terminal-gray">
                        <li>
                            <strong className="text-terminal-text">Account Information:</strong> When you sign up, we collect your email address and password (encrypted).
                        </li>
                        <li>
                            <strong className="text-terminal-text">Profile Information:</strong> Any information you voluntarily add to your developer profile, such as your bio, skills, and project details.
                        </li>
                        <li>
                            <strong className="text-terminal-text">GitHub Data:</strong> If you connect your GitHub account, we access your public repositories and profile data to generate your portfolio. We do not write to your repositories.
                        </li>
                        <li>
                            <strong className="text-terminal-text">Usage Data:</strong> We collect anonymous metrics about how you interact with our service to improve performance.
                        </li>
                    </ul>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 3. How We Use Your Information</h2>
                    <p className="mb-2">We use your information to:</p>
                    <ul className="list-disc pl-5 space-y-2 text-terminal-gray">
                        <li>Provide, maintain, and improve our services.</li>
                        <li>Generate your public developer profile and resume.</li>
                        <li>Process payments (handled securely by Stripe).</li>
                        <li>Communicate with you about updates or security issues.</li>
                    </ul>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 4. Third-Party Services</h2>
                    <p className="mb-2">We share data with trusted third-party providers only as necessary to operate our service:</p>
                    <ul className="list-disc pl-5 space-y-2 text-terminal-gray">
                        <li>
                            <a href="https://stripe.com/privacy" className="underline hover:text-terminal-text" target="_blank" rel="noopener noreferrer">
                                <strong className="text-terminal-text">Stripe</strong>
                            </a>: Payment processing.
                        </li>
                        <li>
                            <a href="https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement" className="underline hover:text-terminal-text" target="_blank" rel="noopener noreferrer">
                                <strong className="text-terminal-text">GitHub</strong>
                            </a>: Data synchronization for your profile.
                        </li>
                        <li>
                            <a href="https://supabase.com/privacy" className="underline hover:text-terminal-text" target="_blank" rel="noopener noreferrer">
                                <strong className="text-terminal-text">Supabase</strong>
                            </a>: Database and authentication services.
                        </li>
                        <li>
                            <a href="https://vercel.com/legal/privacy-policy" className="underline hover:text-terminal-text" target="_blank" rel="noopener noreferrer">
                                <strong className="text-terminal-text">Vercel</strong>
                            </a>: Hosting and analytics.
                        </li>
                    </ul>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 5. Your Rights (Law 25)</h2>
                    <p className="mb-2">Under Quebec Law 25, you have the right to:</p>
                    <ul className="list-disc pl-5 space-y-2 text-terminal-gray">
                        <li>Access the personal information we hold about you.</li>
                        <li>Request correction of inaccurate information.</li>
                        <li>Request deletion of your data ("Right to be Forgotten").</li>
                        <li>Withdraw consent for data processing at any time.</li>
                    </ul>
                    <p className="mt-4">
                        To exercise these rights, please contact our Privacy Officer (details below).
                    </p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 6. Data Retention</h2>
                    <p>
                        We retain your personal information only for as long as necessary to provide our services and fulfill the purposes described in this policy.
                        We may also retain and use your information to comply with our legal obligations, resolve disputes, and enforce our agreements.
                    </p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 7. International Data Transfers</h2>
                    <p className="mb-2">
                        Your personal information may be transferred to, stored, and processed in countries other than the one in which you reside, including the United States.
                        Our third-party service providers (Vercel, Supabase, Stripe) operate globally.
                    </p>
                    <p>
                        By using our service, you consent to the transfer of your information to countries outside your country of residence,
                        which may have different data protection rules than those of your country. We take appropriate measures to ensure that your personal information remains protected in accordance with this Privacy Policy.
                    </p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 8. Security Measures</h2>
                    <p>
                        We implement appropriate technical and organizational measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.
                        Data is encrypted in transit (SSL/TLS) and at rest where applicable. However, no method of transmission over the Internet or electronic storage is 100% secure.
                    </p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 9. Tracking Technologies & Cookies</h2>
                    <p className="mb-2">
                        We use cookies and similar tracking technologies to track activity on our service and hold certain information.
                    </p>
                    <ul className="list-disc pl-5 space-y-2 text-terminal-gray">
                        {/* <li>
                            <strong className="text-terminal-text">Essential Cookies:</strong> Required for authentication and core functionality.
                        </li> */}
                        <li>
                            <strong className="text-terminal-text">Analytics:</strong> We use Vercel Analytics and Speed Insights to understand how our website is used and to improve performance.
                            These tools collect anonymous usage data.
                        </li>
                    </ul>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 10. Children's Privacy</h2>
                    <p>
                        Our service does not address anyone under the age of 13. We do not knowingly collect personally identifiable information from anyone under the age of 13.
                        If you are a parent or guardian and you are aware that your child has provided us with Personal Data, please contact us.
                    </p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 11. Changes to This Privacy Policy</h2>
                    <p>
                        We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the "Last Updated" date.
                    </p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 border-b border-terminal-border pb-2">&gt; 12. Contact Us</h2>
                    <p className="mb-2">
                        If you have questions about this Privacy Policy or wish to exercise your rights, please contact our Privacy Officer:
                    </p>
                    <div className="bg-terminal-bg-lighter p-4 rounded border border-terminal-border/50">
                        <p className="text-terminal-text">Privacy Officer</p>
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

export default PrivacyPolicy;
