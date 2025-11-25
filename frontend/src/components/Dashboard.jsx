import React from 'react';
import { Plus, Eye, Download } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import ProjectCard from './ProjectCard';

const Dashboard = ({ user, projects, onAddProject, onEditProject, onDeleteProject, onViewProfile, onExport }) => {
  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '40px' }}>
        <div style={{ fontSize: '24px', marginBottom: '10px' }}>
          &gt; {user.name}@dev-impact:~$
        </div>
        {user.github && (
          <div style={{ color: '#ff8c42' }}>
            Connected to GitHub: @{user.github}
          </div>
        )}
      </div>

      <div style={{ marginBottom: '40px' }}>
        <div style={{ fontSize: '18px', marginBottom: '20px' }}>
          &gt; Actions
        </div>
        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
          <TerminalButton onClick={onAddProject}>
            <Plus size={16} style={{ display: 'inline', marginRight: '8px' }} />
            [Add Project]
          </TerminalButton>
          <TerminalButton onClick={onViewProfile}>
            <Eye size={16} style={{ display: 'inline', marginRight: '8px' }} />
            [Preview Profile]
          </TerminalButton>
          <TerminalButton onClick={onExport}>
            <Download size={16} style={{ display: 'inline', marginRight: '8px' }} />
            [Export]
          </TerminalButton>
        </div>
      </div>

      <div>
        <div style={{ fontSize: '18px', marginBottom: '20px' }}>
          &gt; Your Projects ({projects.length})
        </div>
        {projects.length === 0 ? (
          <div style={{ color: '#ff8c42', marginBottom: '20px' }}>
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

