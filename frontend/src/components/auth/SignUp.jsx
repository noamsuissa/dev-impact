import React, { useState, useMemo, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import HCaptcha from '@hcaptcha/react-hcaptcha';
import TerminalButton from '../common/TerminalButton';
import TerminalInput from '../common/TerminalInput';
import { useAuth } from '../../hooks/useAuth';
import { auth as authClient } from '../../utils/client';

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

const SignUp = () => {
  const { refreshSession } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [showPasswordHints, setShowPasswordHints] = useState(false);
  const [captchaToken, setCaptchaToken] = useState(null);
  const captchaRef = useRef(null);

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

    const hCaptchaSiteKey = import.meta.env.VITE_HCAPTCHA_SITE_KEY;
    const isCaptchaEnabled = !!hCaptchaSiteKey;

    if (isCaptchaEnabled && !captchaToken) {
      setError('Please complete the captcha');
      return;
    }

    setLoading(true);

    try {
      // Sign up the user
      const data = await authClient.signUp(
        email, 
        password, 
        isCaptchaEnabled ? captchaToken : 'localhost_bypass'
      );

      // Check if email confirmation is required
      if (data.requires_email_verification) {
        setMessage('Check your email to verify your account');
        setTimeout(() => {
          navigate('/signin');
        }, 1800);
      } else if (data.user && data.session) {
        // Successfully signed up and logged in automatically
        setMessage('Account created! Redirecting...');
        await refreshSession();
        setTimeout(() => {
            navigate('/onboarding');
        }, 1500);
      } else {
        setError('Unexpected response from authentication service');
      }
    } catch (err) {
      console.error('Auth error details:', err);
      setError(err.message || 'Failed to create account');
      // Reset captcha on error
      if (captchaRef.current) {
        captchaRef.current.resetCaptcha();
        setCaptchaToken(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const onCaptchaVerify = (token) => {
    setCaptchaToken(token);
    setError(null);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-5">
      <div className="max-w-[500px] w-full">
        {/* Header */}
        <div className="fade-in mb-10">
          <div className="text-2xl mb-2">
            &gt; Create Account
          </div>
          <div className="text-terminal-gray">
            Start showcasing your developer impact
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSignUp} className="space-y-5" autoComplete="on">
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

          {/* Password */}
          <div className="fade-in" style={{ animationDelay: '0.1s' }}>
            <div className="mb-2">
              <label htmlFor="password">&gt; Password:</label>
            </div>
            <TerminalInput
              type="password"
              name="new-password"
              id="password"
              value={password}
              onChange={(val) => {
                setPassword(val);
                setShowPasswordHints(true);
              }}
              placeholder="••••••••"
              disabled={loading}
              required
              autoComplete="new-password"
            />
          </div>

          {/* Password Requirements */}
          {showPasswordHints && password.length > 0 && (
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

          {/* Confirm Password */}
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

          {/* hCaptcha - Only render if site key is present */}
          {import.meta.env.VITE_HCAPTCHA_SITE_KEY && (
            <div className="fade-in flex justify-center py-2" style={{ animationDelay: '0.25s' }}>
              <HCaptcha
                sitekey={import.meta.env.VITE_HCAPTCHA_SITE_KEY}
                onVerify={onCaptchaVerify}
                ref={captchaRef}
                theme="dark"
              />
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
          <div className="fade-in flex gap-5 pt-5" style={{ animationDelay: '0.3s' }}>
            <TerminalButton 
              type="submit" 
              disabled={
                loading || 
                !email || 
                !password ||
                !confirmPassword || 
                !passwordValidation.isValid || 
                password !== confirmPassword ||
                (import.meta.env.VITE_HCAPTCHA_SITE_KEY && !captchaToken)
              }
            >
              {loading ? '[Processing...]' : '[Create Account]'}
            </TerminalButton>
          </div>
        </form>

        {/* Navigation */}
        <div className="fade-in mt-10 pt-10 border-t border-terminal-border" style={{ animationDelay: '0.4s' }}>
          <div className="text-terminal-gray mb-3">
            Already have an account?
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
        <div className="fade-in mt-10 text-terminal-gray text-sm" style={{ animationDelay: '0.5s' }}>
          <div className="mb-1">&gt; Secure authentication powered by Supabase</div>
          <div>&gt; Your data is encrypted and protected</div>
        </div>
      </div>
    </div>
  );
};

export default SignUp;