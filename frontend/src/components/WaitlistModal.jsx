import React, { useState, useEffect } from 'react';
import { X, CheckCircle2 } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import TerminalInput from './common/TerminalInput';
import { waitlist } from '../utils/client';

const WaitlistModal = ({ isOpen, onClose }) => {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setEmail('');
      setName('');
      setError(null);
      setSuccess(false);
    }
  }, [isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!email.trim()) {
      setError('Email is required');
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError('Please enter a valid email address');
      return;
    }

    setIsSubmitting(true);
    try {
      await waitlist.signup(email.trim(), name.trim() || null);
      setSuccess(true);
      // Auto-close after 3 seconds
      setTimeout(() => {
        onClose();
        setSuccess(false);
      }, 3000);
    } catch (err) {
      setError(err.message || 'Failed to join waitlist. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget && !success) {
          onClose();
        }
      }}
    >
      <div className="bg-terminal-bg border border-terminal-border p-6 max-w-md w-full">
        {success ? (
          <>
            <div className="flex items-center justify-between mb-6">
              <div className="text-lg text-terminal-orange">
                &gt; Success!
              </div>
              <button
                onClick={onClose}
                className="text-terminal-gray hover:text-terminal-orange transition-colors"
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="text-center py-6">
              <CheckCircle2 className="mx-auto mb-4 text-terminal-green" size={48} />
              <div className="text-terminal-text mb-2">
                You're on the waitlist!
              </div>
              <div className="text-terminal-gray text-sm">
                Check your email for confirmation. We'll notify you when Dev Impact Pro is ready.
              </div>
            </div>
          </>
        ) : (
          <>
            <div className="flex items-center justify-between mb-6">
              <div className="text-lg text-terminal-orange">
                &gt; Join Waitlist
              </div>
              <button
                onClick={onClose}
                className="text-terminal-gray hover:text-terminal-orange transition-colors"
                disabled={isSubmitting}
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm text-terminal-gray mb-2">
                  Email *
                </label>
                <TerminalInput
                  type="email"
                  value={email}
                  onChange={setEmail}
                  placeholder="your.email@example.com"
                  disabled={isSubmitting}
                  required
                  autoFocus
                  autoComplete="email"
                />
              </div>

              <div>
                <label className="block text-sm text-terminal-gray mb-2">
                  Name (optional)
                </label>
                <TerminalInput
                  type="text"
                  value={name}
                  onChange={setName}
                  placeholder="Your name"
                  disabled={isSubmitting}
                  autoComplete="name"
                />
              </div>

              {error && (
                <div className="text-red-400 text-sm">
                  ✗ {error}
                </div>
              )}

              <div className="flex gap-3 justify-end pt-4">
                <TerminalButton
                  type="button"
                  onClick={onClose}
                  disabled={isSubmitting}
                >
                  [Cancel]
                </TerminalButton>
                <TerminalButton
                  type="submit"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? '[Joining...]' : '[Join Waitlist]'}
                </TerminalButton>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
};

export default WaitlistModal;

