import React, { useState, useMemo } from 'react';
import TerminalButton from './common/TerminalButton';
import TerminalInput from './common/TerminalInput';
import { useSupabase } from '../hooks/useSupabase';

const Auth = ({ onAuthSuccess }) => {
  const { supabase } = useSupabase();
  const [mode, setMode] = useState('signin'); // 'signin' or 'signup'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [showPasswordHints, setShowPasswordHints] = useState(false);

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
      const { data, error: signUpError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: window.location.origin
        }
      });

      if (signUpError) {
        console.error('Signup error:', signUpError);
        throw signUpError;
      }

      console.log('Signup successful:', data);

      // Check if email confirmation is required
      if (data?.user?.identities?.length === 0) {
        setError('An account with this email already exists');
      } else if (data?.user && !data.session) {
        setMessage('Check your email to verify your account');
      } else if (data?.user && data.session) {
        // Successfully signed up and logged in
        setMessage('Account created! Redirecting...');
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
      const { data, error: signInError } = await supabase.auth.signInWithPassword({
        email,
        password
      });

      if (signInError) throw signInError;

      setMessage('Signed in! Redirecting...');
      setTimeout(() => onAuthSuccess(data.user), 1000);
    } catch (err) {
      setError(err.message || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setMode(mode === 'signin' ? 'signup' : 'signin');
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
            &gt; {mode === 'signin' ? 'Sign In' : 'Create Account'}
          </div>
          <div className="text-terminal-gray">
            {mode === 'signin' 
              ? 'Welcome back to dev-impact' 
              : 'Start showcasing your developer impact'}
          </div>
        </div>

        {/* Form */}
        <form onSubmit={mode === 'signin' ? handleSignIn : handleSignUp} className="space-y-5">
          {/* Email */}
          <div className="fade-in">
            <div className="mb-2">&gt; Email:</div>
            <TerminalInput
              type="email"
              value={email}
              onChange={setEmail}
              placeholder="developer@example.com"
              disabled={loading}
              required
            />
          </div>

          {/* Password */}
          <div className="fade-in" style={{ animationDelay: '0.1s' }}>
            <div className="mb-2">&gt; Password:</div>
            <TerminalInput
              type="password"
              value={password}
              onChange={(val) => {
                setPassword(val);
                if (mode === 'signup') setShowPasswordHints(true);
              }}
              placeholder="••••••••"
              disabled={loading}
              required
            />
          </div>

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

          {/* Confirm Password (signup only) */}
          {mode === 'signup' && (
            <div className="fade-in" style={{ animationDelay: '0.2s' }}>
              <div className="mb-2">&gt; Confirm Password:</div>
              <TerminalInput
                type="password"
                value={confirmPassword}
                onChange={setConfirmPassword}
                placeholder="••••••••"
                disabled={loading}
                required
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
                !password || 
                (mode === 'signup' && (!confirmPassword || !passwordValidation.isValid || password !== confirmPassword))
              }
            >
              {loading ? '[Processing...]' : mode === 'signin' ? '[Sign In]' : '[Create Account]'}
            </TerminalButton>
          </div>
        </form>

        {/* Toggle Mode */}
        <div className="fade-in mt-10 pt-10 border-t border-terminal-border" style={{ animationDelay: mode === 'signup' ? '0.4s' : '0.3s' }}>
          <div className="text-terminal-gray mb-3">
            {mode === 'signin' ? "Don't have an account?" : "Already have an account?"}
          </div>
          <TerminalButton onClick={toggleMode} disabled={loading}>
            {mode === 'signin' ? '[Create Account]' : '[Sign In]'}
          </TerminalButton>
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

