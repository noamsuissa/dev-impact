import React, { useState, useEffect, useMemo } from 'react';
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
import { completeGitHubAuth } from '../utils/githubAuth';
import { profiles, userProfiles, subscriptions } from '../utils/client';
import { generateProfileUrl } from '../utils/helpers';

const Dashboard = ({ user, projects, onDeleteProject, onGitHubConnect, onProfileDeleted }) => {
  const navigate = useNavigate();
  const { signOut } = useAuth();
  const [githubState, setGithubState] = useState('initial'); // initial, loading, awaiting, success, error
  const [deviceCode, setDeviceCode] = useState(null);
  const [error, setError] = useState(null);
  const [publishState, setPublishState] = useState('initial'); // initial, loading, success, error
  const [publishedUrl, setPublishedUrl] = useState(null);
  const [isPublished, setIsPublished] = useState(false);
  const [showCopied, setShowCopied] = useState(false);

  // Profile state
  const [userProfilesList, setUserProfilesList] = useState([]);
  const [selectedProfileId, setSelectedProfileId] = useState(null);
  const [publishedProfileSlugs, setPublishedProfileSlugs] = useState([]);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [isPublishModalOpen, setIsPublishModalOpen] = useState(false);
  const [isUnpublishModalOpen, setIsUnpublishModalOpen] = useState(false);
  const [isManageProfilesModalOpen, setIsManageProfilesModalOpen] = useState(false);
  const [editingProfile, setEditingProfile] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [isProjectModalOpen, setIsProjectModalOpen] = useState(false);
  const [subscriptionInfo, setSubscriptionInfo] = useState(null);
  const [isUpgradeModalOpen, setIsUpgradeModalOpen] = useState(false);
  const [isRedirectingToCheckout, setIsRedirectingToCheckout] = useState(false);

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

  const handleConnectGitHub = async () => {
    setGithubState('loading');
    setError(null);

    try {
      const result = await completeGitHubAuth(
        ({ userCode, verificationUri }) => {
          setDeviceCode({ userCode, verificationUri });
          setGithubState('awaiting');
        },
        () => {
          // Progress callback - no logging needed in production
        }
      );

      setGithubState('success');

      // Update user profile with GitHub data
      if (onGitHubConnect) {
        onGitHubConnect(result);
      }
    } catch (err) {
      console.error('GitHub OAuth error:', err);
      setError(err.message);
      setGithubState('error');
    }
  };

  const handleCancelGitHub = () => {
    setGithubState('initial');
    setDeviceCode(null);
    setError(null);
  };

  // Load user profiles and subscription info on mount
  useEffect(() => {
    const loadProfiles = async () => {
      if (!user) return;

      try {
        const profilesList = await userProfiles.list();
        setUserProfilesList(profilesList);

        // Load subscription info
        try {
          const subInfo = await subscriptions.getSubscriptionInfo();
          setSubscriptionInfo(subInfo);
        } catch (err) {
          console.error('Failed to load subscription info:', err);
          // Default to free tier if fetch fails
          setSubscriptionInfo({
            subscription_type: 'free',
            profile_count: profilesList.length,
            max_profiles: 3,
            can_add_profile: profilesList.length < 3
          });
        }

        // Select first profile if available and none is currently selected
        setSelectedProfileId(prev => {
          if (profilesList.length > 0 && !prev) {
            return profilesList[0].id;
          }
          return prev;
        });
      } catch (err) {
        console.error('Failed to load profiles:', err);
        setUserProfilesList([]);
      }
    };

    loadProfiles();
  }, [user]);

  // Check for plan=pro query parameter or pending subscription in localStorage
  // For new/pending users, redirect DIRECTLY to checkout
  useEffect(() => {
    const initCheckoutRedirect = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const planParam = urlParams.get('plan');
      const pendingSub = localStorage.getItem('pendingSubscription');

      if ((planParam === 'pro' || pendingSub === 'pro') && user) {
        setIsRedirectingToCheckout(true);

        try {
          // Create checkout session directly
          const baseUrl = window.location.origin;
          const successUrl = `${baseUrl}/subscription/success`;
          const cancelUrl = `${baseUrl}/subscription/cancel`;

          const { checkout_url } = await subscriptions.createCheckoutSession(successUrl, cancelUrl);

          // Clean up flags only after successful creation (to avoid loops on failure, 
          // though we redirect away anyway)
          if (planParam) {
            const newUrl = window.location.pathname;
            window.history.replaceState({}, '', newUrl);
          }
          if (pendingSub) {
            localStorage.removeItem('pendingSubscription');
          }

          // Go to Stripe
          window.location.href = checkout_url;

        } catch (err) {
          console.error('Direct checkout redirect failed:', err);
          // Fallback to modal on error so user isn't stuck
          if (!subscriptionInfo?.can_add_profile) {
            setIsUpgradeModalOpen(true);
            // Note: UpgradeModal handles its own message logic based on isLimitReached prop we'll pass
            return;
          }
        }
      }
    };

    initCheckoutRedirect();
  }, [user]);

  // Filter projects by selected profile (using useMemo for derived state)
  const filteredProjects = useMemo(() => {
    if (!selectedProfileId) {
      // If no profile selected, show projects without a profile_id (unassigned)
      return projects.filter(p => {
        const pid = p.profile_id;
        return !pid || pid === null || pid === undefined || pid === '';
      });
    }

    // Filter projects that belong ONLY to the selected profile
    // Also include unassigned projects (null/undefined) so user can assign them
    const filtered = projects.filter(p => {
      const pid = p.profile_id;
      // Show if: unassigned (null/undefined/empty) OR exactly matches selected profile
      const isUnassigned = !pid || pid === null || pid === undefined || pid === '';
      const matchesProfile = pid === selectedProfileId;
      return isUnassigned || matchesProfile;
    });

    return filtered;
  }, [projects, selectedProfileId]);

  // Check published status for all profiles
  useEffect(() => {
    const checkPublishedStatus = async () => {
      if (!user || userProfilesList.length === 0) return;

      const username = user.username;
      const publishedSlugs = [];

      // Check each profile's published status
      for (const profile of userProfilesList) {
        try {
          const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
          const response = await fetch(`${apiUrl}/api/profiles/${username}/${profile.slug}`);

          if (response.ok) {
            publishedSlugs.push(profile.slug);
          }
        } catch {
          // Profile not published, that's okay
        }
      }

      setPublishedProfileSlugs(publishedSlugs);

      // Update published state for selected profile
      if (selectedProfileId) {
        const selectedProfile = userProfilesList.find(p => p.id === selectedProfileId);
        if (selectedProfile && publishedSlugs.includes(selectedProfile.slug)) {
          setIsPublished(true);
          const shareUrl = generateProfileUrl(username, selectedProfile.slug);
          setPublishedUrl(shareUrl);
        } else {
          setIsPublished(false);
          setPublishedUrl(null);
        }
      }
    };

    checkPublishedStatus();
  }, [user, userProfilesList, selectedProfileId]);

  // Save selected profile to localStorage
  useEffect(() => {
    if (selectedProfileId && typeof window !== 'undefined') {
      localStorage.setItem('selectedProfileId', selectedProfileId);
    }
  }, [selectedProfileId]);

  if (isRedirectingToCheckout) {
    return (
      <div className="min-h-screen bg-[#2d2d2d] flex items-center justify-center">
        <div className="fade-in text-center p-8 border border-terminal-orange bg-terminal-bg rounded-lg max-w-md">
          <div className="text-3xl mb-4 animate-pulse">
            &gt; _
          </div>
          <div className="text-xl text-terminal-orange mb-3">&gt; Initializing Payment Protocol...</div>
          <div className="text-terminal-gray text-sm">Redirecting you to our secure checkout service via Stripe.</div>
        </div>
      </div>
    );
  }

  const handleCopyLink = async () => {
    if (!publishedUrl) return;

    try {
      await navigator.clipboard.writeText(publishedUrl);
      setShowCopied(true);
      setTimeout(() => setShowCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handlePublishProfile = async (profileIdToPublish) => {
    const profileToPublish = userProfilesList.find(p => p.id === profileIdToPublish);
    if (!profileToPublish) {
      throw new Error('Profile not found.');
    }

    // Check if profile has projects - filter by exact profile_id match (exclude null/undefined)
    const profileProjects = projects.filter(p => {
      const pid = p.profile_id;
      return pid && pid === profileIdToPublish;
    });

    if (profileProjects.length === 0) {
      throw new Error('Please add at least one project to this profile before publishing. Edit your projects to assign them to this profile.');
    }

    setPublishState('loading');
    setError(null);

    try {
      const username = user.username;

      // Publish via API with profile_id
      const response = await profiles.publish({
        username,
        profile_id: profileIdToPublish
      });

      // Use URL from backend response
      const shareUrl = generateProfileUrl(username, response.profile_slug);
      setPublishedUrl(shareUrl);

      // Mark as published
      setIsPublished(true);
      setPublishedProfileSlugs([...publishedProfileSlugs, profileToPublish.slug]);

      // If this is the selected profile, update the published URL
      if (profileIdToPublish === selectedProfileId) {
        setPublishedUrl(shareUrl);
      }

      try {
        await navigator.clipboard.writeText(shareUrl);
        setPublishState('success');

        // Reset success state after 5 seconds
        setTimeout(() => {
          setPublishState('initial');
        }, 5000);
      } catch (clipboardError) {
        console.error('Failed to copy to clipboard:', clipboardError);
        setPublishState('success');
      }
    } catch (err) {
      console.error('Error publishing profile:', err);
      setError(err.message);
      setPublishState('error');
      throw err; // Re-throw so modal can handle it
    }
  };

  const handleOpenPublishModal = () => {
    setIsPublishModalOpen(true);
  };

  const handleClosePublishModal = () => {
    setIsPublishModalOpen(false);
    setError(null);
  };

  const handleUnpublishProfile = async (profileIdToUnpublish) => {
    const profileToUnpublish = userProfilesList.find(p => p.id === profileIdToUnpublish);
    if (!profileToUnpublish) {
      throw new Error('Profile not found.');
    }

    setPublishState('loading');
    setError(null);

    try {
      const username = user.username;

      // Unpublish via API
      await profiles.unpublish(username, profileToUnpublish.slug);

      // Mark as unpublished
      setPublishedProfileSlugs(publishedProfileSlugs.filter(s => s !== profileToUnpublish.slug));

      // If this is the selected profile, update the published state
      if (profileIdToUnpublish === selectedProfileId) {
        setIsPublished(false);
        setPublishedUrl(null);
      }

      setPublishState('initial');
    } catch (err) {
      console.error('Error unpublishing profile:', err);
      setError(err.message);
      setPublishState('error');
      throw err; // Re-throw so modal can handle it
    }
  };

  const handleOpenUnpublishModal = () => {
    setIsUnpublishModalOpen(true);
  };

  const handleCloseUnpublishModal = () => {
    setIsUnpublishModalOpen(false);
    setError(null);
  };

  const handleCreateProfile = async (profileData) => {
    const newProfile = await userProfiles.create(profileData);
    setUserProfilesList([...userProfilesList, newProfile]);

    // Select the newly created profile
    setSelectedProfileId(newProfile.id);

    // Refresh subscription info
    try {
      const subInfo = await subscriptions.getSubscriptionInfo();
      setSubscriptionInfo(subInfo);
    } catch (err) {
      console.error('Failed to refresh subscription info:', err);
    }
  };

  const handleUpdateProfile = async (profileData) => {
    if (!editingProfile) return;

    const updatedProfile = await userProfiles.update(editingProfile.id, profileData);
    setUserProfilesList(userProfilesList.map(p =>
      p.id === updatedProfile.id ? updatedProfile : p
    ));
    setEditingProfile(null);
  };

  const handleDeleteProfile = async (profileId) => {
    const profileToDelete = userProfilesList.find(p => p.id === profileId);
    if (!profileToDelete) {
      throw new Error('Profile not found.');
    }

    // Delete profile (backend will delete all assigned projects)
    await userProfiles.delete(profileId);

    // Remove profile from list
    setUserProfilesList(userProfilesList.filter(p => p.id !== profileId));

    // Note: Projects are already deleted by the backend.
    // The parent component should refetch projects or filter them from its state.
    // For now, the filteredProjects will automatically update via the useEffect
    // that filters projects by selectedProfileId.

    // Select first remaining profile or null
    const remaining = userProfilesList.filter(p => p.id !== profileId);
    setSelectedProfileId(remaining.length > 0 ? remaining[0].id : null);

    // Notify parent to update projects state (filter out deleted projects)
    if (onProfileDeleted) {
      onProfileDeleted(profileId);
    }

    // Refresh subscription info
    try {
      const subInfo = await subscriptions.getSubscriptionInfo();
      setSubscriptionInfo(subInfo);
    } catch (err) {
      console.error('Failed to refresh subscription info:', err);
    }
  };

  const handleOpenManageProfilesModal = () => {
    setIsManageProfilesModalOpen(true);
  };

  const handleCloseManageProfilesModal = () => {
    setIsManageProfilesModalOpen(false);
  };

  const handleOpenProfileModal = (profile = null) => {
    setEditingProfile(profile);
    setIsProfileModalOpen(true);
  };

  const handleCloseProfileModal = () => {
    setIsProfileModalOpen(false);
    setEditingProfile(null);
  };

  return (
    <div className="p-10 max-w-[1200px] mx-auto">
      <div className="mb-10">
        <div className="flex justify-between items-start">
          <div>
            <div className="text-2xl mb-2.5 flex items-center gap-3">
              <span>&gt; {user.username}@dev-impact:~$</span>
              {isPublished && (
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
                {githubState === 'initial' && (
                  <TerminalButton onClick={handleConnectGitHub}>
                    <Github size={16} className="inline mr-2" />
                    [Connect GitHub]
                  </TerminalButton>
                )}

                {githubState === 'loading' && (
                  <div className="text-terminal-orange text-sm">
                    &gt; Initiating GitHub authentication...
                  </div>
                )}

                {githubState === 'awaiting' && deviceCode && (
                  <div className="space-y-3 bg-terminal-bg-lighter border border-terminal-orange/30 p-4 rounded">
                    <div className="text-terminal-orange text-sm">
                      &gt; Authorize this device:
                    </div>
                    <div>
                      <span className="text-terminal-gray text-sm">Code: </span>
                      <span className="text-terminal-orange font-bold text-lg tracking-wider">
                        {deviceCode.userCode}
                      </span>
                    </div>
                    <div>
                      <span className="text-terminal-gray text-sm">Visit: </span>
                      <a
                        href={deviceCode.verificationUri}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-terminal-orange underline hover:text-terminal-orange-light text-sm"
                      >
                        {deviceCode.verificationUri}
                      </a>
                    </div>
                    <div className="text-terminal-gray text-xs">
                      Waiting for authorization...
                    </div>
                    <TerminalButton onClick={handleCancelGitHub}>
                      [Cancel]
                    </TerminalButton>
                  </div>
                )}

                {githubState === 'success' && (
                  <div className="text-terminal-green text-sm">
                    ✓ Successfully connected to GitHub! Refresh to see changes.
                  </div>
                )}

                {githubState === 'error' && (
                  <div className="space-y-3">
                    <div className="text-red-400 text-sm">
                      ✗ Error: {error}
                    </div>
                    <div className="flex gap-3">
                      <TerminalButton onClick={handleConnectGitHub}>
                        [Retry]
                      </TerminalButton>
                      <TerminalButton onClick={handleCancelGitHub}>
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
            {subscriptionInfo === null ? (
              <div className="h-9 w-32 bg-terminal-bg-lighter animate-pulse rounded border border-terminal-border/30"></div>
            ) : subscriptionInfo.subscription_type === 'pro' ? (
              <div className="px-3 py-1.5 rounded border border-terminal-orange/50 bg-terminal-orange/10 text-terminal-orange flex items-center gap-2">
                <Sparkles size={16} />
                <span className="font-semibold text-sm">PRO</span>
              </div>
            ) : (
              <TerminalButton
                onClick={() => setIsUpgradeModalOpen(true)}
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
          {!isPublished ? (
            <TerminalButton
              onClick={handleOpenPublishModal}
              disabled={publishState === 'loading' || userProfilesList.length === 0}
            >
              {publishState === 'loading' ? (
                <>
                  <Share2 size={16} className="inline mr-2 animate-pulse" />
                  [Publishing...]
                </>
              ) : publishState === 'success' ? (
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
              onClick={handleOpenUnpublishModal}
              disabled={publishState === 'loading' || userProfilesList.length === 0}
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
        {isPublished && publishedUrl && (
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
                    href={publishedUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-terminal-orange underline hover:text-terminal-orange-light flex items-center gap-1"
                  >
                    {publishedUrl}
                    <ExternalLink size={12} />
                  </a>
                </div>
              </div>
              <button
                onClick={handleCopyLink}
                className="px-3 py-1.5 bg-terminal-orange/20 hover:bg-terminal-orange/30 border border-terminal-orange/50 rounded text-sm flex items-center gap-2 transition-colors"
              >
                <Copy size={14} />
                {showCopied ? 'Copied!' : 'Copy'}
              </button>
            </div>
          </div>
        )}

        {/* Publish success message (temporary) */}
        {publishState === 'success' && (
          <div className="mt-5 bg-terminal-green/10 border border-terminal-green/30 p-4 rounded">
            <div className="text-terminal-green text-sm">
              ✓ Profile published successfully! Link copied to clipboard.
            </div>
          </div>
        )}

        {/* Publish error message */}
        {publishState === 'error' && error && (
          <div className="mt-5 bg-red-500/10 border border-red-500/30 p-4 rounded">
            <div className="text-red-400 text-sm">
              ✗ Error: {error}
            </div>
          </div>
        )}
      </div>

      <div>
        <div className="text-lg mb-5">
          &gt; Your Projects ({filteredProjects.length})
        </div>

        {/* Profile Tabs */}
        <ProfileTabs
          profiles={userProfilesList}
          selectedProfileId={selectedProfileId}
          onSelectProfile={setSelectedProfileId}
          onAddProfile={() => handleOpenProfileModal()}
          onManageProfiles={handleOpenManageProfilesModal}
          publishedProfileSlugs={publishedProfileSlugs}
          canAddProfile={subscriptionInfo?.can_add_profile ?? true}
          onUpgradeClick={() => setIsUpgradeModalOpen(true)}
        />

        {filteredProjects.length === 0 ? (
          <div className="text-terminal-orange mb-5">
            {selectedProfileId
              ? 'No projects in this profile yet. Add a project to get started!'
              : userProfilesList.length === 0
                ? 'No profiles yet. Create a profile and add your first project!'
                : 'No unassigned projects. Select a profile to see its projects or add a new project.'
            }
          </div>
        ) : (
          <>
            {filteredProjects.some(p => {
              const pid = p.profile_id;
              return !pid || pid === null || pid === undefined || pid === '';
            }) && selectedProfileId && (
                <div className="mb-5 text-terminal-orange text-sm border border-terminal-orange/30 bg-terminal-orange/10 p-3 rounded">
                  <div className="flex items-center gap-2">
                    <span>⚠️</span>
                    <span>Some projects are unassigned. Edit them to assign to this profile.</span>
                  </div>
                </div>
              )}
            <div className="bg-terminal-bg-lighter border border-terminal-border p-5">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-start auto-rows-fr">
                {filteredProjects.map(project => (
                  <div key={project.id} className="min-w-0 h-full">
                    <ProjectCard
                      project={project}
                      onEdit={(p) => navigate(`/project/${p.id}/edit`)}
                      onDelete={onDeleteProject}
                      onClick={(p) => {
                        setSelectedProject(p);
                        setIsProjectModalOpen(true);
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
        isOpen={isProfileModalOpen}
        onClose={handleCloseProfileModal}
        onSubmit={editingProfile ? handleUpdateProfile : handleCreateProfile}
        profile={editingProfile}
      />

      {/* Publish Profile Modal */}
      <PublishProfileModal
        isOpen={isPublishModalOpen}
        onClose={handleClosePublishModal}
        profiles={userProfilesList}
        onPublish={handlePublishProfile}
        publishedProfileSlugs={publishedProfileSlugs}
      />

      {/* Unpublish Profile Modal */}
      <UnpublishProfileModal
        isOpen={isUnpublishModalOpen}
        onClose={handleCloseUnpublishModal}
        profiles={userProfilesList}
        onUnpublish={handleUnpublishProfile}
        publishedProfileSlugs={publishedProfileSlugs}
      />

      {/* Project Modal */}
      <ProjectModal
        isOpen={isProjectModalOpen}
        onClose={() => {
          setIsProjectModalOpen(false);
          setSelectedProject(null);
        }}
        project={selectedProject}
        onEdit={(p) => navigate(`/project/${p.id}/edit`)}
        onDelete={onDeleteProject}
        subscriptionInfo={subscriptionInfo}
      />

      {/* Manage Profiles Modal */}
      <ManageProfilesModal
        isOpen={isManageProfilesModalOpen}
        onClose={handleCloseManageProfilesModal}
        profiles={userProfilesList}
        onDeleteProfile={handleDeleteProfile}
        onEditProfile={handleOpenProfileModal}
        publishedProfileSlugs={publishedProfileSlugs}
        projects={projects}
      />

      {/* Upgrade Modal */}
      <UpgradeModal
        isOpen={isUpgradeModalOpen}
        onClose={() => setIsUpgradeModalOpen(false)}
        isLimitReached={!subscriptionInfo?.can_add_profile && subscriptionInfo?.subscription_type !== 'pro'}
      />

    </div>
  );
};

export default Dashboard;

