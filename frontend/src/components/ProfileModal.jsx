import React, { useState } from 'react';
import { X } from 'lucide-react';
import TerminalButton from './common/TerminalButton';

const ProfileModal = ({ isOpen, onClose, onSubmit, profile = null }) => {
  const [name, setName] = useState(profile?.name || '');
  const [description, setDescription] = useState(profile?.description || '');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  React.useEffect(() => {
    if (isOpen) {
      setName(profile?.name || '');
      setDescription(profile?.description || '');
      setError(null);
    }
  }, [isOpen, profile]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError('Profile name is required');
      return;
    }

    if (name.trim().length < 2) {
      setError('Profile name must be at least 2 characters');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({
        name: name.trim(),
        description: description.trim() || null
      });
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to save profile');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-terminal-bg border border-terminal-border p-6 max-w-md w-full">
        <div className="flex items-center justify-between mb-6">
          <div className="text-lg text-terminal-orange">
            {profile ? 'Edit Profile' : 'Create New Profile'}
          </div>
          <button
            onClick={onClose}
            className="text-terminal-gray hover:text-terminal-orange transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-terminal-gray mb-2">
              Profile Name *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-terminal-bg-lighter border border-terminal-border px-3 py-2 text-terminal-text focus:outline-none focus:border-terminal-orange"
              placeholder="e.g., AI Projects, Game Dev, Full Stack"
              disabled={isSubmitting}
              autoFocus
            />
          </div>

          <div>
            <label className="block text-sm text-terminal-gray mb-2">
              Description (optional)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-terminal-bg-lighter border border-terminal-border px-3 py-2 text-terminal-text focus:outline-none focus:border-terminal-orange resize-none"
              rows={3}
              placeholder="Brief description of this profile..."
              disabled={isSubmitting}
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
              {isSubmitting ? '[Saving...]' : profile ? '[Update]' : '[Create]'}
            </TerminalButton>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProfileModal;

