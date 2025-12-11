import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import { user as userClient, projects as projectsClient, userProfiles } from './utils/client';
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
import PricingPage from './components/PricingPage';
import AboutPage from './components/AboutPage';
import ExamplePage from './components/ExamplePage';
import SubscriptionSuccess from './components/SubscriptionSuccess';
import SubscriptionCancel from './components/SubscriptionCancel';

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
  const [profiles, setProfiles] = useState([]);
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

  // Load profiles
  useEffect(() => {
    const loadProfiles = async () => {
      if (!userProfile) return;
      try {
        const data = await userProfiles.list();
        setProfiles(data || []);
      } catch (err) {
        console.error('Failed to load profiles:', err);
        setProfiles([]);
      }
    };
    loadProfiles();
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
        // Ensure profile_id is included in the updated project
        const updatedWithProfile = {
          ...updated,
          profile_id: updated.profile_id || project.profile_id || null
        };
        setProjects(projects.map(p => p.id === project.id ? updatedWithProfile : p));
      } else {
        const created = await projectsClient.create(project);
        // Ensure profile_id is included in the created project
        const createdWithProfile = {
          ...created,
          profile_id: created.profile_id || project.profile_id || null
        };
        setProjects([...projects, createdWithProfile]);
      }
    } catch (err) {
      console.error('Failed to save project:', err);
      alert('Failed to save project: ' + err.message);
      throw err;
    }
  };

  const handleSaveProfile = async (profileData) => {
    try {
      const created = await userProfiles.create(profileData);
      setProfiles([...profiles, created]);
      return created;
    } catch (err) {
      console.error('Failed to save profile:', err);
      throw err;
    }
  };

  const handleUpdateProfile = async (profileId, profileData) => {
    try {
      const updated = await userProfiles.update(profileId, profileData);
      setProfiles(profiles.map(p => p.id === profileId ? updated : p));
      return updated;
    } catch (err) {
      console.error('Failed to update profile:', err);
      throw err;
    }
  };

  const handleDeleteProfile = async (profileId) => {
    try {
      await userProfiles.delete(profileId);
      setProfiles(profiles.filter(p => p.id !== profileId));
      // Also remove projects that belonged to this profile (backend already deleted them)
      setProjects(projects.filter(p => p.profile_id !== profileId));
    } catch (err) {
      console.error('Failed to delete profile:', err);
      throw err;
    }
  };

  const handleProfileDeleted = (profileId) => {
    // Called after profile is deleted to update projects state
    // Projects are already deleted by backend, just filter them from state
    setProjects(projects.filter(p => p.profile_id !== profileId));
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
      profiles,
      handleOnboardingComplete,
      handleSaveProject,
      handleDeleteProject,
      handleSaveProfile,
      handleUpdateProfile,
      handleDeleteProfile,
      handleProfileDeleted,
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
  const { userProfile, projects, handleDeleteProject, handleGitHubConnect, handleSaveProject, handleProfileDeleted } = useOutletContext();
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
    onSaveProject={handleSaveProject}
    onGitHubConnect={handleGitHubConnect}
    onProfileDeleted={handleProfileDeleted}
  />;
}

const ProjectBuilderRoute = () => {
  const { userProfile, projects, profiles, handleSaveProject } = useOutletContext();
  const navigate = useNavigate();

  if (!userProfile) {
    navigate('/onboarding');
    return null;
  }

  // Ensure profiles is an array
  const profilesList = Array.isArray(profiles) ? profiles : [];

  // Get selected profile ID from localStorage or use first profile
  const getSelectedProfileId = () => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('selectedProfileId');
      if (stored && profilesList.some(p => p.id === stored)) {
        return stored;
      }
    }
    return profilesList.length > 0 ? profilesList[0].id : null;
  };

  return <ProjectBuilder
    onSave={handleSaveProject}
    projects={projects || []}
    profiles={profilesList}
    selectedProfileId={getSelectedProfileId()}
  />;
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

// Helper function to check if we're on a subdomain and extract username
const getSubdomainUsername = () => {
  const hostname = window.location.hostname;
  const baseDomain = import.meta.env.VITE_BASE_DOMAIN || 'dev-impact.io';

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
      return subdomain;
    }
  }

  return null;
};

// Component to conditionally render LandingPage or PublicProfile based on subdomain
const RootRoute = () => {
  const subdomainUsername = getSubdomainUsername();

  // If we're on a subdomain, show the profile
  if (subdomainUsername) {
    return <PublicProfile />;
  }

  // Otherwise, show the landing page
  return <LandingPage />;
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
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<RootRoute />} />
          <Route path="/signin" element={<SignIn />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/example" element={<ExamplePage />} />
          <Route path="/subscription/success" element={<SubscriptionSuccess />} />
          <Route path="/subscription/cancel" element={<SubscriptionCancel />} />

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
          <Route path="/:username/:profileSlug" element={<PublicProfile />} />
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
