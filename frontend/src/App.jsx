import React, { useState, useEffect } from 'react';
import { useSupabase } from './hooks/useSupabase';
import LandingPage from './components/LandingPage';
import Auth from './components/Auth';
import ResetPassword from './components/ResetPassword';
import Onboarding from './components/Onboarding';
import Dashboard from './components/Dashboard';
import ProjectBuilder from './components/ProjectBuilder';
import ProfileView from './components/ProfileView';
import ExportPage from './components/ExportPage';
import './index.css';

export default function App() {
  const { supabase, user: authUser, loading: authLoading } = useSupabase();
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

  // Load user profile from Supabase when authenticated
  useEffect(() => {
    const loadProfile = async () => {
      if (!authUser || !supabase) return;

      setDataLoading(true);
      try {
        // Try to load from Supabase first
        const { data, error } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', authUser.id)
          .single();

        if (error && error.code !== 'PGRST116') { // PGRST116 = not found
          console.error('Error loading profile:', error);
        }

        if (data) {
          // Map Supabase profile to app format
          setUserProfile({
            name: data.full_name,
            github: {
              username: data.github_username,
              avatar_url: data.github_avatar_url
            }
          });
        } else {
          // No profile in Supabase, check localStorage for migration
          const oldProfile = localStorage.getItem('dev-impact-user');
          if (oldProfile) {
            console.log('Found old localStorage profile, will migrate during onboarding');
            setUserProfile(JSON.parse(oldProfile));
          }
        }
      } catch (err) {
        console.error('Failed to load profile:', err);
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
  }, [authUser, supabase]);

  // Load projects from Supabase when user is authenticated
  useEffect(() => {
    const loadProjects = async () => {
      if (!authUser || !supabase) return;

      try {
        const { data, error } = await supabase
          .from('impact_projects')
          .select(`
            *,
            metrics:project_metrics (*)
          `)
          .eq('user_id', authUser.id)
          .order('display_order');

        if (error) {
          console.error('Error loading projects:', error);
          // Fall back to localStorage
          const oldProjects = localStorage.getItem('dev-impact-projects');
          if (oldProjects) {
            console.log('Loaded projects from localStorage');
            setProjects(JSON.parse(oldProjects));
          }
          return;
        }

        if (data && data.length > 0) {
          // Transform Supabase data to app format
          const transformedProjects = data.map(project => ({
            id: project.id,
            company: project.company,
            projectName: project.project_name,
            role: project.role,
            teamSize: project.team_size,
            problem: project.problem,
            contributions: project.contributions,
            techStack: project.tech_stack,
            metrics: project.metrics
              ?.sort((a, b) => a.display_order - b.display_order)
              .map(m => ({
                primary: m.primary_value,
                label: m.label,
                detail: m.detail
              })) || []
          }));
          setProjects(transformedProjects);
        } else {
          // No projects in Supabase, check localStorage
          const oldProjects = localStorage.getItem('dev-impact-projects');
          if (oldProjects) {
            console.log('Found old localStorage projects');
            setProjects(JSON.parse(oldProjects));
          }
        }
      } catch (err) {
        console.error('Failed to load projects:', err);
      }
    };

    if (authUser && userProfile) {
      loadProjects();
    }
  }, [authUser, userProfile, supabase]);

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
    if (!authUser || !supabase) return;

    try {
      // Save profile to Supabase
      const { error } = await supabase
        .from('profiles')
        .upsert({
          id: authUser.id,
          username: userData.github?.username || userData.name.toLowerCase().replace(/\s+/g, '-'),
          full_name: userData.name,
          github_username: userData.github?.username,
          github_avatar_url: userData.github?.avatar_url,
          is_published: false
        });

      if (error) {
        console.error('Error saving profile:', error);
        // Fall back to localStorage
        localStorage.setItem('dev-impact-user', JSON.stringify(userData));
      } else {
        console.log('Profile saved to Supabase');
        // Clear old localStorage
        localStorage.removeItem('dev-impact-user');
      }

      setUserProfile(userData);
      setCurrentView(null);
    } catch (err) {
      console.error('Failed to save profile:', err);
      setUserProfile(userData);
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
    if (!authUser || !supabase) return;

    try {
      setDataLoading(true);

      if (editingProject) {
        // Update existing project
        const { error: projectError } = await supabase
          .from('impact_projects')
          .update({
            company: project.company,
            project_name: project.projectName,
            role: project.role,
            team_size: project.teamSize,
            problem: project.problem,
            contributions: project.contributions,
            tech_stack: project.techStack
          })
          .eq('id', project.id);

        if (projectError) throw projectError;

        // Delete old metrics and insert new ones
        await supabase.from('project_metrics').delete().eq('project_id', project.id);
        
        if (project.metrics && project.metrics.length > 0) {
          const metricsToInsert = project.metrics.map((metric, index) => ({
            project_id: project.id,
            primary_value: metric.primary,
            label: metric.label,
            detail: metric.detail || null,
            display_order: index
          }));

          const { error: metricsError } = await supabase
            .from('project_metrics')
            .insert(metricsToInsert);

          if (metricsError) throw metricsError;
        }

        setProjects(projects.map(p => p.id === project.id ? project : p));
        console.log('Project updated in Supabase');
      } else {
        // Insert new project
        const { data: projectData, error: projectError } = await supabase
          .from('impact_projects')
          .insert({
            user_id: authUser.id,
            company: project.company,
            project_name: project.projectName,
            role: project.role,
            team_size: project.teamSize,
            problem: project.problem,
            contributions: project.contributions,
            tech_stack: project.techStack,
            display_order: projects.length
          })
          .select()
          .single();

        if (projectError) throw projectError;

        // Insert metrics
        if (project.metrics && project.metrics.length > 0) {
          const metricsToInsert = project.metrics.map((metric, index) => ({
            project_id: projectData.id,
            primary_value: metric.primary,
            label: metric.label,
            detail: metric.detail || null,
            display_order: index
          }));

          const { error: metricsError } = await supabase
            .from('project_metrics')
            .insert(metricsToInsert);

          if (metricsError) throw metricsError;
        }

        setProjects([...projects, { ...project, id: projectData.id }]);
        console.log('Project saved to Supabase');
      }

      // Clear old localStorage
      localStorage.removeItem('dev-impact-projects');
    } catch (err) {
      console.error('Failed to save project:', err);
      // Fall back to localStorage
      if (editingProject) {
        setProjects(projects.map(p => p.id === project.id ? project : p));
      } else {
        setProjects([...projects, project]);
      }
      localStorage.setItem('dev-impact-projects', JSON.stringify(projects));
    } finally {
      setDataLoading(false);
      setEditingProject(null);
      setCurrentView('dashboard');
    }
  };

  const handleDeleteProject = async (id) => {
    if (!confirm('Delete this project?')) return;

    if (!authUser || !supabase) return;

    try {
      const { error } = await supabase
        .from('impact_projects')
        .delete()
        .eq('id', id);

      if (error) throw error;

      setProjects(projects.filter(p => p.id !== id));
      console.log('Project deleted from Supabase');
    } catch (err) {
      console.error('Failed to delete project:', err);
      // Fall back to local state update
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
