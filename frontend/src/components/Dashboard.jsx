import React from 'react';
import { Plus, Eye, Download, LogOut } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import ProjectCard from './ProjectCard';
import { useSupabase } from '../hooks/useSupabase';

const Dashboard = ({ user, projects, onAddProject, onEditProject, onDeleteProject, onViewProfile, onExport }) => {
  const { supabase } = useSupabase();

  const handleSignOut = async () => {
    if (confirm('Are you sure you want to sign out?')) {
      const { error } = await supabase.auth.signOut();
      if (error) {
        alert('Error signing out: ' + error.message);
      }
      // User will be automatically redirected by auth state change
    }
  };
  return (
    <div className="p-10 max-w-[1200px] mx-auto">
      <div className="mb-10">
        <div className="flex justify-between items-start">
          <div>
            <div className="text-2xl mb-2.5">
              &gt; {user.name}@dev-impact:~$
            </div>
            {user.github?.username && (
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
          projects.map(project => (
            <ProjectCard
              key={project.id}
              project={project}
              onEdit={onEditProject}
              onDelete={onDeleteProject}
              compact
            />
          ))
        )}
      </div>
    </div>
  );
};

export default Dashboard;

