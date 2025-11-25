import React from 'react';
import { Github, ArrowLeft } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import ProjectCard from './ProjectCard';

const ProfileView = ({ user, projects, onBack }) => {
  return (
    <div className="p-10 max-w-[1200px] mx-auto">
      <div className="mb-10 flex items-center gap-5">
        <TerminalButton onClick={onBack}>
          <ArrowLeft size={16} className="inline mr-2" />
          [Back to Dashboard]
        </TerminalButton>
      </div>

      <div className="border border-terminal-border p-10 mb-10">
        <div className="text-[32px] mb-2.5 uppercase text-terminal-orange">
          {user.name}
        </div>
        <div className="text-lg text-[#c9c5c0] mb-5">
          Developer Profile
        </div>
        {user.github && (
          <div className="mb-2.5">
            <Github size={16} className="inline mr-2" />
            github.com/{user.github}
          </div>
        )}
        <div className="border-t border-terminal-border mt-5 pt-5 text-[#c9c5c0]">
          {projects.length} {projects.length === 1 ? 'Project' : 'Projects'} • 
          {' '}{projects.reduce((sum, p) => sum + p.metrics.length, 0)} Achievements
        </div>
      </div>

      {projects.map(project => (
        <ProjectCard key={project.id} project={project} />
      ))}
    </div>
  );
};

export default ProfileView;

