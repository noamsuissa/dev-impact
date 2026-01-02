import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import TerminalButton from './common/TerminalButton';
import { useMetaTags } from '../hooks/useMetaTags';
import { useStructuredData } from '../hooks/useStructuredData';

const LandingPage = () => {
  const [lines, setLines] = useState([]);
  const [showButtons, setShowButtons] = useState(false);
  const [starCount, setStarCount] = useState(null);

  // Set meta tags for landing page
  useMetaTags({
    title: 'dev-impact - Show Your Developer Impact',
    description: 'A new standard in showcasing developer impact. Show real impact, not just bullet points. Create beautiful, shareable developer profiles with quantifiable metrics.',
    image: 'https://www.dev-impact.io/og-image-2.png',
    imageSecureUrl: 'https://www.dev-impact.io/og-image-2.png',
    url: 'https://www.dev-impact.io/',
    type: 'website',
    author: 'dev-impact',
    siteName: 'dev-impact'
  });

  // Add structured data (JSON-LD) for SEO
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "dev-impact",
    "logo": {
      "@type": "ImageObject",
      "url": "https://www.dev-impact.io/dev-impact-short.png",
      "width": 200,
      "height": 200
    },
    "image": "https://www.dev-impact.io/dev-impact-short.png",
    "description": "A new standard in showcasing developer impact. Show real impact, not just bullet points. Create beautiful, shareable developer profiles with quantifiable metrics.",
    "url": "https://www.dev-impact.io/",
    "applicationCategory": "DeveloperApplication",
    "operatingSystem": "Web",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    },
    "publisher": {
      "@type": "Organization",
      "name": "dev-impact",
      "logo": {
        "@type": "ImageObject",
        "url": "https://www.dev-impact.io/dev-impact-short.png",
        "width": 200,
        "height": 200
      },
      "url": "https://www.dev-impact.io/",
      "sameAs": [
        "https://github.com/noamsuissa/dev-impact"
      ]
    },
    "creator": {
      "@type": "Organization",
      "name": "dev-impact",
      "logo": {
        "@type": "ImageObject",
        "url": "https://www.dev-impact.io/dev-impact-short.png",
        "width": 200,
        "height": 200
      },
      "url": "https://www.dev-impact.io/",
      "sameAs": [
        "https://github.com/noamsuissa/dev-impact"
      ]
    },
    ...(starCount && {
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "5",
        "ratingCount": starCount.toString()
      }
    })
  };

  useStructuredData(structuredData, 'landing-page-structured-data');

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

  // Fetch GitHub star count - Deferred to avoid blocking critical rendering
  useEffect(() => {
    const fetchStarCount = async () => {
      try {
        const response = await fetch('https://api.github.com/repos/noamsuissa/dev-impact');
        if (response.ok) {
          const data = await response.json();
          setStarCount(data.stargazers_count);
        }
      } catch (error) {
        // Silently fail if API call fails
        console.error('Failed to fetch star count:', error);
      }
    };

    // Defer GitHub API call until after initial render using requestIdleCallback
    // Falls back to setTimeout if requestIdleCallback is not available
    if ('requestIdleCallback' in window) {
      requestIdleCallback(fetchStarCount, { timeout: 2000 });
    } else {
      // Fallback: wait for page to be interactive
      setTimeout(fetchStarCount, 1000);
    }
  }, []);

  return (
    <main className="min-h-screen flex items-center justify-center p-5 relative">
      {/* GitHub Button - Top Right */}
      {showButtons && (
        <div className="absolute top-6 right-6 fade-in">
          <a 
            href="https://github.com/noamsuissa/dev-impact" 
            target="_blank" 
            rel="noopener noreferrer"
            className="group"
          >
            <TerminalButton className="flex items-center gap-2">
              <div className="relative w-6 h-6">
                <img 
                  src="/github-mark-white.svg" 
                  alt="GitHub" 
                  className="w-6 h-6 group-hover:opacity-0 transition-opacity"
                />
                <img 
                  src="/github-mark.svg" 
                  alt="GitHub" 
                  className="w-6 h-6 absolute top-0 left-0 opacity-0 group-hover:opacity-100 transition-opacity"
                />
              </div>
              {starCount !== null && (
                <span className="text-sm">
                  ⭐ {starCount}
                </span>
              )}
            </TerminalButton>
          </a>
        </div>
      )}
      <article className="w-full max-w-[630px]">
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
                loading="lazy"
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
      </article>
    </main>
  );
};

export default LandingPage;