import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Eye, Download, LogOut, Github, Share2, CheckCircle, ExternalLink, Copy, User, Sparkles } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import ProjectCard from './ProjectCard';
import ProfileTabs from './ProfileTabs';
import ProfileModal from './ProfileModal';
import PublishProfileModal from './PublishProfileModal';
import UnpublishProfileModal from './UnpublishProfileModal';
import ManageProfilesModal from './ManageProfilesModal';
import ProjectModal from './ProjectModal';
import UpgradeModal from './UpgradeModal';
import { useAuth } from '../hooks/useAuth';
import { useDashboard } from '../hooks/useDashboard';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, signOut } = useAuth();
  const {github, publish, profiles, projects, upgrade} = useDashboard();

  const handleSignOut = async () => {
    if (confirm('Are you sure you want to sign out?')) {
      try {
        await signOut();
        // User will be automatically redirected by auth state change
      } catch (error) {
        alert('Error signing out: ' + error.message);
      }
    }
  };

  return (
    <div className="p-10 max-w-[1200px] mx-auto">
      <div className="mb-10">
        <div className="flex justify-between items-start">
          <div>
            <div className="text-2xl mb-2.5 flex items-center gap-3">
              <span>&gt; {user.username}@dev-impact:~$</span>
              {publish.isPublished && (
                <span className="flex items-center gap-2 text-sm">
                  <span className="relative flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                  </span>
                  <span className="text-green-400">Published</span>
                </span>
              )}
            </div>
            {user.github?.username ? (
              <div className="flex items-center gap-3 text-terminal-orange">
                <span>Connected to GitHub:</span>
                {user.github.avatar_url && (
                  <img
                    src={user.github.avatar_url}
                    alt={user.github.username}
                    className="w-6 h-6 rounded-full"
                  />
                )}
                <span>@{user.github.username}</span>
              </div>
            ) : (
              <div>
                {github.state === 'initial' && (
                  <TerminalButton onClick={github.handleConnect}>
                    <Github size={16} className="inline mr-2" />
                    [Connect GitHub]
                  </TerminalButton>
                )}

                {github.state === 'loading' && (
                  <div className="text-terminal-orange text-sm">
                    &gt; Initiating GitHub authentication...
                  </div>
                )}

                {github.state === 'awaiting' && github.deviceCode && (
                  <div className="space-y-3 bg-terminal-bg-lighter border border-terminal-orange/30 p-4 rounded">
                    <div className="text-terminal-orange text-sm">
                      &gt; Authorize this device:
                    </div>
                    <div>
                      <span className="text-terminal-gray text-sm">Code: </span>
                      <span className="text-terminal-orange font-bold text-lg tracking-wider">
                        {github.deviceCode.userCode}
                      </span>
                    </div>
                    <div>
                      <span className="text-terminal-gray text-sm">Visit: </span>
                      <a
                        href={github.deviceCode.verificationUri}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-terminal-orange underline hover:text-terminal-orange-light text-sm"
                      >
                        {github.deviceCode.verificationUri}
                      </a>
                    </div>
                    <div className="text-terminal-gray text-xs">
                      Waiting for authorization...
                    </div>
                    <TerminalButton onClick={github.handleCancel}>
                      [Cancel]
                    </TerminalButton>
                  </div>
                )}

                {github.state === 'success' && (
                  <div className="text-terminal-green text-sm">
                    ✓ Successfully connected to GitHub! Refresh to see changes.
                  </div>
                )}

                {github.state === 'error' && (
                  <div className="space-y-3">
                    <div className="text-red-400 text-sm">
                      ✗ Error: {github.error}
                    </div>
                    <div className="flex gap-3">
                      <TerminalButton onClick={github.handleConnect}>
                        [Retry]
                      </TerminalButton>
                      <TerminalButton onClick={github.handleCancel}>
                        [Cancel]
                      </TerminalButton>
                    </div>
                  </div>
                )}
              </div>
            )}

          </div>
          <div className="flex items-center gap-3">
            {/* Upgrade Button - Only show if not on Pro plan */}
            {/* Feature Badge or Upgrade Button */}
            {profiles.subscriptionInfo === null ? (
              <div className="h-9 w-32 bg-terminal-bg-lighter animate-pulse rounded border border-terminal-border/30"></div>
            ) : profiles.subscriptionInfo.subscription_type === 'pro' ? (
              <div className="px-3 py-1.5 rounded border border-terminal-orange/50 bg-terminal-orange/10 text-terminal-orange flex items-center gap-2">
                <Sparkles size={16} />
                <span className="font-semibold text-sm">PRO</span>
              </div>
            ) : (
              <TerminalButton
                onClick={() => upgrade.setIsModalOpen(true)}
                className="text-terminal-orange border-terminal-orange hover:bg-terminal-orange/10"
              >
                <Sparkles size={16} className="inline mr-2" />
                {import.meta.env.VITE_ENABLE_PAYMENTS === 'true' ? "[Upgrade to Pro]" : "[Join Waitlist]"}
              </TerminalButton>
            )}

            <TerminalButton onClick={handleSignOut}>
              <LogOut size={16} className="inline mr-2" />
              [Sign Out]
            </TerminalButton>
          </div>
        </div>
      </div>

      <div className="mb-10">
        <div className="text-lg mb-5">
          &gt; Actions
        </div>
        <div className="flex gap-5 flex-wrap">
          <TerminalButton onClick={() => navigate('/project/new')}>
            <Plus size={16} className="inline mr-2" />
            [Add Project]
          </TerminalButton>
          <TerminalButton onClick={() => navigate('/profile')}>
            <Eye size={16} className="inline mr-2" />
            [Preview Profile]
          </TerminalButton>

          {/* Show Publish or Unpublish based on current state */}
          {!publish.isPublished ? (
            <TerminalButton
              onClick={publish.openModal}
              disabled={publish.state === 'loading' || profiles.list.length === 0}
            >
              {publish.state === 'loading' ? (
                <>
                  <Share2 size={16} className="inline mr-2 animate-pulse" />
                  [Publishing...]
                </>
              ) : publish.state === 'success' ? (
                <>
                  <CheckCircle size={16} className="inline mr-2" />
                  [Published! ✓]
                </>
              ) : (
                <>
                  <Share2 size={16} className="inline mr-2" />
                  [Publish Profile]
                </>
              )}
            </TerminalButton>
          ) : (
            <TerminalButton
              onClick={publish.openUnpublishModal}
              disabled={publish.state === 'loading' || profiles.list.length === 0}
            >
              <Share2 size={16} className="inline mr-2" />
              [Unpublish]
            </TerminalButton>
          )}

          <TerminalButton onClick={() => navigate('/export')}>
            <Download size={16} className="inline mr-2" />
            [Export]
          </TerminalButton>
          <TerminalButton onClick={() => navigate('/account')}>
            <User size={16} className="inline mr-2" />
            [Account]
          </TerminalButton>
        </div>

        {/* Published profile link (always visible when published) */}
        {publish.isPublished && publish.url && (
          <div className="mt-5 bg-terminal-green/10 border border-terminal-green/30 p-4 rounded">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="text-terminal-green text-sm mb-2 flex items-center gap-2">
                  <CheckCircle size={16} />
                  <span>Your profile is live!</span>
                </div>
                <div className="text-terminal-gray text-sm flex items-center gap-2 flex-wrap">
                  <span className="text-terminal-orange">Link:</span>
                  <a
                    href={publish.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-terminal-orange underline hover:text-terminal-orange-light flex items-center gap-1"
                  >
                    {publish.url}
                    <ExternalLink size={12} />
                  </a>
                </div>
              </div>
              <button
                onClick={publish.handleCopyLink}
                className="px-3 py-1.5 bg-terminal-orange/20 hover:bg-terminal-orange/30 border border-terminal-orange/50 rounded text-sm flex items-center gap-2 transition-colors"
              >
                <Copy size={14} />
                {publish.showCopied ? 'Copied!' : 'Copy'}
              </button>
            </div>
          </div>
        )}

        {/* Publish success message (temporary) */}
        {publish.state === 'success' && (
          <div className="mt-5 bg-terminal-green/10 border border-terminal-green/30 p-4 rounded">
            <div className="text-terminal-green text-sm">
              ✓ Profile published successfully! Link copied to clipboard.
            </div>
          </div>
        )}

        {/* Publish error message */}
        {publish.state === 'error' && publish.error && (
          <div className="mt-5 bg-red-500/10 border border-red-500/30 p-4 rounded">
            <div className="text-red-400 text-sm">
              ✗ Error: {publish.error}
            </div>
          </div>
        )}
      </div>

      <div>
        <div className="text-lg mb-5">
          &gt; Your Projects ({projects.filtered.length})
        </div>

        {/* Profile Tabs */}
        <ProfileTabs
          profiles={profiles.list}
          selectedProfileId={profiles.selectedId}
          onSelectProfile={profiles.setSelectedId}
          onAddProfile={() => profiles.openProfileModal()}
          onManageProfiles={profiles.openManageModal}
          publishedProfileSlugs={publish.publishedProfileSlugs}
          canAddProfile={profiles.subscriptionInfo?.can_add_profile ?? true}
          onUpgradeClick={() => upgrade.setIsModalOpen(true)}
        />

        {projects.filtered.length === 0 ? (
          <div className="text-terminal-orange mb-5">
            {profiles.selectedId
              ? 'No projects in this profile yet. Add a project to get started!'
              : profiles.list.length === 0
                ? 'No profiles yet. Create a profile and add your first project!'
                : 'No unassigned projects. Select a profile to see its projects or add a new project.'
            }
          </div>
        ) : (
          <>
            {projects.filtered.some(p => {
              const pid = p.profile_id;
              return !pid || pid === null || pid === undefined || pid === '';
            }) && profiles.selectedId && (
                <div className="mb-5 text-terminal-orange text-sm border border-terminal-orange/30 bg-terminal-orange/10 p-3 rounded">
                  <div className="flex items-center gap-2">
                    <span>⚠️</span>
                    <span>Some projects are unassigned. Edit them to assign to this profile.</span>
                  </div>
                </div>
              )}
            <div className="bg-terminal-bg-lighter border border-terminal-border p-5">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-start auto-rows-fr">
                {projects.filtered.map(project => (
                  <div key={project.id} className="min-w-0 h-full">
                    <ProjectCard
                      project={project}
                      onEdit={(p) => navigate(`/project/${p.id}/edit`)}
                      onDelete={projects.handleDelete}
                      onClick={(p) => {
                        projects.setSelected(p);
                        projects.openModal(true);
                      }}
                      compact
                    />
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>

      {/* Profile Modal */}
      <ProfileModal
        isOpen={profiles.isProfileModalOpen}
        onClose={profiles.closeProfileModal}
        onSubmit={profiles.editing ? profiles.handleUpdate : profiles.handleCreate}
        profile={profiles.editing}
      />

      {/* Publish Profile Modal */}
      <PublishProfileModal
        isOpen={publish.isModalOpen}
        onClose={publish.closeModal}
        profiles={profiles.list}
        onPublish={publish.handlePublish}
        publishedProfileSlugs={publish.publishedProfileSlugs}
      />

      {/* Unpublish Profile Modal */}
      <UnpublishProfileModal
        isOpen={publish.isUnpublishModalOpen}
        onClose={publish.closeUnpublishModal}
        profiles={profiles.list}
        onUnpublish={publish.handleUnpublish}
        publishedProfileSlugs={publish.publishedProfileSlugs}
      />

      {/* Project Modal */}
      <ProjectModal
        isOpen={projects.isModalOpen}
        onClose={() => {
          projects.openModal(false);
          projects.setSelected(null);
        }}
        project={projects.selected}
        onEdit={(p) => navigate(`/project/${p.id}/edit`)}
        onDelete={projects.handleDelete}
        subscriptionInfo={profiles.subscriptionInfo}
      />

      {/* Manage Profiles Modal */}
      <ManageProfilesModal
        isOpen={profiles.isManageModalOpen}
        onClose={profiles.closeManageModal}
        profiles={profiles.list}
        onDeleteProfile={profiles.handleDelete}
        onEditProfile={profiles.openProfileModal}
        publishedProfileSlugs={publish.publishedProfileSlugs}
        projects={projects.list}
      />

      {/* Upgrade Modal */}
      <UpgradeModal
        isOpen={upgrade.isModalOpen}
        onClose={() => upgrade.setIsModalOpen(false)}
        isLimitReached={!profiles.subscriptionInfo?.can_add_profile && profiles.subscriptionInfo?.subscription_type !== 'pro'}
      />

    </div>
  );
};

export default Dashboard;
