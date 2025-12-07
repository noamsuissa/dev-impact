import React, { useState } from 'react';
import { X, Trash2 } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import DeleteProfileModal from './DeleteProfileModal';

const ManageProfilesModal = ({ 
  isOpen, 
  onClose, 
  profiles = [], 
  onDeleteProfile, 
  onEditProfile,
  publishedProfileSlugs = [],
  projects = []
}) => {
  const [deletingProfile, setDeletingProfile] = useState(null);

  React.useEffect(() => {
    if (isOpen) {
      setDeletingProfile(null);
    }
  }, [isOpen]);

  const handleDeleteClick = (profile) => {
    setDeletingProfile(profile);
  };

  const handleDeleteConfirm = async (profileId) => {
    await onDeleteProfile(profileId);
    setDeletingProfile(null);
  };

  const handleCloseDeleteModal = () => {
    setDeletingProfile(null);
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div className="bg-terminal-bg border border-terminal-border p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <div className="text-lg text-terminal-orange">
              Manage Profiles
            </div>
            <button
              onClick={onClose}
              className="text-terminal-gray hover:text-terminal-orange transition-colors"
            >
              <X size={20} />
            </button>
          </div>

          <div className="space-y-3">
            {profiles.length === 0 ? (
              <div className="text-terminal-gray text-sm text-center py-8">
                No profiles yet. Create one to get started!
              </div>
            ) : (
              profiles.map((profile) => {
                const isPublished = publishedProfileSlugs.includes(profile.slug);
                const projectCount = projects.filter(p => p.profile_id === profile.id).length;

                return (
                  <div
                    key={profile.id}
                    className="bg-terminal-bg-lighter border border-terminal-border p-4 rounded flex items-center justify-between hover:border-terminal-orange/50 transition-colors"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-terminal-orange font-semibold">
                          {profile.name}
                        </span>
                        {isPublished && (
                          <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                          </span>
                        )}
                      </div>
                      {profile.description && (
                        <div className="text-terminal-gray text-sm mb-2">
                          {profile.description}
                        </div>
                      )}
                      <div className="text-terminal-gray text-xs">
                        {projectCount} project{projectCount !== 1 ? 's' : ''} assigned
                        {isPublished && ' • Published'}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      {onEditProfile && (
                        <button
                          onClick={() => {
                            onEditProfile(profile);
                            onClose();
                          }}
                          className="px-3 py-1.5 bg-terminal-bg border border-terminal-border hover:border-terminal-orange text-terminal-orange text-sm transition-colors"
                          title="Edit profile"
                        >
                          Edit
                        </button>
                      )}
                      <button
                        onClick={() => handleDeleteClick(profile)}
                        className="px-3 py-1.5 bg-red-500/20 border border-red-500/50 hover:bg-red-500/30 text-red-400 transition-colors flex items-center gap-2"
                        title="Delete profile"
                      >
                        <Trash2 size={14} />
                        Delete
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          <div className="flex justify-end pt-6 mt-6 border-t border-terminal-border">
            <TerminalButton onClick={onClose}>
              [Close]
            </TerminalButton>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {deletingProfile && (
        <DeleteProfileModal
          isOpen={!!deletingProfile}
          onClose={handleCloseDeleteModal}
          profile={deletingProfile}
          onDelete={handleDeleteConfirm}
          projectCount={projects.filter(p => p.profile_id === deletingProfile.id).length}
        />
      )}
    </>
  );
};

export default ManageProfilesModal;

