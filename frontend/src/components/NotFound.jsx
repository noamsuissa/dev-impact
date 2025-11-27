import React from 'react';
import { useNavigate } from 'react-router-dom';
import TerminalButton from './common/TerminalButton';

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#2d2d2d] text-[#f1f1f1] font-mono flex items-center justify-center p-4">
      <div className="max-w-2xl w-full fade-in">
        <div className="space-y-6">
          {/* ASCII Art 404 */}
          <pre className="text-[#ff6b6b] text-sm md:text-base overflow-x-auto">
{`
  _  _    ___   _  _   
 | || |  / _ \\ | || |  
 | || |_| | | || || |_ 
 |__   _| | | ||__   _|
    | | | |_| |   | |  
    |_|  \\___/    |_|  
`}
          </pre>

          {/* Error Messages */}
          <div className="space-y-2 text-[#f1f1f1]">
            <div className="flex items-start gap-2">
              <span className="text-[#ff6b6b]">&gt;</span>
              <span>ERROR: Page not found</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-[#6b9eff]">&gt;</span>
              <span>The requested resource does not exist in this repository.</span>
            </div>
          </div>

          {/* Suggestions */}
          <div className="space-y-2 text-[#888] text-sm">
            <div>&gt; Possible reasons:</div>
            <div className="pl-4 space-y-1">
              <div>- The page may have been moved or deleted</div>
              <div>- The URL might contain a typo</div>
              <div>- The profile you're looking for might not exist</div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4">
            <TerminalButton 
              onClick={() => navigate('/')}
              className="flex-1"
            >
              &gt; Go Home
            </TerminalButton>
            <TerminalButton 
              onClick={() => navigate(-1)}
              className="flex-1"
            >
              &gt; Go Back
            </TerminalButton>
          </div>
        </div>
      </div>
    </div>
  );
}

