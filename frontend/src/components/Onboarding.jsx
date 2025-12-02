import React, { useState } from 'react';
import TerminalButton from './common/TerminalButton';
import TerminalInput from './common/TerminalInput';
import { completeGitHubAuth } from '../utils/githubAuth';
import { profiles } from '../utils/client';

const Onboarding = ({ onComplete }) => {
  const [step, setStep] = useState(0);
  const [name, setName] = useState('');
  const [username, setUsername] = useState('');
  const [usernameError, setUsernameError] = useState(null);
  const [isCheckingUsername, setIsCheckingUsername] = useState(false);
  const [githubState, setGithubState] = useState('initial'); // initial, loading, awaiting, success, error
  const [githubData, setGithubData] = useState(null);
  const [deviceCode, setDeviceCode] = useState(null);
  const [error, setError] = useState(null);

  const steps = [
    {
      prompt: '> Welcome to dev-impact',
      input: null
    },
    {
      prompt: "> Let's set up your profile...",
      input: null
    },
    {
      prompt: '> Your name:',
      input: 'name'
    },
    {
      prompt: '> Choose a username:',
      input: 'username'
    },
    {
      prompt: '> Connect your GitHub account (optional):',
      input: 'github'
    }
  ];

  const validateUsername = (value) => {
    if (!value) return 'Username is required';
    if (value.length < 3) return 'Username must be at least 3 characters';
    if (value.length > 50) return 'Username must be less than 50 characters';
    if (!/^[a-z0-9-]+$/.test(value)) return 'Only lowercase letters, numbers, and hyphens allowed';
    return null;
  };

  const handleNext = async () => {
    if (steps[step].input === 'username') {
      const validationError = validateUsername(username);
      if (validationError) {
        setUsernameError(validationError);
        return;
      }

      setIsCheckingUsername(true);
      setUsernameError(null);
      try {
        const result = await profiles.checkUsername(username);
        if (!result.available) {
          setUsernameError('Username is already taken');
          setIsCheckingUsername(false);
          return;
        }
      } catch (err) {
        console.error('Error checking username:', err);
        setUsernameError('Failed to validate username. Please try again.');
        setIsCheckingUsername(false);
        return;
      }
      setIsCheckingUsername(false);
    }

    if (step < steps.length - 1) {
      setStep(step + 1);
    } else {
      // Complete onboarding
      const userData = {
        name,
        username,
        github: githubData || null
      };
      onComplete(userData);
    }
  };

  const handleConnectGitHub = async () => {
    setGithubState('loading');
    setError(null);

    try {
      const result = await completeGitHubAuth(
        ({ userCode, verificationUri }) => {
          setDeviceCode({ userCode, verificationUri });
          setGithubState('awaiting');
        },
        (message) => {
          console.log('GitHub OAuth progress:', message);
        }
      );

      setGithubData(result);
      setGithubState('success');
    } catch (err) {
      console.error('GitHub OAuth error:', err);
      setError(err.message);
      setGithubState('error');
    }
  };

  const handleSkipGitHub = () => {
    setGithubData(null);
    setGithubState('initial');
    handleNext();
  };

  const handleRetryGitHub = () => {
    setGithubState('initial');
    setError(null);
    setDeviceCode(null);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-5">
      <div className="max-w-[600px] w-full">
        {steps.slice(0, step + 1).map((s, i) => (
          <div key={i} className="fade-in mb-5">
            <div className="mb-2.5">{s.prompt}</div>
            
            {/* Name input */}
            {i === step && s.input === 'name' && (
              <TerminalInput 
                value={name} 
                onChange={setName} 
                placeholder="John Doe" 
                autoFocus
              />
            )}
            {i < step && s.input === 'name' && (
              <div className="text-terminal-orange">{name}</div>
            )}

            {/* Username input */}
            {i === step && s.input === 'username' && (
              <div>
                <TerminalInput 
                  value={username} 
                  onChange={(val) => {
                    setUsername(val.toLowerCase());
                    setUsernameError(null);
                  }} 
                  placeholder="johndoe" 
                  autoFocus
                />
                <div className="mt-2 text-sm text-terminal-gray">
                  3-50 characters, lowercase letters, numbers, and hyphens only
                </div>
                {usernameError && (
                  <div className="mt-2 text-red-400">
                    ✗ {usernameError}
                  </div>
                )}
              </div>
            )}
            {i < step && s.input === 'username' && (
              <div className="text-terminal-orange">@{username}</div>
            )}

            {/* GitHub connection */}
            {i === step && s.input === 'github' && (
              <div className="mt-5">
                {githubState === 'initial' && (
                  <div className="flex gap-5">
                    <TerminalButton onClick={handleConnectGitHub}>
                      [Connect GitHub]
                    </TerminalButton>
                    <TerminalButton onClick={handleSkipGitHub}>
                      [Skip]
                    </TerminalButton>
                  </div>
                )}

                {githubState === 'loading' && (
                  <div className="text-terminal-orange">
                    &gt; Initiating GitHub authentication...
                  </div>
                )}

                {githubState === 'awaiting' && deviceCode && (
                  <div className="space-y-3">
                    <div className="text-terminal-orange">
                      &gt; Please authorize this device:
                    </div>
                    <div className="bg-[#1e1e1e] p-4 rounded border border-terminal-orange/30">
                      <div className="mb-2">
                        <span className="text-terminal-gray">Code: </span>
                        <span className="text-terminal-orange font-bold text-xl tracking-wider">
                          {deviceCode.userCode}
                        </span>
                      </div>
                      <div className="mb-3">
                        <span className="text-terminal-gray">Visit: </span>
                        <a 
                          href={deviceCode.verificationUri}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-terminal-orange underline hover:text-terminal-orange-light"
                        >
                          {deviceCode.verificationUri}
                        </a>
                      </div>
                      <div className="text-terminal-gray text-sm">
                        Waiting for authorization...
                      </div>
                    </div>
                  </div>
                )}

                {githubState === 'success' && githubData && (
                  <div className="space-y-2">
                    <div className="text-terminal-green">
                      ✓ Successfully connected to GitHub
                    </div>
                    <div className="flex items-center gap-3 bg-[#1e1e1e] p-3 rounded border border-terminal-green/30">
                      <img 
                        src={githubData.avatar_url} 
                        alt={githubData.username}
                        className="w-10 h-10 rounded-full"
                      />
                      <div>
                        <div className="text-terminal-orange font-bold">
                          @{githubData.username}
                        </div>
                        {githubData.name && (
                          <div className="text-terminal-gray text-sm">
                            {githubData.name}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {githubState === 'error' && (
                  <div className="space-y-3">
                    <div className="text-red-400">
                      ✗ Error: {error}
                    </div>
                    <div className="flex gap-5">
                      <TerminalButton onClick={handleRetryGitHub}>
                        [Retry]
                      </TerminalButton>
                      <TerminalButton onClick={handleSkipGitHub}>
                        [Skip]
                      </TerminalButton>
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {i < step && s.input === 'github' && (
              <div className="text-terminal-orange">
                {githubData ? `@${githubData.username}` : '(skipped)'}
              </div>
            )}
          </div>
        ))}

        {/* Show continue button when GitHub step is complete */}
        {step === steps.length - 1 && (githubState === 'success' || githubState === 'initial') && (
          <div className="fade-in mt-10">
            <TerminalButton onClick={handleNext}>
              [Continue]
            </TerminalButton>
          </div>
        )}

        {/* Next button for non-GitHub steps */}
        {step < steps.length - 1 && steps[step].input === 'name' && (
          <div className="mt-5">
            <TerminalButton onClick={handleNext} disabled={!name.trim()}>
              [Next]
            </TerminalButton>
          </div>
        )}

        {step < steps.length - 1 && steps[step].input === 'username' && (
          <div className="mt-5">
            <TerminalButton onClick={handleNext} disabled={!username.trim() || isCheckingUsername}>
              {isCheckingUsername ? '[Checking...]' : '[Next]'}
            </TerminalButton>
          </div>
        )}

        {step < steps.length - 1 && !steps[step].input && (
          <div className="mt-5">
            <TerminalButton onClick={handleNext}>
              [Continue]
            </TerminalButton>
          </div>
        )}
      </div>
    </div>
  );
};

export default Onboarding;
