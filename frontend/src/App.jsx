import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import { useDashboard } from './hooks/useDashboard';
import { user as userClient } from './utils/client';
import { DashboardProvider } from './contexts/DashboardContext';
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
import PrivacyPolicy from './components/PrivacyPolicy';
import TermsOfService from './components/TermsOfService';
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
// It uses the user from AuthContext which includes the merged profile data.
const AuthenticatedLayout = () => {
  const { user, updateUserProfile } = useAuth();
  const navigate = useNavigate();

  // Check if user has completed onboarding (has username)
  useEffect(() => {
    if (user && !user.username) {
      // No username means onboarding not complete
      if (window.location.pathname !== '/onboarding') {
        navigate('/onboarding');
      }
    }
  }, [user, navigate]);

  const handleOnboardingComplete = async (userData) => {
    try {
      await userClient.completeOnboarding(userData);
      // Refresh the user profile in AuthContext
      await updateUserProfile();
      navigate('/dashboard');
    } catch (err) {
      console.error('Failed to save profile:', err);
      // Still update the context even if save fails
      await updateUserProfile();
    }
  };

  // Convert auth user to userProfile format for backward compatibility
  const userProfile = user ? {
    name: user.name,
    username: user.username,
    github: user.github
  } : null;

  // Wrap Outlet with DashboardProvider to provide dashboard state to all child routes
  return (
    <DashboardProvider>
      <Outlet context={{
        userProfile,
        handleOnboardingComplete
      }} />
    </DashboardProvider>
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
  const { userProfile } = useOutletContext();
  const navigate = useNavigate();

  // If no profile, redirect to onboarding (double check, though layout handles it too)
  useEffect(() => {
    if (!userProfile) navigate('/onboarding');
  }, [userProfile, navigate]);

  if (!userProfile) return null;

  return <Dashboard />;
}

const ProjectBuilderRoute = () => {
  const { userProfile } = useOutletContext();
  const { projects, profiles } = useDashboard();
  const navigate = useNavigate();

  if (!userProfile) {
    navigate('/onboarding');
    return null;
  }

  return <ProjectBuilder
    onSave={projects.save}
    projects={projects.list}
    profiles={profiles.list}
    selectedProfileId={profiles.selectedId}
  />;
}

const ProfileViewRoute = () => {
  const { userProfile } = useOutletContext();
  const { projects } = useDashboard();
  const navigate = useNavigate();

  if (!userProfile) {
    navigate('/onboarding');
    return null;
  }

  return <ProfileView user={userProfile} projects={projects.list} />;
}

const ExportPageRoute = () => {
  const { userProfile } = useOutletContext();
  const { projects } = useDashboard();
  const navigate = useNavigate();

  if (!userProfile) {
    navigate('/onboarding');
    return null;
  }

  return <ExportPage user={userProfile} projects={projects.list} />;
}

const AccountPageRoute = () => {
  const { userProfile } = useOutletContext();
  const { projects } = useDashboard();
  const navigate = useNavigate();

  if (!userProfile) {
    navigate('/onboarding');
    return null;
  }

  return <AccountPage user={userProfile} projects={projects.list} />;
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
          <Route path="/privacy" element={<PrivacyPolicy />} />
          <Route path="/terms" element={<TermsOfService />} />
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
