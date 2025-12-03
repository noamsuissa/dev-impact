import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Github, ArrowLeft, Trash2, User } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import DeleteAccountModal from './DeleteAccountModal';
import { user as userClient } from '../utils/client';
import { useAuth } from '../hooks/useAuth';

const AccountPage = ({ user, projects }) => {
  const navigate = useNavigate();
  const { signOut } = useAuth();
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteAccount = async () => {
    setIsDeleting(true);
    try {
      await userClient.deleteAccount();
      // Sign out and redirect to home
      await signOut();
      navigate('/');
    } catch (error) {
      console.error('Failed to delete account:', error);
      alert('Failed to delete account: ' + error.message);
      setIsDeleting(false);
    }
  };

  return (
    <div className="p-10 max-w-[1200px] mx-auto">
      <div className="mb-10 flex items-center gap-5">
        <Link to="/dashboard">
          <TerminalButton>
            <ArrowLeft size={16} className="inline mr-2" />
            [Back to Dashboard]
          </TerminalButton>
        </Link>
      </div>

      <div className="border border-terminal-border p-10 mb-10">
        <div className="flex items-start gap-6 mb-6">
          {user.github?.avatar_url ? (
            <img
              src={user.github.avatar_url}
              alt={user.name}
              className="w-24 h-24 rounded-full border-2 border-terminal-orange"
            />
          ) : (
            <div className="w-24 h-24 rounded-full border-2 border-terminal-orange flex items-center justify-center bg-terminal-bg-lighter">
              <User size={40} className="text-terminal-orange" />
            </div>
          )}
          <div className="flex-1">
            <div className="text-[32px] mb-2.5 uppercase text-terminal-orange">
              {user.name || 'User'}
            </div>
            <div className="text-lg text-[#c9c5c0] mb-5">
              Account Settings
            </div>
            {user.github?.username && (
              <div className="mb-2.5 flex items-center gap-2">
                <Github size={16} />
                <span className="text-terminal-gray">github.com/{user.github.username}</span>
              </div>
            )}
          </div>
        </div>

        <div className="border-t border-terminal-border pt-5 mt-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-[#c9c5c0]">
            <div>
              <div className="text-terminal-gray text-sm mb-1">Username</div>
              <div className="text-terminal-orange">{user.username || 'N/A'}</div>
            </div>
            <div>
              <div className="text-terminal-gray text-sm mb-1">Full Name</div>
              <div className="text-terminal-orange">{user.name || 'N/A'}</div>
            </div>
            <div>
              <div className="text-terminal-gray text-sm mb-1">Projects</div>
              <div className="text-terminal-orange">{projects.length} {projects.length === 1 ? 'Project' : 'Projects'}</div>
            </div>
            <div>
              <div className="text-terminal-gray text-sm mb-1">Total Achievements</div>
              <div className="text-terminal-orange">{projects.reduce((sum, p) => sum + p.metrics.length, 0)} Achievements</div>
            </div>
          </div>
        </div>
      </div>

      <div className="border border-red-500/30 bg-red-500/10 p-6 rounded">
        <div className="mb-4">
          <h3 className="text-lg text-red-400 mb-2 flex items-center gap-2">
            <Trash2 size={20} />
            Danger Zone
          </h3>
          <p className="text-terminal-gray text-sm">
            Once you delete your account, there is no going back. This will permanently delete your profile, projects, and all associated data.
          </p>
        </div>
        <TerminalButton
          onClick={() => setShowDeleteModal(true)}
          disabled={isDeleting}
          className="bg-red-500/20 hover:bg-red-500/30 border-red-500/50 text-red-400"
        >
          <Trash2 size={16} className="inline mr-2" />
          {isDeleting ? '[Deleting...]' : '[Delete Account]'}
        </TerminalButton>
      </div>

      {showDeleteModal && (
        <DeleteAccountModal
          onConfirm={handleDeleteAccount}
          onCancel={() => {
            setShowDeleteModal(false);
            setIsDeleting(false);
          }}
          isDeleting={isDeleting}
        />
      )}
    </div>
  );
};

export default AccountPage;

