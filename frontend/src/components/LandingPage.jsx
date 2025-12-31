import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import TerminalButton from './common/TerminalButton';
import { useMetaTags } from '../hooks/useMetaTags';

const LandingPage = () => {
  const [lines, setLines] = useState([]);
  const [showButtons, setShowButtons] = useState(false);

  // Set meta tags for landing page
  useMetaTags({
    title: 'dev-impact - Show Your Developer Impact',
    description: 'A new standard in showcasing developer impact. Show real impact, not just bullet points. Create beautiful, shareable developer profiles with quantifiable metrics.',
    image: 'https://www.dev-impact.io/og-image-2.png',
    url: 'https://www.dev-impact.io/',
    type: 'website'
  });

  useEffect(() => {
    const bootSequence = [
      '> dev-impact v1.0.0',
      '> initializing system...',
      '> loading components...',
      '> ready.',
      '',
      'A new standard for developer resumes.',
      'Show real impact, not just bullet points.',
      ''
    ];

    // Check if landing page has been loaded before
    const hasLoadedBefore = localStorage.getItem('dev-impact-landing-loaded');

    if (hasLoadedBefore) {
      // Show all lines immediately (defer to avoid lint warning)
      setTimeout(() => {
        setLines(bootSequence);
        setShowButtons(true);
      }, 0);
    } else {
      // First time - animate the boot sequence
      bootSequence.forEach((line, i) => {
        setTimeout(() => {
          setLines(prev => [...prev, line]);
          if (i === bootSequence.length - 1) {
            setTimeout(() => {
              setShowButtons(true);
              // Mark as loaded after animation completes
              localStorage.setItem('dev-impact-landing-loaded', 'true');
            }, 500);
          }
        }, i * 300);
      });
    }
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center p-5">
      <div className="w-full max-w-[630px]">
        {/* Text and Logo Container */}
        <div className="flex items-start gap-6 mb-10">
          {/* Left column - Text content */}
          <div className="flex-1">
            {lines.map((line, i) => (
              <div key={i} className="fade-in mb-2.5">
                {line}
              </div>
            ))}
          </div>

          {/* Right column - Logo */}
          {showButtons && (
            <div className="fade-in hidden md:block flex-shrink-0">
              <img
                src="/dev-impact-short.svg"
                alt="dev-impact logo"
                width={200}
                className="opacity-90"
              />
            </div>
          )}
        </div>

        {/* Buttons Container - Full Width */}
        {showButtons && (
          <div className="fade-in">
            <div className="flex flex-wrap gap-5 mb-5">
              <Link to="/signin">
                <TerminalButton>
                  [Start Building]
                </TerminalButton>
              </Link>
              <Link to="/about">
                <TerminalButton>
                  [About Us]
                </TerminalButton>
              </Link>
              <Link to="/pricing">
                <TerminalButton>
                  [Pricing]
                </TerminalButton>
              </Link>
              <Link to="/example">
                <TerminalButton>
                  [View Example]
                </TerminalButton>
              </Link>
            </div>
            <div className="text-center space-x-4">
              <Link to="/terms" className="text-xs text-terminal-gray hover:text-terminal-text transition-colors">
                [Terms of Service]
              </Link>
              <Link to="/privacy" className="text-xs text-terminal-gray hover:text-terminal-text transition-colors">
                [Privacy Policy]
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LandingPage;