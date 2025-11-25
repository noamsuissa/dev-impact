import React, { useState } from 'react';
import LandingPage from './components/LandingPage';
import Onboarding from './components/Onboarding';
import Dashboard from './components/Dashboard';
import ProjectBuilder from './components/ProjectBuilder';
import ProfileView from './components/ProfileView';
import ExportPage from './components/ExportPage';
import './index.css';

export default function App() {
  const [page, setPage] = useState('landing'); // landing, onboarding, dashboard, builder, profile, export
  const [user, setUser] = useState(null);
  const [projects, setProjects] = useState([]);
  const [editingProject, setEditingProject] = useState(null);

  const handleOnboardingComplete = (userData) => {
    setUser(userData);
    setPage('dashboard');
  };

  const handleAddProject = () => {
    setEditingProject(null);
    setPage('builder');
  };

  const handleEditProject = (project) => {
    setEditingProject(project);
    setPage('builder');
  };

  const handleSaveProject = (project) => {
    if (editingProject) {
      setProjects(projects.map(p => p.id === project.id ? project : p));
    } else {
      setProjects([...projects, project]);
    }
    setEditingProject(null);
    setPage('dashboard');
  };

  const handleDeleteProject = (id) => {
    if (confirm('Delete this project?')) {
      setProjects(projects.filter(p => p.id !== id));
    }
  };

  return (
    <div className="min-h-screen bg-[#2d2d2d]">
      {page === 'landing' && (
        <LandingPage onStart={() => setPage('onboarding')} />
      )}
      {page === 'onboarding' && (
        <Onboarding onComplete={handleOnboardingComplete} />
      )}
      {page === 'dashboard' && (
        <Dashboard
          user={user}
          projects={projects}
          onAddProject={handleAddProject}
          onEditProject={handleEditProject}
          onDeleteProject={handleDeleteProject}
          onViewProfile={() => setPage('profile')}
          onExport={() => setPage('export')}
        />
      )}
      {page === 'builder' && (
        <ProjectBuilder
          editProject={editingProject}
          onSave={handleSaveProject}
          onCancel={() => setPage('dashboard')}
        />
      )}
      {page === 'profile' && (
        <ProfileView
          user={user}
          projects={projects}
          onBack={() => setPage('dashboard')}
        />
      )}
      {page === 'export' && (
        <ExportPage
          user={user}
          projects={projects}
          onBack={() => setPage('dashboard')}
        />
      )}
    </div>
  );
}
