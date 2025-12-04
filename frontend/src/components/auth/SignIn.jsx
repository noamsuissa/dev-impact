import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import TerminalButton from '../common/TerminalButton';
import TerminalInput from '../common/TerminalInput';
import { useAuth } from '../../hooks/useAuth';
import { auth as authClient } from '../../utils/client';
import MFAChallenge from './MFAChallenge';

const SignIn = () => {
  const { refreshSession } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [rememberMe, setRememberMe] = useState(true);
  const [mfaChallengeId, setMfaChallengeId] = useState(null);

  const handleSignIn = async (e) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);

    try {
      const data = await authClient.signIn(email, password);

      // Check if MFA is required
      if (data.requires_mfa && data.mfa_challenge_id) {
        // Store credentials temporarily for MFA verification
        sessionStorage.setItem('mfa_email', email);
        sessionStorage.setItem('mfa_password', password);
        if (data.mfa_factor_id) {
          sessionStorage.setItem('mfa_factor_id', data.mfa_factor_id);
        }
        
        setMfaChallengeId(data.mfa_challenge_id);
        setLoading(false);
        return;
      }

      // Normal sign-in success
      setMessage('Signed in! Redirecting...');
      await refreshSession();
      setTimeout(() => {
        navigate('/dashboard', { replace: true });
      }, 1000);
    } catch (err) {
      setError(err.message || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const handleMFASuccess = async () => {
    setMessage('Signed in! Redirecting...');
    await refreshSession();
    setTimeout(() => {
      navigate('/dashboard', { replace: true });
    }, 1000);
  };

  const handleMFACancel = () => {
    sessionStorage.removeItem('mfa_email');
    sessionStorage.removeItem('mfa_password');
    setMfaChallengeId(null);
    setPassword('');
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-5">
      <div className="max-w-[500px] w-full">
        {/* Back to Home */}
        <div className="mb-5">
          <Link to="/" className="inline-flex items-center gap-2 text-terminal-text hover:text-terminal-orange transition-colors">
            <ArrowLeft size={16} />
            <span>Back to home</span>
          </Link>
        </div>

        {/* Header */}
        <div className="fade-in mb-10">
          <div className="text-2xl mb-2">
            &gt; Sign In
          </div>
          <div className="text-terminal-gray">
            Welcome back to dev-impact
          </div>
        </div>

        {/* MFA Challenge */}
        {mfaChallengeId ? (
          <MFAChallenge
            challengeId={mfaChallengeId}
            onSuccess={handleMFASuccess}
            onCancel={handleMFACancel}
          />
        ) : (
          /* Form */
          <form onSubmit={handleSignIn} className="space-y-5" autoComplete="on">
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
              autoComplete="email"
            />
          </div>

          {/* Password */}
          <div className="fade-in" style={{ animationDelay: '0.1s' }}>
            <div className="mb-2 flex justify-between items-center">
              <label htmlFor="password">&gt; Password:</label>
              <Link
                to="/forgot-password"
                className="text-terminal-orange text-xs hover:text-terminal-orange-light transition-colors"
              >
                Forgot password?
              </Link>
            </div>
            <TerminalInput
              type="password"
              name="password"
              id="password"
              value={password}
              onChange={setPassword}
              placeholder="••••••••"
              disabled={loading}
              required
              autoComplete="current-password"
            />
          </div>

          {/* Remember Me */}
          <div className="fade-in flex items-center gap-3" style={{ animationDelay: '0.2s' }}>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                disabled={loading}
                className="w-4 h-4 bg-terminal-bg-lighter border border-terminal-border cursor-pointer accent-terminal-orange"
              />
              <span className="text-terminal-text text-sm">Remember me</span>
            </label>
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
              disabled={loading || !email || !password}
            >
              {loading ? '[Processing...]' : '[Sign In]'}
            </TerminalButton>
          </div>
        </form>
        )}

        {/* Navigation */}
        <div className="fade-in mt-10 pt-10 border-t border-terminal-border" style={{ animationDelay: '0.3s' }}>
          <div className="text-terminal-gray mb-3">
            Don't have an account?
          </div>
          <div className="flex gap-3">
            <Link to="/signup">
              <TerminalButton disabled={loading}>
                [Create Account]
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

export default SignIn;

