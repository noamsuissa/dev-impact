import React, { useState } from 'react';
import { Plus, Eye, Download, LogOut, Github } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import ProjectCard from './ProjectCard';
import { useSupabase } from '../hooks/useSupabase';
import { completeGitHubAuth } from '../utils/githubAuth';

const Dashboard = ({ user, projects, onAddProject, onEditProject, onDeleteProject, onViewProfile, onExport, onGitHubConnect }) => {
  const { supabase } = useSupabase();
  const [githubState, setGithubState] = useState('initial'); // initial, loading, awaiting, success, error
  const [deviceCode, setDeviceCode] = useState(null);
  const [error, setError] = useState(null);

  const handleSignOut = async () => {
    if (confirm('Are you sure you want to sign out?')) {
      const { error } = await supabase.auth.signOut();
      if (error) {
        alert('Error signing out: ' + error.message);
      }
      // User will be automatically redirected by auth state change
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
  return (
    <div className="p-10 max-w-[1200px] mx-auto">
      <div className="mb-10">
        <div className="flex justify-between items-start">
          <div>
            <div className="text-2xl mb-2.5">
              &gt; {user.name}@dev-impact:~$
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
          <TerminalButton onClick={onAddProject}>
            <Plus size={16} className="inline mr-2" />
            [Add Project]
          </TerminalButton>
          <TerminalButton onClick={onViewProfile}>
            <Eye size={16} className="inline mr-2" />
            [Preview Profile]
          </TerminalButton>
          <TerminalButton onClick={onExport}>
            <Download size={16} className="inline mr-2" />
            [Export]
          </TerminalButton>
        </div>
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
                    onEdit={onEditProject}
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

