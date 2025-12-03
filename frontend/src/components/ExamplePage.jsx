import React from 'react';
import { Link } from 'react-router-dom';
import { Github, ArrowLeft, Eye } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import ProjectCard from './ProjectCard';

const ExamplePage = () => {
  // Example profile data
  const exampleProfile = {
    user: {
      name: 'John Doe',
      github: {
        username: 'johndoe',
        avatar_url: 'https://github.com/github.png' // Placeholder, you can use a real avatar URL
      }
    },
    projects: [
      {
        id: 'example-1',
        company: 'TechCorp',
        projectName: 'E-Commerce Platform Performance Optimization',
        role: 'Senior Backend Engineer',
        teamSize: 5,
        problem: 'API response times averaged 2.5s, causing 15% cart abandonment. Database queries were inefficient and caching strategy was outdated.',
        contributions: [
          'Refactored database queries using query optimization and indexing',
          'Implemented Redis caching layer for frequently accessed data',
          'Migrated critical endpoints to async processing with background jobs',
          'Added comprehensive monitoring and alerting for performance metrics'
        ],
        metrics: [
          {
            primary: '60%',
            label: 'Faster API',
            detail: '2.5s → 1.0s'
          },
          {
            primary: '40%',
            label: 'Less Abandonment',
            detail: '15% → 9%'
          },
          {
            primary: '3M',
            label: 'Daily Requests',
            detail: 'Handled'
          }
        ],
        techStack: ['Python', 'PostgreSQL', 'Redis', 'FastAPI', 'Docker', 'Kubernetes']
      },
      {
        id: 'example-2',
        company: 'StartupXYZ',
        projectName: 'Real-Time Analytics Dashboard',
        role: 'Full-Stack Developer',
        teamSize: 3,
        problem: 'Business team needed real-time insights but existing reports were static and updated daily. Manual data exports were time-consuming.',
        contributions: [
          'Built real-time data pipeline using Apache Kafka and stream processing',
          'Created interactive dashboard with live charts and filters',
          'Implemented WebSocket connections for instant data updates',
          'Designed responsive UI that works across all devices'
        ],
        metrics: [
          {
            primary: '10x',
            label: 'Faster Insights',
            detail: 'Daily → Real-time'
          },
          {
            primary: '85%',
            label: 'Time Saved',
            detail: 'Per week'
          },
          {
            primary: '50K',
            label: 'Daily Users',
            detail: 'Active'
          }
        ],
        techStack: ['React', 'Node.js', 'Kafka', 'PostgreSQL', 'WebSocket', 'D3.js']
      },
      {
        id: 'example-3',
        company: 'CloudScale Inc',
        projectName: 'Microservices Migration',
        role: 'DevOps Engineer',
        teamSize: 8,
        problem: 'Monolithic application couldn\'t scale, deployments took 4 hours, and single point of failure caused frequent outages.',
        contributions: [
          'Architected microservices architecture with 12 independent services',
          'Implemented CI/CD pipelines reducing deployment time by 90%',
          'Set up Kubernetes cluster with auto-scaling and health checks',
          'Created comprehensive monitoring and distributed tracing system'
        ],
        metrics: [
          {
            primary: '95%',
            label: 'Faster Deploy',
            detail: '4h → 12min'
          },
          {
            primary: '99.9%',
            label: 'Uptime',
            detail: 'Achieved'
          },
          {
            primary: '5x',
            label: 'Scale Capacity',
            detail: 'Increased'
          }
        ],
        techStack: ['Kubernetes', 'Docker', 'Jenkins', 'Prometheus', 'Grafana', 'Go']
      }
    ],
    view_count: 1247
  };

  return (
    <div className="min-h-screen bg-[#2d2d2d] text-terminal-text">
      <div className="p-10 max-w-[1200px] mx-auto">
        {/* Navigation */}
        <div className="mb-10 flex items-center justify-between">
          <Link to="/">
            <TerminalButton>
              <ArrowLeft size={16} className="inline mr-2" />
              [Back to Home]
            </TerminalButton>
          </Link>
          <div className="flex items-center gap-2 text-terminal-gray text-sm">
            <Eye size={14} />
            <span>{exampleProfile.view_count} views</span>
          </div>
        </div>

        {/* Example Badge */}
        <div className="mb-5 bg-terminal-orange/10 border border-terminal-orange/30 p-4 rounded">
          <div className="text-terminal-orange text-sm">
            &gt; This is an example profile showcasing how dev-impact displays developer impact.
            <Link to="/signup" className="underline ml-2 hover:text-terminal-orange-light">
              Create your own profile →
            </Link>
          </div>
        </div>

        {/* Profile Header */}
        <div className="border border-terminal-border p-10 mb-10">
          <div className="flex items-start gap-6">
            {exampleProfile.user.github?.avatar_url && (
              <img
                src={exampleProfile.user.github.avatar_url}
                alt={exampleProfile.user.name}
                className="w-24 h-24 rounded-full border-2 border-terminal-orange"
              />
            )}
            <div className="flex-1">
              <div className="text-[32px] mb-2.5 uppercase text-terminal-orange">
                {exampleProfile.user.name}
              </div>
              <div className="text-lg text-[#c9c5c0] mb-5">
                Developer Profile
              </div>
              {exampleProfile.user.github?.username && (
                <div className="mb-2.5 flex items-center text-terminal-gray">
                  <Github size={16} className="inline mr-2" />
                  <span>github.com/{exampleProfile.user.github.username}</span>
                </div>
              )}
              <div className="border-t border-terminal-border mt-5 pt-5 text-[#c9c5c0]">
                {exampleProfile.projects.length} {exampleProfile.projects.length === 1 ? 'Project' : 'Projects'}
                {' • '}
                {exampleProfile.projects.reduce((sum, p) => sum + (p.metrics?.length || 0), 0)} Achievements
              </div>
            </div>
          </div>
        </div>

        {/* Projects */}
        {exampleProfile.projects && exampleProfile.projects.length > 0 && (
          <div>
            <div className="text-lg mb-5">
              &gt; Projects ({exampleProfile.projects.length})
            </div>
            <div className="bg-terminal-bg-lighter border border-terminal-border p-5">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-start auto-rows-fr">
                {exampleProfile.projects.map(project => (
                  <div key={project.id} className="min-w-0 h-full">
                    <ProjectCard project={project} compact />
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-10 pt-5 border-t border-terminal-border text-center text-terminal-gray text-sm">
          <div>
            Example profile on dev-impact.io
          </div>
          <div className="mt-4 flex items-center justify-center gap-2">
            <span className="text-terminal-gray">Powered by</span>
            <Link to="/" className="inline-flex items-center gap-1 px-2 py-1 rounded bg-terminal-orange/10 border border-terminal-orange/30 hover:bg-terminal-orange/20 transition-colors">
              <span className="text-terminal-orange font-semibold">dev-impact</span>
            </Link>
          </div>
          <div className="mt-2">
            <Link to="/signup" className="text-terminal-orange hover:underline">
              Create your own developer profile
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExamplePage;

