import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Eye, Download, LogOut, Github, Share2, CheckCircle, ExternalLink, Copy } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import ProjectCard from './ProjectCard';
import { useAuth } from '../hooks/useAuth';
import { completeGitHubAuth } from '../utils/githubAuth';
import { profiles } from '../utils/client';

const Dashboard = ({ user, projects, onDeleteProject, onGitHubConnect }) => {
  const navigate = useNavigate();
  const { signOut } = useAuth();
  const [githubState, setGithubState] = useState('initial'); // initial, loading, awaiting, success, error
  const [deviceCode, setDeviceCode] = useState(null);
  const [error, setError] = useState(null);
  const [publishState, setPublishState] = useState('initial'); // initial, loading, success, error
  const [publishedUrl, setPublishedUrl] = useState(null);
  const [isPublished, setIsPublished] = useState(false);
  const [showCopied, setShowCopied] = useState(false);

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
        (message) => {
          console.log('GitHub OAuth progress:', message);
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

  // Check if profile is already published on mount
  useEffect(() => {
    const checkPublishedStatus = async () => {
      if (!user) return;
      
      const username = user.github?.username || 
                      user.name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
      
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/profiles/${username}`);
        
        if (response.ok) {
          const shareUrl = `https://dev-impact.io/${username}`;
          setIsPublished(true);
          setPublishedUrl(shareUrl);
        }
      } catch {
        // Profile not published, that's okay
        console.log('Profile not published yet');
      }
    };

    checkPublishedStatus();
  }, [user]);

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

  const handlePublishProfile = async () => {
    if (projects.length === 0) {
      alert('Please add at least one project before publishing your profile.');
      return;
    }

    setPublishState('loading');
    setError(null);

    try {
      // Generate username from GitHub or name
      const username = user.github?.username || 
                      user.name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');

      // Backend fetches fresh data from database, so we only need to send username
      // Publish via API
      await profiles.publish({ username });
      
      // Copy link to clipboard
      const shareUrl = `https://dev-impact.io/${username}`;
      setPublishedUrl(shareUrl);
      
      // Mark as published
      setIsPublished(true);
      
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
      
      // Reset error state after 5 seconds
      setTimeout(() => {
        setPublishState('initial');
      }, 5000);
    }
  };

  const handleUnpublishProfile = async () => {
    if (!confirm('Are you sure you want to unpublish your profile? It will no longer be accessible to others.')) {
      return;
    }

    setPublishState('loading');
    setError(null);

    try {
      // Generate username from GitHub or name
      const username = user.github?.username || 
                      user.name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');

      // Unpublish via API
      await profiles.unpublish(username);

      // Mark as unpublished
      setIsPublished(false);
      setPublishedUrl(null);
      setPublishState('initial');
      
      // Show success message briefly
      alert('Profile unpublished successfully!');
    } catch (err) {
      console.error('Error unpublishing profile:', err);
      setError(err.message);
      setPublishState('error');
      
      // Reset error state after 5 seconds
      setTimeout(() => {
        setPublishState('initial');
      }, 5000);
    }
  };

  return (
    <div className="p-10 max-w-[1200px] mx-auto">
      <div className="mb-10">
        <div className="flex justify-between items-start">
          <div>
            <div className="text-2xl mb-2.5 flex items-center gap-3">
              <span>&gt; {user.name}@dev-impact:~$</span>
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
          <TerminalButton onClick={handleSignOut}>
            <LogOut size={16} className="inline mr-2" />
            [Sign Out]
          </TerminalButton>
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
              onClick={handlePublishProfile}
              disabled={publishState === 'loading'}
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
              onClick={handleUnpublishProfile}
              disabled={publishState === 'loading'}
            >
              {publishState === 'loading' ? (
                <>
                  <Share2 size={16} className="inline mr-2 animate-pulse" />
                  [Unpublishing...]
                </>
              ) : (
                <>
                  <Share2 size={16} className="inline mr-2" />
                  [Unpublish]
                </>
              )}
            </TerminalButton>
          )}
          
          <TerminalButton onClick={() => navigate('/export')}>
            <Download size={16} className="inline mr-2" />
            [Export]
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
          &gt; Your Projects ({projects.length})
        </div>
        {projects.length === 0 ? (
          <div className="text-terminal-orange mb-5">
            No projects yet. Add your first project to get started!
          </div>
        ) : (
          <div className="bg-terminal-bg-lighter border border-terminal-border p-5">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-start auto-rows-fr">
              {projects.map(project => (
                <div key={project.id} className="min-w-0 h-full">
                  <ProjectCard
                    project={project}
                    onEdit={(p) => navigate(`/project/${p.id}/edit`)}
                    onDelete={onDeleteProject}
                    compact
                  />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;

