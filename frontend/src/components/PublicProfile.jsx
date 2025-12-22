import React, { useState, useEffect } from 'react';
import { useParams, Link, Navigate } from 'react-router-dom';
import { Github, Eye } from 'lucide-react';
import ProjectCard from './ProjectCard';
import ProjectModal from './ProjectModal';
import { useMetaTags } from '../hooks/useMetaTags';
import { generatePortfolioUrl } from '../utils/helpers';
import { useAuth } from '../hooks/useAuth';

const PublicProfile = () => {
  const { username: usernameFromPath, portfolioSlug: portfolioSlugFromPath } = useParams();
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [isProjectModalOpen, setIsProjectModalOpen] = useState(false);
  
  // Extract username and profile slug from subdomain/path
  const getUsernameAndSlug = () => {
    const hostname = window.location.hostname;
    const baseDomain = import.meta.env.VITE_BASE_DOMAIN || 'dev-impact.io';
    let username = null;
    let portfolioSlug = null;
    
    // Check if we're on a subdomain (production)
    if (hostname !== 'localhost' && 
        !hostname.match(/^\d+\.\d+\.\d+\.\d+$/) && 
        hostname.includes('.')) {
      const parts = hostname.split('.');
      const domainParts = baseDomain.split('.');
      const isSubdomain = parts.length > domainParts.length;
      
      if (isSubdomain && parts[0] && parts[0] !== 'www') {
        username = parts[0];
        // Extract profile slug from pathname (e.g., /profile-slug)
        const pathParts = window.location.pathname.split('/').filter(p => p);
        if (pathParts.length > 0) {
          portfolioSlug = pathParts[0];
        }
      }
    } else {
      // Localhost: extract from path (e.g., /username/profile-slug)
      username = usernameFromPath;
      portfolioSlug = portfolioSlugFromPath;
    }
    
    return { username, portfolioSlug };
  };
  
  const { username, portfolioSlug } = getUsernameAndSlug();

  // Get home URL - navigate to main domain if on subdomain
  const getHomeUrl = () => {
    const hostname = window.location.hostname;
    const baseDomain = import.meta.env.VITE_BASE_DOMAIN || 'dev-impact.io';
    
    // Check if we're on a subdomain
    if (hostname !== 'localhost' && 
        !hostname.match(/^\d+\.\d+\.\d+\.\d+$/) && 
        hostname.includes('.')) {
      const parts = hostname.split('.');
      const domainParts = baseDomain.split('.');
      const isSubdomain = parts.length > domainParts.length;
      
      if (isSubdomain && parts[0] && parts[0] !== 'www') {
        // We're on a subdomain, redirect to main domain
        const protocol = window.location.protocol;
        return `${protocol}//${baseDomain}/`;
      }
    }
    
    // Not on subdomain, use regular navigation
    return user ? "/dashboard" : "/";
  };

  const handleLogoClick = (e) => {
    const homeUrl = getHomeUrl();
    // If it's a full URL (subdomain case), use window.location
    if (homeUrl.startsWith('http')) {
      e.preventDefault();
      window.location.href = homeUrl;
    }
    // Otherwise, let Link handle it normally
  };

  // Dynamic meta tags for SEO and OpenGraph
  const profileUrl = username ? generatePortfolioUrl(username, portfolioSlug) : (() => {
    const baseDomain = import.meta.env.VITE_BASE_DOMAIN || 'dev-impact.io';
    return typeof window !== 'undefined' && window.location.hostname === 'localhost' 
      ? `http://localhost:${window.location.port || '5173'}/`
      : `https://${baseDomain}/`;
  })();
  const profileTitle = profile 
    ? `${profile.user.name}${profile.portfolio ? ` - ${profile.portfolio.name}` : ''} - Developer Profile | dev-impact` 
    : 'Developer Profile | dev-impact';
  const profileDescription = profile 
    ? `View ${profile.user.name}'s${profile.portfolio ? ` ${profile.portfolio.name}` : ''} developer profile on dev-impact. ${profile.projects.length} projects with ${profile.projects.reduce((sum, p) => sum + (p.metrics?.length || 0), 0)} achievements.`
    : 'View developer profile on dev-impact';
  
  // Use static OG image for all profiles
  const baseDomain = import.meta.env.VITE_BASE_DOMAIN || 'dev-impact.io';
  const profileImage = typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? `http://localhost:${window.location.port || '5173'}/og-image.png`
    : `https://${baseDomain}/og-image.png`;

  useMetaTags({
    title: profileTitle,
    description: profileDescription,
    image: profileImage,
    url: profileUrl,
    type: 'profile'
  });

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        setError(null);

        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        let url = `${apiUrl}/api/portfolios/${username}`;
        if (portfolioSlug) {
          url += `/${portfolioSlug}`;
        }
        
        const response = await fetch(url);

        if (!response.ok) {
          if (response.status === 404) {
            throw new Error('Profile not found');
          }
          throw new Error('Failed to load profile');
        }

        const data = await response.json();
        setProfile(data);
      } catch (err) {
        console.error('Error fetching profile:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (username) {
      fetchProfile();
    }
  }, [username, portfolioSlug]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#2d2d2d] text-terminal-text flex items-center justify-center">
        <div className="fade-in">
          <div>&gt; Loading profile...</div>
        </div>
      </div>
    );
  }

  // Redirect to 404 page if profile not found
  if (error) {
    return <Navigate to="/404" replace />;
  }

  if (!profile) {
    return null;
  }

  return (
    <div className="min-h-screen bg-[#2d2d2d] text-terminal-text">
      <div className="p-10 max-w-[1200px] mx-auto">
        {/* Navigation */}
        <div className="mb-10 flex items-center justify-between">
          <Link 
            to={user ? "/dashboard" : "/"}
            onClick={handleLogoClick}
            className="text-terminal-orange font-mono text-xl font-semibold hover:text-terminal-orange/80 transition-colors"
          >
            dev-impact
          </Link>
          <div className="flex items-center gap-2 text-terminal-gray text-sm">
            <Eye size={14} />
            <span>{profile.view_count || 0} views</span>
          </div>
        </div>

        {/* Profile Header */}
        <div className="border border-terminal-border p-10 mb-10">
          <div className="flex items-start gap-6">
            {profile.user.github?.avatar_url && (
              <img
                src={profile.user.github.avatar_url}
                alt={profile.user.name}
                className="w-24 h-24 rounded-full border-2 border-terminal-orange"
              />
            )}
            <div className="flex-1">
              <div className="text-[32px] mb-2.5 uppercase text-terminal-orange">
                {profile.user.name}
              </div>
              <div className="text-lg text-[#c9c5c0] mb-2">
                {profile.portfolio?.name || 'Developer Profile'}
              </div>
              {profile.portfolio?.description && (
                <div className="text-sm text-terminal-gray mb-5">
                  {profile.portfolio.description}
                </div>
              )}
              {!profile.portfolio?.description && <div className="mb-5"></div>}
              {profile.user.github?.username && (
                <div className="mb-2.5">
                  <a
                    href={`https://github.com/${profile.user.github.username}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-terminal-orange transition-colors"
                  >
                    <Github size={16} className="inline mr-2" />
                    github.com/{profile.user.github.username}
                  </a>
                </div>
              )}
              <div className="border-t border-terminal-border mt-5 pt-5 text-[#c9c5c0]">
                {profile.projects.length} {profile.projects.length === 1 ? 'Project' : 'Projects'}
                {' • '}
                {profile.projects.reduce((sum, p) => sum + (p.metrics?.length || 0), 0)} Achievements
              </div>
            </div>
          </div>
        </div>

        {/* Projects */}
        {profile.projects && profile.projects.length > 0 && (
          <div>
            <div className="text-lg mb-5">
              &gt; Projects ({profile.projects.length})
            </div>
            <div className="bg-terminal-bg-lighter border border-terminal-border p-5">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-start auto-rows-fr">
                {profile.projects.map(project => (
                  <div key={project.id} className="min-w-0 h-full">
                    <ProjectCard 
                      project={project} 
                      compact
                      onClick={(p) => {
                        setSelectedProject(p);
                        setIsProjectModalOpen(true);
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-10 pt-5 border-t border-terminal-border text-center text-terminal-gray text-sm">
          <div>
            Published on dev-impact.io
          </div>
          <div className="mt-4 flex items-center justify-center gap-2">
            <span className="text-terminal-gray">Powered by</span>
            <Link to="/" className="inline-flex items-center gap-1 px-2 py-1 rounded bg-terminal-orange/10 border border-terminal-orange/30 hover:bg-terminal-orange/20 transition-colors">
              <span className="text-terminal-orange font-semibold">dev-impact</span>
            </Link>
          </div>
          <div className="mt-2">
            <Link to="/" className="text-terminal-orange hover:underline">
              Create your own developer profile
            </Link>
          </div>
        </div>
      </div>

      {/* Project Modal (Read-only) */}
      <ProjectModal
        isOpen={isProjectModalOpen}
        onClose={() => {
          setIsProjectModalOpen(false);
          setSelectedProject(null);
        }}
        project={selectedProject}
        readOnly={true}
      />
    </div>
  );
};

export default PublicProfile;

