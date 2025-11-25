import React from 'react';
import { Github, ArrowLeft } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import ProjectCard from './ProjectCard';

const ProfileView = ({ user, projects, onBack }) => {
  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '40px', display: 'flex', alignItems: 'center', gap: '20px' }}>
        <TerminalButton onClick={onBack}>
          <ArrowLeft size={16} style={{ display: 'inline', marginRight: '8px' }} />
          [Back to Dashboard]
        </TerminalButton>
      </div>

      <div style={{ 
        border: '1px solid #00ff00',
        padding: '40px',
        marginBottom: '40px'
      }}>
        <div style={{ fontSize: '32px', marginBottom: '10px', textTransform: 'uppercase' }}>
          {user.name}
        </div>
        <div style={{ fontSize: '18px', color: '#00aa00', marginBottom: '20px' }}>
          Developer Profile
        </div>
        {user.github && (
          <div style={{ marginBottom: '10px' }}>
            <Github size={16} style={{ display: 'inline', marginRight: '8px' }} />
            github.com/{user.github}
          </div>
        )}
        <div style={{ 
          borderTop: '1px solid #00ff00',
          marginTop: '20px',
          paddingTop: '20px'
        }}>
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

