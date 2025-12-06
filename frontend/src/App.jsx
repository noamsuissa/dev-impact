import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import { user as userClient, projects as projectsClient } from './utils/client';
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/react';

// Pages / Components
import LandingPage from './components/LandingPage';
import SignIn from './components/auth/SignIn';
import SignUp from './components/auth/SignUp';
import ForgotPassword from './components/auth/ForgotPassword';
import ResetPassword from './components/ResetPassword';
import Onboarding from './components/Onboarding';
import Dashboard from './components/Dashboard';
import ProjectBuilder from './components/ProjectBuilder';
import ProfileView from './components/ProfileView';
import ExportPage from './components/ExportPage';
import AccountPage from './components/AccountPage';
import PublicProfile from './components/PublicProfile';
import NotFound from './components/NotFound';
import ProtectedRoute from './components/ProtectedRoute';
import AboutPage from './components/AboutPage';
import ExamplePage from './components/ExamplePage';

import './index.css';

// Component to handle initial redirects based on hash (Supabase auth)
const AuthRedirectHandler = () => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const hashParams = new URLSearchParams(window.location.hash.substring(1));
    if (hashParams.get('type') === 'recovery') {
      // Redirect to reset password page, preserving the hash
      navigate('/reset-password' + window.location.hash);
    }
  }, [navigate, location]);

  return null;
};

// Authenticated Layout Component
// This component wraps all protected routes.
// It is responsible for fetching the user profile and projects once authenticated.
const AuthenticatedLayout = () => {
  const [userProfile, setUserProfile] = useState(null);
  const [projects, setProjects] = useState([]);
  const [isLoadingProfile, setIsLoadingProfile] = useState(true);
  const navigate = useNavigate();

  // Load user profile
  useEffect(() => {
    const loadProfile = async () => {
      try {
        const data = await userClient.getProfile();
        if (data) {
          setUserProfile({
            name: data.full_name,
            username: data.username,
            github: data.github_username ? {
              username: data.github_username,
              avatar_url: data.github_avatar_url
            } : null
          });
        } else {
             // No profile found -> Onboarding
             // We can't navigate here if we are already on onboarding path, avoid loops
             if (window.location.pathname !== '/onboarding') {
                navigate('/onboarding');
             }
        }
      } catch (err) {
        console.error('Failed to load profile:', err);
        // If profile load fails, we assume onboarding is needed or error state
        if (window.location.pathname !== '/onboarding') {
            navigate('/onboarding');
        }
      } finally {
        setIsLoadingProfile(false);
      }
    };
    loadProfile();
  }, [navigate]);

  // Load projects
  useEffect(() => {
    const loadProjects = async () => {
      if (!userProfile) return;
      try {
        const data = await projectsClient.list();
        setProjects(data || []);
      } catch (err) {
        console.error('Failed to load projects:', err);
        setProjects([]);
      }
    };
    loadProjects();
  }, [userProfile]);

  const handleOnboardingComplete = async (userData) => {
    try {
      await userClient.completeOnboarding(userData);
      setUserProfile(userData);
      navigate('/dashboard');
    } catch (err) {
      console.error('Failed to save profile:', err);
      setUserProfile(userData);
    }
  };

  const handleSaveProject = async (project) => {
    try {
      const isExisting = projects.some(p => p.id === project.id);
      if (isExisting) {
        const updated = await projectsClient.update(project.id, project);
        setProjects(projects.map(p => p.id === project.id ? updated : p));
      } else {
        const created = await projectsClient.create(project);
        setProjects([...projects, created]);
      }
    } catch (err) {
      console.error('Failed to save project:', err);
      alert('Failed to save project: ' + err.message);
      throw err;
    }
  };

  const handleDeleteProject = async (id) => {
    if (!confirm('Delete this project?')) return;
    try {
      await projectsClient.delete(id);
      setProjects(projects.filter(p => p.id !== id));
    } catch (err) {
      console.error('Failed to delete project:', err);
      alert('Failed to delete project: ' + err.message);
    }
  };

  const handleGitHubConnect = async (githubData) => {
    try {
      await userClient.updateProfile({
        github_username: githubData.username,
        github_avatar_url: githubData.avatar_url
      });
      setUserProfile({
        ...userProfile,
        github: {
          username: githubData.username,
          avatar_url: githubData.avatar_url
        }
      });
    } catch (err) {
      console.error('Failed to save GitHub connection:', err);
      alert('GitHub connected but failed to save. Please try again.');
    }
  };

  if (isLoadingProfile) {
    return (
      <div className="min-h-screen bg-[#2d2d2d] flex items-center justify-center">
        <div className="fade-in">
          <div>&gt; Loading profile data...</div>
        </div>
      </div>
    );
  }

  // Pass props to children via Outlet context or cloneElement?
  // React Router v6 Outlet context is cleaner.
  return (
    <Outlet context={{ 
        userProfile, 
        projects, 
        handleOnboardingComplete, 
        handleSaveProject, 
        handleDeleteProject, 
        handleGitHubConnect 
    }} />
  );
};

// Route wrapper components to consume context and pass as props
// This adapts the Outlet context back to props for existing components
import { useOutletContext } from 'react-router-dom';

const OnboardingRoute = () => {
    const { userProfile, handleOnboardingComplete } = useOutletContext();
    const navigate = useNavigate();
    
    // If profile exists, redirect to dashboard
    useEffect(() => {
        if (userProfile) navigate('/dashboard');
    }, [userProfile, navigate]);

    if (userProfile) return null;
    return <Onboarding onComplete={handleOnboardingComplete} />;
}

const DashboardRoute = () => {
    const { userProfile, projects, handleDeleteProject, handleGitHubConnect } = useOutletContext();
    const navigate = useNavigate();

    // If no profile, redirect to onboarding (double check, though layout handles it too)
    useEffect(() => {
        if (!userProfile) navigate('/onboarding');
    }, [userProfile, navigate]);

    if (!userProfile) return null;

    return <Dashboard 
        user={userProfile} 
        projects={projects} 
        onDeleteProject={handleDeleteProject}
        onGitHubConnect={handleGitHubConnect}
    />;
}

const ProjectBuilderRoute = () => {
    const { userProfile, projects, handleSaveProject } = useOutletContext();
    const navigate = useNavigate();
    
    if (!userProfile) {
        navigate('/onboarding');
        return null;
    }

    return <ProjectBuilder onSave={handleSaveProject} projects={projects} />;
}

const ProfileViewRoute = () => {
    const { userProfile, projects } = useOutletContext();
    const navigate = useNavigate();
    
    if (!userProfile) {
        navigate('/onboarding');
        return null;
    }

    return <ProfileView user={userProfile} projects={projects} />;
}

const ExportPageRoute = () => {
    const { userProfile, projects } = useOutletContext();
    const navigate = useNavigate();
    
    if (!userProfile) {
        navigate('/onboarding');
        return null;
    }

    return <ExportPage user={userProfile} projects={projects} />;
}

const AccountPageRoute = () => {
    const { userProfile, projects } = useOutletContext();
    const navigate = useNavigate();
    
    if (!userProfile) {
        navigate('/onboarding');
        return null;
    }

    return <AccountPage user={userProfile} projects={projects} />;
}

// Component to handle subdomain-based profile routing
const SubdomainProfileHandler = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const baseDomain = import.meta.env.VITE_BASE_DOMAIN || 'dev-impact.io';
  
  useEffect(() => {
    const hostname = window.location.hostname;
    
    // Check if we're on a subdomain (e.g., username.dev-impact.io)
    // Exclude localhost and IP addresses
    if (hostname !== 'localhost' && 
        !hostname.match(/^\d+\.\d+\.\d+\.\d+$/) && 
        hostname.includes('.')) {
      
      // Extract subdomain (everything before the first dot)
      const parts = hostname.split('.');
      const subdomain = parts[0];
      
      // Check if subdomain is not the main domain parts
      // For dev-impact.io, we want to catch username.dev-impact.io
      const domainParts = baseDomain.split('.');
      const isSubdomain = parts.length > domainParts.length;
      
      if (isSubdomain && subdomain && subdomain !== 'www') {
        // We're on a subdomain, extract username and navigate
        const username = subdomain;
        // Only navigate if we're not already showing that profile
        if (location.pathname !== `/${username}`) {
          // Use replace to avoid adding to history
          navigate(`/${username}`, { replace: true });
        }
      }
    }
  }, [navigate, location, baseDomain]);
  
  return null;
};

export default function App() {
  const { loading: authLoading } = useAuth();
  
  // Loading screen
  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#2d2d2d] flex items-center justify-center">
        <div className="fade-in">
          <div>&gt; Loading dev-impact...</div>
        </div>
      </div>
    );
  }

  return (
    <>
      <Router>
        <AuthRedirectHandler />
        <SubdomainProfileHandler />
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/signin" element={<SignIn />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/example" element={<ExamplePage />} />
          
          {/* Protected Routes - All nested under a Layout */}
          <Route element={<ProtectedRoute><AuthenticatedLayout /></ProtectedRoute>}>
              <Route path="/onboarding" element={<OnboardingRoute />} />
              <Route path="/dashboard" element={<DashboardRoute />} />
              <Route path="/project/new" element={<ProjectBuilderRoute />} />
              <Route path="/project/:projectId/edit" element={<ProjectBuilderRoute />} />
              <Route path="/profile" element={<ProfileViewRoute />} />
              <Route path="/export" element={<ExportPageRoute />} />
              <Route path="/account" element={<AccountPageRoute />} />
          </Route>
          
          {/* Public Profile Route - supports both subdomain and path-based access */}
          <Route path="/404" element={<NotFound />} />
          <Route path="/:username" element={<PublicProfile />} />
          
          {/* 404 Route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
      <Analytics />
      <SpeedInsights />
    </>
  );
}
