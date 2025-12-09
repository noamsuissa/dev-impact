import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Github, ArrowLeft } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import ProjectCard from './ProjectCard';
import ProjectModal from './ProjectModal';

const ProfileView = ({ user, projects }) => {
  const [selectedProject, setSelectedProject] = useState(null);
  const [isProjectModalOpen, setIsProjectModalOpen] = useState(false);

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
        <div className="text-[32px] mb-2.5 uppercase text-terminal-orange">
          {user.name}
        </div>
        <div className="text-lg text-[#c9c5c0] mb-5">
          Developer Profile
        </div>
        {user.github?.username && (
          <div className="mb-2.5">
            <Github size={16} className="inline mr-2" />
            github.com/{user.github.username}
          </div>
        )}
        <div className="border-t border-terminal-border mt-5 pt-5 text-[#c9c5c0]">
          {projects.length} {projects.length === 1 ? 'Project' : 'Projects'} • 
          {' '}{projects.reduce((sum, p) => sum + p.metrics.length, 0)} Achievements
        </div>
      </div>

      {projects.length > 0 && (
        <div className="bg-terminal-bg-lighter border border-terminal-border p-5">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-start auto-rows-fr">
            {projects.map(project => (
              <div key={project.id} className="min-w-0 h-full">
                <ProjectCard
                  project={project}
                  compact
                  onClick={(p) => {
                    setSelectedProject(p);
                    setIsProjectModalOpen(true);
                  }}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Project Modal (Read-only) */}
      <ProjectModal
        isOpen={isProjectModalOpen}
        onClose={() => {
          setIsProjectModalOpen(false);
          setSelectedProject(null);
        }}
        project={selectedProject}
        readOnly={true}
      />
    </div>
  );
};

export default ProfileView;

