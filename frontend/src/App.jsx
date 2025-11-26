import React, { useState, useEffect } from 'react';
import { useSupabase } from './hooks/useSupabase';
import LandingPage from './components/LandingPage';
import Auth from './components/Auth';
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
  const { user: authUser, loading: authLoading } = useSupabase();
  const [userProfile, setUserProfile] = useState(() => loadFromStorage('dev-impact-user', null));
  const [currentView, setCurrentView] = useState(null); // null, 'auth', 'onboarding', 'dashboard', etc.
  const [projects, setProjects] = useState(() => loadFromStorage('dev-impact-projects', []));
  const [editingProject, setEditingProject] = useState(null);

  // Determine which page to show based on auth and profile state
  const page = (() => {
    // If explicitly navigating to a page, use that
    if (currentView) return currentView;

    // If still loading auth, show loading
    if (authLoading) return 'loading';

    // Not authenticated - show landing
    if (!authUser) return 'landing';

    // Authenticated but no profile - show onboarding
    if (!userProfile) return 'onboarding';

    // Authenticated with profile - show dashboard
    return 'dashboard';
  })();

  // Save user profile to localStorage whenever it changes
  useEffect(() => {
    if (userProfile) {
      localStorage.setItem('dev-impact-user', JSON.stringify(userProfile));
    }
  }, [userProfile]);

  // Save projects to localStorage whenever they change
  useEffect(() => {
    if (projects.length > 0) {
      localStorage.setItem('dev-impact-projects', JSON.stringify(projects));
    }
  }, [projects]);

  const handleAuthSuccess = () => {
    // After successful auth, reset view to let automatic routing handle it
    setCurrentView(null);
  };

  const handleOnboardingComplete = (userData) => {
    setUserProfile(userData);
    setCurrentView(null); // Will auto-navigate to dashboard
  };

  const handleAddProject = () => {
    setEditingProject(null);
    setCurrentView('builder');
  };

  const handleEditProject = (project) => {
    setEditingProject(project);
    setCurrentView('builder');
  };

  const handleSaveProject = (project) => {
    if (editingProject) {
      setProjects(projects.map(p => p.id === project.id ? project : p));
    } else {
      setProjects([...projects, project]);
    }
    setEditingProject(null);
    setCurrentView('dashboard');
  };

  const handleDeleteProject = (id) => {
    if (confirm('Delete this project?')) {
      setProjects(projects.filter(p => p.id !== id));
    }
  };

  return (
    <div className="min-h-screen bg-[#2d2d2d]">
      {page === 'loading' && (
        <div className="min-h-screen flex items-center justify-center">
          <div className="fade-in">
            <div>&gt; Loading dev-impact...</div>
          </div>
        </div>
      )}
      {page === 'landing' && (
        <LandingPage onStart={() => setCurrentView('auth')} />
      )}
      {page === 'auth' && (
        <Auth onAuthSuccess={handleAuthSuccess} />
      )}
      {page === 'onboarding' && (
        <Onboarding onComplete={handleOnboardingComplete} />
      )}
      {page === 'dashboard' && (
        <Dashboard
          user={userProfile}
          projects={projects}
          onAddProject={handleAddProject}
          onEditProject={handleEditProject}
          onDeleteProject={handleDeleteProject}
          onViewProfile={() => setCurrentView('profile')}
          onExport={() => setCurrentView('export')}
        />
      )}
      {page === 'builder' && (
        <ProjectBuilder
          editProject={editingProject}
          onSave={handleSaveProject}
          onCancel={() => setCurrentView('dashboard')}
        />
      )}
      {page === 'profile' && (
        <ProfileView
          user={userProfile}
          projects={projects}
          onBack={() => setCurrentView('dashboard')}
        />
      )}
      {page === 'export' && (
        <ExportPage
          user={userProfile}
          projects={projects}
          onBack={() => setCurrentView('dashboard')}
        />
      )}
    </div>
  );
}
