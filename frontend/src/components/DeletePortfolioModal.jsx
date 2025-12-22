import React, { useState } from 'react';
import { X, AlertTriangle } from 'lucide-react';
import TerminalButton from './common/TerminalButton';

const DeletePortfolioModal = ({ isOpen, onClose, portfolio, onDelete, projectCount = 0 }) => {
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState(null);
  const [confirmText, setConfirmText] = useState('');

  React.useEffect(() => {
    if (isOpen) {
      setConfirmText('');
      setError(null);
      setIsDeleting(false);
    }
  }, [isOpen]);

  const handleDelete = async () => {
    if (confirmText !== 'DELETE') {
      setError('Please type DELETE to confirm');
      return;
    }

    setIsDeleting(true);
    setError(null);

    try {
      await onDelete(portfolio.id);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to delete portfolio');
    } finally {
      setIsDeleting(false);
    }
  };

  if (!isOpen || !portfolio) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-terminal-bg border border-red-500/50 p-6 max-w-md w-full">
        <div className="flex items-center justify-between mb-6">
          <div className="text-lg text-red-400 flex items-center gap-2">
            <AlertTriangle size={20} />
            Delete Portfolio
          </div>
          <button
            onClick={onClose}
            className="text-terminal-gray hover:text-terminal-orange transition-colors"
            disabled={isDeleting}
          >
            <X size={20} />
          </button>
        </div>

        <div className="space-y-4">
          <div className="bg-red-500/10 border border-red-500/30 p-4 rounded">
            <div className="text-red-400 text-sm font-semibold mb-2">
              Warning: This action cannot be undone!
            </div>
            <div className="text-terminal-gray text-sm space-y-1">
              <p>You are about to delete the portfolio <span className="text-terminal-orange font-semibold">"{portfolio.name}"</span>.</p>
              {projectCount > 0 ? (
                <p className="text-red-400">
                  <strong>{projectCount} project{projectCount !== 1 ? 's' : ''}</strong> assigned to this portfolio will also be permanently deleted.
                </p>
              ) : (
                <p>This portfolio has no assigned projects.</p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm text-terminal-gray mb-2">
              Type <span className="text-red-400 font-mono">DELETE</span> to confirm:
            </label>
            <input
              type="text"
              value={confirmText}
              onChange={(e) => setConfirmText(e.target.value)}
              className="w-full bg-terminal-bg-lighter border border-terminal-border px-3 py-2 text-terminal-text focus:outline-none focus:border-red-500"
              placeholder="DELETE"
              disabled={isDeleting}
              autoFocus
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
              disabled={isDeleting}
            >
              [Cancel]
            </TerminalButton>
            <TerminalButton
              type="button"
              onClick={handleDelete}
              disabled={isDeleting || confirmText !== 'DELETE'}
              className="bg-red-500/20 border-red-500/50 text-red-400 hover:bg-red-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isDeleting ? '[Deleting...]' : '[Delete Portfolio]'}
            </TerminalButton>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DeletePortfolioModal;

