import React, { useState, useMemo } from 'react';
import TerminalButton from './common/TerminalButton';
import TerminalInput from './common/TerminalInput';
import { auth } from '../utils/client';

const ResetPassword = ({ onSuccess }) => {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

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

  const handleUpdatePassword = async (e) => {
    e.preventDefault();
    setError(null);
    setMessage(null);

    // Validation
    if (!passwordValidation.isValid) {
      setError('Please meet all password requirements');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      await auth.updatePassword(password);

      setMessage('Password updated successfully! Redirecting...');
      setTimeout(() => {
        if (onSuccess) onSuccess();
      }, 2000);
    } catch (err) {
      setError(err.message || 'Failed to update password');
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
            &gt; Set New Password
          </div>
          <div className="text-terminal-gray">
            Choose a strong password for your account
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleUpdatePassword} className="space-y-5">
          {/* New Password */}
          <div className="fade-in">
            <div className="mb-2">&gt; New Password:</div>
            <TerminalInput
              type="password"
              value={password}
              onChange={setPassword}
              placeholder="••••••••"
              disabled={loading}
              required
            />
          </div>

          {/* Password Requirements */}
          {password.length > 0 && (
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
          <div className="fade-in" style={{ animationDelay: '0.1s' }}>
            <div className="mb-2">&gt; Confirm New Password:</div>
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
              disabled={
                loading || 
                !password || 
                !confirmPassword || 
                !passwordValidation.isValid || 
                password !== confirmPassword
              }
            >
              {loading ? '[Updating...]' : '[Update Password]'}
            </TerminalButton>
          </div>
        </form>

        {/* Help Text */}
        <div className="fade-in mt-10 text-terminal-gray text-sm" style={{ animationDelay: '0.3s' }}>
          <div className="mb-1">&gt; After updating, you'll be redirected to sign in</div>
          <div>&gt; Use your new password to access your account</div>
        </div>
      </div>
    </div>
  );
};

// Password requirement indicator component
const PasswordRequirement = ({ met, children }) => (
  <div className="flex items-center gap-2">
    <span className={met ? 'text-terminal-green' : 'text-terminal-gray'}>
      {met ? '✓' : '○'}
    </span>
    <span className={met ? 'text-terminal-green' : 'text-terminal-gray'}>
      {children}
    </span>
  </div>
);

export default ResetPassword;

