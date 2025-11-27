import React, { useState, useEffect } from 'react';
import TerminalButton from './common/TerminalButton';

const LandingPage = ({ onStart }) => {
  const [lines, setLines] = useState([]);
  const [showButtons, setShowButtons] = useState(false);

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

    bootSequence.forEach((line, i) => {
      setTimeout(() => {
        setLines(prev => [...prev, line]);
        if (i === bootSequence.length - 1) {
          setTimeout(() => setShowButtons(true), 500);
        }
      }, i * 300);
    });
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center p-5">
      <div className="max-w-[600px] w-full">
        {lines.map((line, i) => (
          <div key={i} className="fade-in mb-2.5">
            {line}
          </div>
        ))}
        {showButtons && (
          <div className="fade-in mt-10 flex gap-5">
            <TerminalButton onClick={onStart}>
              [Start Building]
            </TerminalButton>
            <TerminalButton onClick={() => alert('Example coming soon!')}>
              [View Example]
            </TerminalButton>
          </div>
        )}
      </div>
    </div>
  );
};

export default LandingPage;

