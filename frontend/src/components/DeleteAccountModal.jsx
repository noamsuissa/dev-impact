import React, { useState } from 'react';
import { X, AlertTriangle, Trash2 } from 'lucide-react';
import TerminalButton from './common/TerminalButton';

const DeleteAccountModal = ({ onConfirm, onCancel, isDeleting }) => {
  const [confirmText, setConfirmText] = useState('');
  const isConfirmed = confirmText === 'DELETE';

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-terminal-bg border-2 border-red-500/50 rounded-lg max-w-md w-full p-6 relative">
        <button
          onClick={onCancel}
          disabled={isDeleting}
          className="absolute top-4 right-4 text-terminal-gray hover:text-terminal-text transition-colors"
        >
          <X size={20} />
        </button>

        <div className="mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center">
              <AlertTriangle size={24} className="text-red-400" />
            </div>
            <h2 className="text-xl text-terminal-orange font-bold">
              Delete Account
            </h2>
          </div>

          <p className="text-terminal-text mb-4">
            Are you absolutely sure you want to delete your account? This action cannot be undone.
          </p>

          <div className="bg-red-500/10 border border-red-500/30 p-4 rounded mb-4">
            <p className="text-red-400 text-sm">
              This will permanently delete:
            </p>
            <ul className="list-disc list-inside text-terminal-gray text-sm mt-2 space-y-1">
              <li>Your profile and all profile data</li>
              <li>All your projects and achievements</li>
              <li>Your authentication account</li>
            </ul>
          </div>

          <div className="mb-4">
            <p className="text-terminal-gray text-sm mb-2">
              Type <span className="text-terminal-orange font-mono font-bold">DELETE</span> to confirm:
            </p>
            <input
              type="text"
              value={confirmText}
              onChange={(e) => setConfirmText(e.target.value)}
              disabled={isDeleting}
              placeholder="Type DELETE here"
              className="w-full bg-terminal-bg-lighter border border-terminal-border text-terminal-text px-3 py-2 rounded focus:outline-none focus:border-terminal-orange focus:ring-1 focus:ring-terminal-orange disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>
        </div>

        <div className="flex gap-3 justify-end">
          <TerminalButton
            onClick={onCancel}
            disabled={isDeleting}
            className="bg-terminal-bg-lighter hover:bg-terminal-bg-lighter/80"
          >
            [Cancel]
          </TerminalButton>
          <TerminalButton
            onClick={onConfirm}
            disabled={isDeleting || !isConfirmed}
            className={`${
              isConfirmed && !isDeleting
                ? 'bg-red-500/20 hover:bg-red-500/30 border-red-500/50 text-red-400'
                : 'bg-terminal-bg-lighter border-terminal-border text-terminal-gray cursor-not-allowed'
            }`}
          >
            {isDeleting ? (
              <>
                <Trash2 size={16} className="inline mr-2 animate-pulse" />
                [Deleting...]
              </>
            ) : (
              <>
                <Trash2 size={16} className="inline mr-2" />
                [Delete Account]
              </>
            )}
          </TerminalButton>
        </div>
      </div>
    </div>
  );
};

export default DeleteAccountModal;
