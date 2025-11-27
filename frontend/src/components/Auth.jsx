import React, { useState, useMemo } from 'react';
import TerminalButton from './common/TerminalButton';
import TerminalInput from './common/TerminalInput';
import { useAuth } from '../hooks/useAuth';
import { auth as authClient } from '../utils/client';

const Auth = ({ onAuthSuccess }) => {
  const { refreshSession } = useAuth();
  const [mode, setMode] = useState('signin'); // 'signin', 'signup', or 'reset'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [showPasswordHints, setShowPasswordHints] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);

  // Password validation rules
  const passwordValidation = useMemo(() => {
    const rules = {
      minLength: password.length >= 8,
      hasUpperCase: /[A-Z]/.test(password),
      hasLowerCase: /[a-z]/.test(password),
      hasNumber: /[0-9]/.test(password),
      hasSpecial: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    };

    const isValid = rules.minLength && rules.hasUpperCase && rules.hasLowerCase && rules.hasNumber && rules.hasSpecial;
    
    return { rules, isValid };
  }, [password]);

  const handleSignUp = async (e) => {
    e.preventDefault();
    setError(null);
    setMessage(null);

    // Validation
    if (!passwordValidation.isValid) {
      setError('Please meet all password requirements');
      setShowPasswordHints(true);
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      // Sign up the user
      const data = await authClient.signUp(email, password);

      console.log('Signup successful:', data);

      // Check if email confirmation is required
      if (data.requires_email_verification) {
        setMessage('Check your email to verify your account');
      } else if (data.user && data.session) {
        // Successfully signed up and logged in
        setMessage('Account created! Redirecting...');
        await refreshSession();
        setTimeout(() => onAuthSuccess(data.user), 1500);
      } else {
        setError('Unexpected response from authentication service');
      }
    } catch (err) {
      console.error('Auth error details:', err);
      setError(err.message || 'Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  const handleSignIn = async (e) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);

    try {
      const data = await authClient.signIn(email, password);

      setMessage('Signed in! Redirecting...');
      await refreshSession();
      setTimeout(() => onAuthSuccess(data.user), 1000);
    } catch (err) {
      setError(err.message || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

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

  const toggleMode = (newMode) => {
    setMode(newMode || (mode === 'signin' ? 'signup' : 'signin'));
    setError(null);
    setMessage(null);
    setEmail('');
    setPassword('');
    setConfirmPassword('');
    setShowPasswordHints(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-5">
      <div className="max-w-[500px] w-full" key={mode}>
        {/* Header */}
        <div className="fade-in mb-10">
          <div className="text-2xl mb-2">
            &gt; {mode === 'signin' ? 'Sign In' : mode === 'signup' ? 'Create Account' : 'Reset Password'}
          </div>
          <div className="text-terminal-gray">
            {mode === 'signin' 
              ? 'Welcome back to dev-impact' 
              : mode === 'signup'
              ? 'Start showcasing your developer impact'
              : 'Enter your email to receive a password reset link'}
          </div>
        </div>

        {/* Form */}
        <form 
          onSubmit={mode === 'signin' ? handleSignIn : mode === 'signup' ? handleSignUp : handlePasswordReset} 
          className="space-y-5"
          autoComplete="on"
        >
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
              autoComplete={mode === 'signin' ? 'email' : 'username'}
            />
          </div>

          {/* Password (hidden in reset mode) */}
          {mode !== 'reset' && (
            <div className="fade-in" style={{ animationDelay: '0.1s' }}>
              <div className="mb-2 flex justify-between items-center">
                <label htmlFor="password">&gt; Password:</label>
                {mode === 'signin' && (
                  <button
                    type="button"
                    onClick={() => toggleMode('reset')}
                    className="text-terminal-orange text-xs hover:text-terminal-orange-light transition-colors"
                  >
                    Forgot password?
                  </button>
                )}
              </div>
              <TerminalInput
                type="password"
                name={mode === 'signin' ? 'password' : 'new-password'}
                id="password"
                value={password}
                onChange={(val) => {
                  setPassword(val);
                  if (mode === 'signup') setShowPasswordHints(true);
                }}
                placeholder="••••••••"
                disabled={loading}
                required
                autoComplete={mode === 'signin' ? 'current-password' : 'new-password'}
              />
            </div>
          )}

          {/* Password Requirements (signup only) */}
          {mode === 'signup' && showPasswordHints && password.length > 0 && (
            <div className="fade-in mt-3 space-y-1.5 text-sm bg-terminal-bg-lighter border border-terminal-border p-3 rounded">
              <div className="text-terminal-gray mb-2">&gt; Password requirements:</div>
              <PasswordRequirement met={passwordValidation.rules.minLength}>
                At least 8 characters
              </PasswordRequirement>
              <PasswordRequirement met={passwordValidation.rules.hasUpperCase}>
                One uppercase letter
              </PasswordRequirement>
              <PasswordRequirement met={passwordValidation.rules.hasLowerCase}>
                One lowercase letter
              </PasswordRequirement>
              <PasswordRequirement met={passwordValidation.rules.hasNumber}>
                One number
              </PasswordRequirement>
              <PasswordRequirement met={passwordValidation.rules.hasSpecial}>
                One special character (!@#$%^&*...)
              </PasswordRequirement>
            </div>
          )}

          {/* Remember Me (signin only) */}
          {mode === 'signin' && (
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
          )}

          {/* Confirm Password (signup only) */}
          {mode === 'signup' && (
            <div className="fade-in" style={{ animationDelay: '0.2s' }}>
              <div className="mb-2">
                <label htmlFor="confirm-password">&gt; Confirm Password:</label>
              </div>
              <TerminalInput
                type="password"
                name="confirm-password"
                id="confirm-password"
                value={confirmPassword}
                onChange={setConfirmPassword}
                placeholder="••••••••"
                disabled={loading}
                required
                autoComplete="new-password"
              />
              {confirmPassword.length > 0 && (
                <div className="mt-2 text-sm">
                  {password === confirmPassword ? (
                    <span className="text-terminal-green">✓ Passwords match</span>
                  ) : (
                    <span className="text-terminal-orange">○ Passwords do not match</span>
                  )}
                </div>
              )}
            </div>
          )}

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
          <div className="fade-in flex gap-5 pt-5" style={{ animationDelay: mode === 'signup' ? '0.3s' : '0.2s' }}>
            <TerminalButton 
              type="submit" 
              disabled={
                loading || 
                !email || 
                (mode !== 'reset' && !password) ||
                (mode === 'signup' && (!confirmPassword || !passwordValidation.isValid || password !== confirmPassword))
              }
            >
              {loading 
                ? '[Processing...]' 
                : mode === 'signin' 
                ? '[Sign In]' 
                : mode === 'signup'
                ? '[Create Account]'
                : '[Send Reset Link]'}
            </TerminalButton>
          </div>
        </form>

        {/* Toggle Mode */}
        <div className="fade-in mt-10 pt-10 border-t border-terminal-border" style={{ animationDelay: mode === 'signup' ? '0.4s' : '0.3s' }}>
          <div className="text-terminal-gray mb-3">
            {mode === 'signin' 
              ? "Don't have an account?" 
              : mode === 'signup'
              ? "Already have an account?"
              : "Remember your password?"}
          </div>
          <div className="flex gap-3">
            <TerminalButton 
              onClick={() => toggleMode(mode === 'reset' ? 'signin' : mode === 'signin' ? 'signup' : 'signin')} 
              disabled={loading}
            >
              {mode === 'signin' ? '[Create Account]' : '[Sign In]'}
            </TerminalButton>
            {mode === 'signup' && (
              <TerminalButton onClick={() => toggleMode('reset')} disabled={loading}>
                [Forgot Password?]
              </TerminalButton>
            )}
          </div>
        </div>

        {/* Help Text */}
        <div className="fade-in mt-10 text-terminal-gray text-sm" style={{ animationDelay: mode === 'signup' ? '0.5s' : '0.4s' }}>
          <div className="mb-1">&gt; Secure authentication powered by Supabase</div>
          <div>&gt; Your data is encrypted and protected</div>
        </div>
      </div>
    </div>
  );
};

// Password requirement indicator component
const PasswordRequirement = ({ met, optional, children }) => (
  <div className="flex items-center gap-2">
    <span className={met ? 'text-terminal-green' : 'text-terminal-gray'}>
      {met ? '✓' : '○'}
    </span>
    <span className={met ? 'text-terminal-green' : 'text-terminal-gray'}>
      {children}
      {optional && <span className="text-terminal-gray text-xs ml-1">(optional)</span>}
    </span>
  </div>
);

export default Auth;

