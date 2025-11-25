import React, { useState } from 'react';
import TerminalButton from './common/TerminalButton';
import TerminalInput from './common/TerminalInput';

const Onboarding = ({ onComplete }) => {
  const [step, setStep] = useState(0);
  const [name, setName] = useState('');
  const [github, setGithub] = useState('');

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
      prompt: '> GitHub username (optional):',
      input: 'github'
    }
  ];

  const handleNext = () => {
    if (step < steps.length - 1) {
      setStep(step + 1);
    } else {
      onComplete({ name, github });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-5">
      <div className="max-w-[600px] w-full">
        {steps.slice(0, step + 1).map((s, i) => (
          <div key={i} className="fade-in mb-5">
            <div className="mb-2.5">{s.prompt}</div>
            {i === step && s.input === 'name' && (
              <TerminalInput value={name} onChange={setName} placeholder="John Doe" />
            )}
            {i === step && s.input === 'github' && (
              <TerminalInput value={github} onChange={setGithub} placeholder="johndoe" />
            )}
            {i < step && s.input === 'name' && (
              <div className="text-terminal-orange">{name}</div>
            )}
            {i < step && s.input === 'github' && (
              <div className="text-terminal-orange">{github || '(skipped)'}</div>
            )}
          </div>
        ))}
        {step === steps.length - 1 && (
          <div className="fade-in mt-10 flex gap-5">
            <TerminalButton onClick={handleNext}>
              [Continue]
            </TerminalButton>
            <TerminalButton onClick={() => onComplete({ name, github: '' })}>
              [Skip GitHub]
            </TerminalButton>
          </div>
        )}
        {step < steps.length - 1 && steps[step].input && (
          <div className="mt-5">
            <TerminalButton onClick={handleNext}>
              [Next]
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

