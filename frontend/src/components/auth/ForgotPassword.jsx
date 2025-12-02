import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import TerminalButton from '../common/TerminalButton';
import TerminalInput from '../common/TerminalInput';
import { auth as authClient } from '../../utils/client';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  const handlePasswordReset = async (e) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);

    try {
      await authClient.resetPassword(email);

      setMessage('Password reset email sent! Check your inbox.');
      setEmail('');
    } catch (err) {
      setError(err.message || 'Failed to send reset email');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-5">
      <div className="max-w-[500px] w-full">
        {/* Header */}
        <div className="fade-in mb-10">
          <div className="text-2xl mb-2">
            &gt; Reset Password
          </div>
          <div className="text-terminal-gray">
            Enter your email to receive a password reset link
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handlePasswordReset} className="space-y-5" autoComplete="on">
          {/* Email */}
          <div className="fade-in">
            <div className="mb-2">
              <label htmlFor="email">&gt; Email:</label>
            </div>
            <TerminalInput
              type="email"
              name="email"
              id="email"
              value={email}
              onChange={setEmail}
              placeholder="developer@example.com"
              disabled={loading}
              required
              autoComplete="username"
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="fade-in text-red-400 bg-red-400/10 border border-red-400/30 p-3 rounded">
              ✗ {error}
            </div>
          )}

          {/* Success Message */}
          {message && (
            <div className="fade-in text-terminal-green bg-terminal-green/10 border border-terminal-green/30 p-3 rounded">
              ✓ {message}
            </div>
          )}

          {/* Submit Button */}
          <div className="fade-in flex gap-5 pt-5" style={{ animationDelay: '0.2s' }}>
            <TerminalButton 
              type="submit" 
              disabled={loading || !email}
            >
              {loading ? '[Processing...]' : '[Send Reset Link]'}
            </TerminalButton>
          </div>
        </form>

        {/* Navigation */}
        <div className="fade-in mt-10 pt-10 border-t border-terminal-border" style={{ animationDelay: '0.3s' }}>
          <div className="text-terminal-gray mb-3">
            Remember your password?
          </div>
          <div className="flex gap-3">
            <Link to="/signin">
              <TerminalButton disabled={loading}>
                [Sign In]
              </TerminalButton>
            </Link>
          </div>
        </div>

        {/* Help Text */}
        <div className="fade-in mt-10 text-terminal-gray text-sm" style={{ animationDelay: '0.4s' }}>
          <div className="mb-1">&gt; Secure authentication powered by Supabase</div>
          <div>&gt; Your data is encrypted and protected</div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;

