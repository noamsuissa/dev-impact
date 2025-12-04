import React, { useState } from 'react';
import TerminalButton from '../common/TerminalButton';
import TerminalInput from '../common/TerminalInput';
import { auth as authClient } from '../../utils/client';

const MFAChallenge = ({ challengeId, onSuccess, onCancel }) => {
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleVerify = async (e) => {
    e.preventDefault();
    setError(null);
    
    if (!code || code.length !== 6) {
      setError('Please enter a valid 6-digit code');
      return;
    }

    setLoading(true);

    try {
      // Get email and password from session storage (stored during initial sign-in)
      const email = sessionStorage.getItem('mfa_email');
      const password = sessionStorage.getItem('mfa_password');
      
      if (!email || !password) {
        throw new Error('Session expired. Please sign in again.');
      }

      const data = await authClient.signIn(email, password, challengeId, code);
      
      // Clear stored credentials
      sessionStorage.removeItem('mfa_email');
      sessionStorage.removeItem('mfa_password');
      
      if (data.session) {
        onSuccess(data);
      } else {
        throw new Error('Failed to complete sign-in');
      }
    } catch (err) {
      setError(err.message || 'Invalid verification code');
      setCode('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in">
      <div className="mb-5">
        <div className="text-xl mb-2">
          &gt; Two-Factor Authentication
        </div>
        <div className="text-terminal-gray">
          Enter the 6-digit code from your authenticator app
        </div>
      </div>

      <form onSubmit={handleVerify} className="space-y-5">
        <div>
          <div className="mb-2">
            <label htmlFor="mfa-code">&gt; Verification Code:</label>
          </div>
          <TerminalInput
            type="text"
            name="mfa-code"
            id="mfa-code"
            value={code}
            onChange={(e) => {
              const value = e.target.value.replace(/\D/g, '').slice(0, 6);
              setCode(value);
              setError(null);
            }}
            placeholder="000000"
            disabled={loading}
            required
            autoComplete="one-time-code"
            maxLength={6}
            className="text-center text-2xl tracking-widest"
          />
        </div>

        {error && (
          <div className="text-red-400 bg-red-400/10 border border-red-400/30 p-3 rounded">
            ✗ {error}
          </div>
        )}

        <div className="flex gap-5 pt-5">
          <TerminalButton 
            type="submit" 
            disabled={loading || code.length !== 6}
          >
            {loading ? '[Verifying...]' : '[Verify]'}
          </TerminalButton>
          {onCancel && (
            <TerminalButton 
              type="button"
              onClick={onCancel}
              disabled={loading}
            >
              [Cancel]
            </TerminalButton>
          )}
        </div>
      </form>

      <div className="mt-5 text-terminal-gray text-sm">
        <div>&gt; Having trouble? Make sure your device time is correct</div>
        <div>&gt; The code refreshes every 30 seconds</div>
      </div>
    </div>
  );
};

export default MFAChallenge;

