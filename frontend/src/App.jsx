import React, { useState, useEffect } from 'react';
import LandingPage from './components/LandingPage';
import Onboarding from './components/Onboarding';
import Dashboard from './components/Dashboard';
import ProjectBuilder from './components/ProjectBuilder';
import ProfileView from './components/ProfileView';
import ExportPage from './components/ExportPage';
import './index.css';

// Helper function to load from localStorage
const loadFromStorage = (key, defaultValue) => {
  try {
    const saved = localStorage.getItem(key);
    return saved ? JSON.parse(saved) : defaultValue;
  } catch (e) {
    console.error(`Failed to parse ${key}:`, e);
    return defaultValue;
  }
};

export default function App() {
  const [user, setUser] = useState(() => loadFromStorage('dev-impact-user', null));
  const [page, setPage] = useState(() => 
    loadFromStorage('dev-impact-user', null) ? 'dashboard' : 'landing'
  );
  const [projects, setProjects] = useState(() => loadFromStorage('dev-impact-projects', []));
  const [editingProject, setEditingProject] = useState(null);

  // Save user data to localStorage whenever it changes
  useEffect(() => {
    if (user) {
      localStorage.setItem('dev-impact-user', JSON.stringify(user));
    }
  }, [user]);

  // Save projects to localStorage whenever they change
  useEffect(() => {
    if (projects.length > 0) {
      localStorage.setItem('dev-impact-projects', JSON.stringify(projects));
    }
  }, [projects]);

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
