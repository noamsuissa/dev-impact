import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import { user as userClient, projects as projectsClient } from './utils/client';
import LandingPage from './components/LandingPage';
import Auth from './components/Auth';
import ResetPassword from './components/ResetPassword';
import Onboarding from './components/Onboarding';
import Dashboard from './components/Dashboard';
import ProjectBuilder from './components/ProjectBuilder';
import ProfileView from './components/ProfileView';
import ExportPage from './components/ExportPage';
import PublicProfile from './components/PublicProfile';
import NotFound from './components/NotFound';
import './index.css';

export default function App() {
  const { user: authUser, loading: authLoading } = useAuth();
  const [userProfile, setUserProfile] = useState(null);
  const [currentView, setCurrentView] = useState(null);
  const [projects, setProjects] = useState([]);
  const [editingProject, setEditingProject] = useState(null);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [dataLoading, setDataLoading] = useState(false);
  
  // Check if user is resetting password (from email link)
  const [isResettingPassword, setIsResettingPassword] = useState(() => {
    const hashParams = new URLSearchParams(window.location.hash.substring(1));
    return hashParams.get('type') === 'recovery';
  });

  // Handle initial load to prevent flicker
  useEffect(() => {
    if (!authLoading && isInitialLoad) {
      const timer = setTimeout(() => setIsInitialLoad(false), 100);
      return () => clearTimeout(timer);
    }
  }, [authLoading, isInitialLoad]);

  // Load user profile from API when authenticated
  useEffect(() => {
    const loadProfile = async () => {
      if (!authUser) return;

      setDataLoading(true);
      try {
        // Try to load from API
        const data = await userClient.getProfile();

        if (data) {
          // Map API profile to app format
          setUserProfile({
            name: data.full_name,
            github: data.github_username ? {
              username: data.github_username,
              avatar_url: data.github_avatar_url
            } : null
          });
        }
      } catch (err) {
        console.error('Failed to load profile:', err);
        // Profile not found - user needs onboarding
        setUserProfile(null);
      } finally {
        setDataLoading(false);
      }
    };

    if (authUser) {
      loadProfile();
    } else {
      // Clear profile when logged out
      setUserProfile(null);
      setProjects([]);
    }
  }, [authUser]);

  // Load projects from API when user is authenticated
  useEffect(() => {
    const loadProjects = async () => {
      if (!authUser) return;

      try {
        const data = await projectsClient.list();
        setProjects(data || []);
      } catch (err) {
        console.error('Failed to load projects:', err);
        setProjects([]);
      }
    };

    if (authUser && userProfile) {
      loadProjects();
    }
  }, [authUser, userProfile]);

  // Determine which page to show based on auth and profile state
  const page = (() => {
    // If resetting password, show reset page
    if (isResettingPassword) return 'reset-password';

    // If explicitly navigating to a page, use that
    if (currentView) return currentView;

    // If still loading auth, data, or initial load, show loading
    if (authLoading || isInitialLoad || (authUser && dataLoading && !userProfile)) return 'loading';

    // Not authenticated - show landing
    if (!authUser) return 'landing';

    // Authenticated but no profile - show onboarding
    if (!userProfile) return 'onboarding';

    // Authenticated with profile - show dashboard
    return 'dashboard';
  })();

  const handleAuthSuccess = () => {
    setCurrentView(null);
  };

  const handlePasswordResetSuccess = () => {
    setIsResettingPassword(false);
    window.location.hash = '';
    setCurrentView('auth');
  };

  const handleOnboardingComplete = async (userData) => {
    if (!authUser) return;

    try {
      // Save profile via API
      await userClient.completeOnboarding(userData);
      
      console.log('Profile saved via API');
      setUserProfile(userData);
      setCurrentView(null);
    } catch (err) {
      console.error('Failed to save profile:', err);
      // Still set profile locally so user can proceed
      setUserProfile(userData);
      setCurrentView(null);
    }
  };

  const handleAddProject = () => {
    setEditingProject(null);
    setCurrentView('builder');
  };

  const handleEditProject = (project) => {
    setEditingProject(project);
    setCurrentView('builder');
  };

  const handleSaveProject = async (project) => {
    if (!authUser) return;

    try {
      setDataLoading(true);

      if (editingProject) {
        // Update existing project
        const updated = await projectsClient.update(project.id, project);
        setProjects(projects.map(p => p.id === project.id ? updated : p));
        console.log('Project updated via API');
      } else {
        // Create new project
        const created = await projectsClient.create(project);
        setProjects([...projects, created]);
        console.log('Project created via API');
      }
    } catch (err) {
      console.error('Failed to save project:', err);
      alert('Failed to save project: ' + err.message);
    } finally {
      setDataLoading(false);
      setEditingProject(null);
      setCurrentView('dashboard');
    }
  };

  const handleDeleteProject = async (id) => {
    if (!confirm('Delete this project?')) return;

    if (!authUser) return;

    try {
      await projectsClient.delete(id);
      setProjects(projects.filter(p => p.id !== id));
      console.log('Project deleted via API');
    } catch (err) {
      console.error('Failed to delete project:', err);
      alert('Failed to delete project: ' + err.message);
    }
  };

  const handleGitHubConnect = async (githubData) => {
    if (!authUser) return;

    try {
      // Update profile via API with GitHub info
      await userClient.updateProfile({
        github_username: githubData.username,
        github_avatar_url: githubData.avatar_url
      });

      // Update local state
      setUserProfile({
        ...userProfile,
        github: {
          username: githubData.username,
          avatar_url: githubData.avatar_url
        }
      });

      console.log('GitHub connected and saved via API');
    } catch (err) {
      console.error('Failed to save GitHub connection:', err);
      alert('GitHub connected but failed to save. Please try again.');
    }
  };

  return (
    <Router>
      <Routes>
        {/* Main app routes */}
        <Route path="/" element={
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
      {page === 'reset-password' && (
        <ResetPassword onSuccess={handlePasswordResetSuccess} />
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
          onGitHubConnect={handleGitHubConnect}
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
        } />
        
        {/* Public profile route */}
        <Route path="/:username" element={<PublicProfile />} />
        
        {/* 404 routes - must be last */}
        <Route path="/404" element={<NotFound />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}
