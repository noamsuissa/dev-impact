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
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{ maxWidth: '600px', width: '100%' }}>
        {steps.slice(0, step + 1).map((s, i) => (
          <div key={i} className="fade-in" style={{ marginBottom: '20px' }}>
            <div style={{ marginBottom: '10px' }}>{s.prompt}</div>
            {i === step && s.input === 'name' && (
              <TerminalInput value={name} onChange={setName} placeholder="John Doe" />
            )}
            {i === step && s.input === 'github' && (
              <TerminalInput value={github} onChange={setGithub} placeholder="johndoe" />
            )}
            {i < step && s.input === 'name' && (
              <div style={{ color: '#00aa00' }}>{name}</div>
            )}
            {i < step && s.input === 'github' && (
              <div style={{ color: '#00aa00' }}>{github || '(skipped)'}</div>
            )}
          </div>
        ))}
        {step === steps.length - 1 && (
          <div className="fade-in" style={{ marginTop: '40px', display: 'flex', gap: '20px' }}>
            <TerminalButton onClick={handleNext}>
              [Continue]
            </TerminalButton>
            <TerminalButton onClick={() => onComplete({ name, github: '' })}>
              [Skip GitHub]
            </TerminalButton>
          </div>
        )}
        {step < steps.length - 1 && steps[step].input && (
          <div style={{ marginTop: '20px' }}>
            <TerminalButton onClick={handleNext}>
              [Next]
            </TerminalButton>
          </div>
        )}
        {step < steps.length - 1 && !steps[step].input && (
          <div style={{ marginTop: '20px' }}>
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

