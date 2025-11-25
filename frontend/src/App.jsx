import React, { useState, useEffect } from 'react';
import { Camera, Github, Plus, Eye, Download, Edit, Trash2, ArrowLeft } from 'lucide-react';

// Terminal CSS styles
const terminalStyles = `
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
  
  * {
    box-sizing: border-box;
  }
  
  body {
    margin: 0;
    padding: 0;
    background: #0a0a0a;
    color: #00ff00;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
  }
  
  .terminal-glow {
    text-shadow: 0 0 5px #00ff00;
  }
  
  .terminal-button {
    background: transparent;
    border: 1px solid #00ff00;
    color: #00ff00;
    padding: 8px 16px;
    font-family: 'JetBrains Mono', monospace;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .terminal-button:hover {
    background: #00ff00;
    color: #0a0a0a;
    box-shadow: 0 0 10px #00ff00;
  }
  
  .terminal-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .terminal-input {
    background: #1a1a1a;
    border: 1px solid #00ff00;
    color: #00ff00;
    padding: 8px;
    font-family: 'JetBrains Mono', monospace;
    width: 100%;
    outline: none;
  }
  
  .terminal-input:focus {
    box-shadow: 0 0 5px #00ff00;
  }
  
  .terminal-card {
    background: #0a0a0a;
    border: 1px solid #00ff00;
    padding: 20px;
    margin: 20px 0;
  }
  
  .blink {
    animation: blink 1s infinite;
  }
  
  @keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
  }
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  
  .fade-in {
    animation: fadeIn 0.5s ease-in;
  }
`;

// Utility functions
const repeat = (char, times) => char.repeat(Math.max(0, times));

// Components
const TerminalButton = ({ children, onClick, disabled, className = '' }) => (
  <button 
    className={`terminal-button ${className}`}
    onClick={onClick}
    disabled={disabled}
  >
    {children}
  </button>
);

const TerminalInput = ({ value, onChange, placeholder, className = '' }) => (
  <input
    className={`terminal-input ${className}`}
    value={value}
    onChange={(e) => onChange(e.target.value)}
    placeholder={placeholder}
  />
);

// Landing Page Component
const LandingPage = ({ onStart }) => {
  const [lines, setLines] = useState([]);
  const [showButtons, setShowButtons] = useState(false);

  useEffect(() => {
    const bootSequence = [
      '> dev-impact v1.0.0',
      '> initializing system...',
      '> loading components...',
      '> ready.',
      '',
      'A new standard for developer resumes.',
      'Show real impact, not just bullet points.',
      ''
    ];

    bootSequence.forEach((line, i) => {
      setTimeout(() => {
        setLines(prev => [...prev, line]);
        if (i === bootSequence.length - 1) {
          setTimeout(() => setShowButtons(true), 500);
        }
      }, i * 300);
    });
  }, []);

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{ maxWidth: '600px', width: '100%' }}>
        {lines.map((line, i) => (
          <div key={i} className="fade-in" style={{ marginBottom: '10px' }}>
            {line}
          </div>
        ))}
        {showButtons && (
          <div className="fade-in" style={{ marginTop: '40px', display: 'flex', gap: '20px' }}>
            <TerminalButton onClick={onStart}>
              [Start Building]
            </TerminalButton>
            <TerminalButton onClick={() => alert('Example coming soon!')}>
              [View Example]
            </TerminalButton>
          </div>
        )}
      </div>
    </div>
  );
};

// Onboarding Component
const Onboarding = ({ onComplete }) => {
  const [step, setStep] = useState(0);
  const [name, setName] = useState('');
  const [github, setGithub] = useState('');

  const steps = [
    {
      prompt: '> Welcome to dev-impact',
      input: null
    },
    {
      prompt: "> Let's set up your profile...",
      input: null
    },
    {
      prompt: '> Your name:',
      input: 'name'
    },
    {
      prompt: '> GitHub username (optional):',
      input: 'github'
    }
  ];

  const handleNext = () => {
    if (step < steps.length - 1) {
      setStep(step + 1);
    } else {
      onComplete({ name, github });
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{ maxWidth: '600px', width: '100%' }}>
        {steps.slice(0, step + 1).map((s, i) => (
          <div key={i} className="fade-in" style={{ marginBottom: '20px' }}>
            <div style={{ marginBottom: '10px' }}>{s.prompt}</div>
            {i === step && s.input === 'name' && (
              <TerminalInput value={name} onChange={setName} placeholder="John Doe" />
            )}
            {i === step && s.input === 'github' && (
              <TerminalInput value={github} onChange={setGithub} placeholder="johndoe" />
            )}
            {i < step && s.input === 'name' && (
              <div style={{ color: '#00aa00' }}>{name}</div>
            )}
            {i < step && s.input === 'github' && (
              <div style={{ color: '#00aa00' }}>{github || '(skipped)'}</div>
            )}
          </div>
        ))}
        {step === steps.length - 1 && (
          <div className="fade-in" style={{ marginTop: '40px', display: 'flex', gap: '20px' }}>
            <TerminalButton onClick={handleNext}>
              [Continue]
            </TerminalButton>
            <TerminalButton onClick={() => onComplete({ name, github: '' })}>
              [Skip GitHub]
            </TerminalButton>
          </div>
        )}
        {step < steps.length - 1 && steps[step].input && (
          <div style={{ marginTop: '20px' }}>
            <TerminalButton onClick={handleNext}>
              [Next]
            </TerminalButton>
          </div>
        )}
        {step < steps.length - 1 && !steps[step].input && (
          <div style={{ marginTop: '20px' }}>
            <TerminalButton onClick={handleNext}>
              [Continue]
            </TerminalButton>
          </div>
        )}
      </div>
    </div>
  );
};

// Project Card Component
const ProjectCard = ({ project, onEdit, onDelete, compact = false }) => {
  const maxWidth = compact ? 60 : 80;
  
  const padLine = (text) => {
    const textStr = text.toString();
    return `│ ${textStr}${repeat(' ', maxWidth - textStr.length - 1)}│`;
  };
  
  const centerText = (text, width) => {
    const padding = Math.max(0, width - text.length);
    const leftPad = Math.floor(padding / 2);
    const rightPad = padding - leftPad;
    return repeat(' ', leftPad) + text + repeat(' ', rightPad);
  };
  
  const buildMetricCard = (metric) => {
    const cardWidth = 16;
    const lines = [];
    
    lines.push('┌' + repeat('─', cardWidth) + '┐');
    lines.push('│' + centerText(metric.primary, cardWidth) + '│');
    lines.push('│' + centerText(metric.label, cardWidth) + '│');
    
    if (metric.detail) {
      lines.push('├' + repeat('─', cardWidth) + '┤');
      lines.push('│' + centerText(metric.detail, cardWidth) + '│');
    }
    
    lines.push('└' + repeat('─', cardWidth) + '┘');
    
    return lines;
  };
  
  const metricCards = project.metrics.map(m => buildMetricCard(m));
  const maxMetricLines = Math.max(...metricCards.map(c => c.length), 0);
  
  const combinedMetrics = [];
  for (let i = 0; i < maxMetricLines; i++) {
    let line = '│ ';
    metricCards.forEach((card, idx) => {
      line += (card[i] || repeat(' ', 18));
      if (idx < metricCards.length - 1) line += '  ';
    });
    const currentLength = line.length - 2;
    line += repeat(' ', maxWidth - currentLength - 1) + '│';
    combinedMetrics.push(line);
  }

  return (
    <div style={{
      fontFamily: "'JetBrains Mono', 'Courier New', monospace",
      fontSize: compact ? '12px' : '14px',
      lineHeight: '1.5',
      color: '#00ff00',
      backgroundColor: '#0a0a0a',
      padding: '20px',
      whiteSpace: 'pre',
      border: '1px solid #00ff00',
      margin: '20px 0'
    }}>
      <div>┌{repeat('─', maxWidth)}┐</div>
      <div>{padLine(`🏢 ${project.company}`)}</div>
      <div>{padLine(project.projectName)}</div>
      <div>{padLine(`${project.role} • Team of ${project.teamSize}`)}</div>
      <div>├{repeat('─', maxWidth)}┤</div>
      <div>{padLine('')}</div>
      <div>{padLine(`Problem: ${project.problem}`)}</div>
      <div>{padLine('')}</div>
      <div>{padLine('Solution:')}</div>
      {project.contributions.map((contrib, idx) => (
        <div key={idx}>{padLine(`• ${contrib}`)}</div>
      ))}
      <div>{padLine('')}</div>
      
      {combinedMetrics.map((line, idx) => (
        <div key={idx}>{line}</div>
      ))}
      
      <div>{padLine('')}</div>
      <div>{padLine(project.techStack.join(' • '))}</div>
      <div>└{repeat('─', maxWidth)}┘</div>
      
      {(onEdit || onDelete) && (
        <div style={{ marginTop: '10px', display: 'flex', gap: '10px' }}>
          {onEdit && (
            <TerminalButton onClick={() => onEdit(project)}>
              [Edit]
            </TerminalButton>
          )}
          {onDelete && (
            <TerminalButton onClick={() => onDelete(project.id)}>
              [Delete]
            </TerminalButton>
          )}
        </div>
      )}
    </div>
  );
};

// Dashboard Component
const Dashboard = ({ user, projects, onAddProject, onEditProject, onDeleteProject, onViewProfile }) => {
  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '40px' }}>
        <div style={{ fontSize: '24px', marginBottom: '10px' }}>
          &gt; {user.name}@dev-impact:~$
        </div>
        {user.github && (
          <div style={{ color: '#00aa00' }}>
            Connected to GitHub: @{user.github}
          </div>
        )}
      </div>

      <div style={{ marginBottom: '40px' }}>
        <div style={{ fontSize: '18px', marginBottom: '20px' }}>
          &gt; Actions
        </div>
        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
          <TerminalButton onClick={onAddProject}>
            <Plus size={16} style={{ display: 'inline', marginRight: '8px' }} />
            [Add Project]
          </TerminalButton>
          <TerminalButton onClick={onViewProfile}>
            <Eye size={16} style={{ display: 'inline', marginRight: '8px' }} />
            [Preview Profile]
          </TerminalButton>
          <TerminalButton onClick={() => alert('Export coming soon!')}>
            <Download size={16} style={{ display: 'inline', marginRight: '8px' }} />
            [Export]
          </TerminalButton>
        </div>
      </div>

      <div>
        <div style={{ fontSize: '18px', marginBottom: '20px' }}>
          &gt; Your Projects ({projects.length})
        </div>
        {projects.length === 0 ? (
          <div style={{ color: '#00aa00', marginBottom: '20px' }}>
            No projects yet. Add your first project to get started!
          </div>
        ) : (
          projects.map(project => (
            <ProjectCard
              key={project.id}
              project={project}
              onEdit={onEditProject}
              onDelete={onDeleteProject}
              compact
            />
          ))
        )}
      </div>
    </div>
  );
};

// Project Builder Component
const ProjectBuilder = ({ onSave, onCancel, editProject = null }) => {
  const [company, setCompany] = useState(editProject?.company || '');
  const [projectName, setProjectName] = useState(editProject?.projectName || '');
  const [role, setRole] = useState(editProject?.role || '');
  const [teamSize, setTeamSize] = useState(editProject?.teamSize || '');
  const [problem, setProblem] = useState(editProject?.problem || '');
  const [contributions, setContributions] = useState(editProject?.contributions || ['']);
  const [metrics, setMetrics] = useState(editProject?.metrics || []);
  const [techStack, setTechStack] = useState(editProject?.techStack || []);
  const [newTech, setNewTech] = useState('');

  const addContribution = () => {
    setContributions([...contributions, '']);
  };

  const updateContribution = (index, value) => {
    const updated = [...contributions];
    updated[index] = value;
    setContributions(updated);
  };

  const removeContribution = (index) => {
    setContributions(contributions.filter((_, i) => i !== index));
  };

  const addMetric = () => {
    setMetrics([...metrics, { primary: '', label: '', detail: '' }]);
  };

  const updateMetric = (index, field, value) => {
    const updated = [...metrics];
    updated[index][field] = value;
    setMetrics(updated);
  };

  const removeMetric = (index) => {
    setMetrics(metrics.filter((_, i) => i !== index));
  };

  const addTech = () => {
    if (newTech.trim() && !techStack.includes(newTech.trim())) {
      setTechStack([...techStack, newTech.trim()]);
      setNewTech('');
    }
  };

  const removeTech = (tech) => {
    setTechStack(techStack.filter(t => t !== tech));
  };

  const handleSave = () => {
    const project = {
      id: editProject?.id || Date.now().toString(),
      company,
      projectName,
      role,
      teamSize: parseInt(teamSize) || 1,
      problem,
      contributions: contributions.filter(c => c.trim()),
      metrics: metrics.filter(m => m.primary && m.label),
      techStack
    };
    onSave(project);
  };

  const isValid = company && projectName && role && teamSize && problem && 
                  contributions.some(c => c.trim()) && techStack.length > 0;

  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ marginBottom: '40px', display: 'flex', alignItems: 'center', gap: '20px' }}>
        <TerminalButton onClick={onCancel}>
          <ArrowLeft size={16} style={{ display: 'inline', marginRight: '8px' }} />
          [Back]
        </TerminalButton>
        <div style={{ fontSize: '20px' }}>
          &gt; {editProject ? 'Edit' : 'New'} Project
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <div style={{ marginBottom: '8px' }}>&gt; Company:</div>
        <TerminalInput value={company} onChange={setCompany} placeholder="TechCorp" />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <div style={{ marginBottom: '8px' }}>&gt; Project Name:</div>
        <TerminalInput value={projectName} onChange={setProjectName} placeholder="Real-time Analytics Dashboard" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
        <div>
          <div style={{ marginBottom: '8px' }}>&gt; Your Role:</div>
          <TerminalInput value={role} onChange={setRole} placeholder="Senior Frontend Engineer" />
        </div>
        <div>
          <div style={{ marginBottom: '8px' }}>&gt; Team Size:</div>
          <TerminalInput value={teamSize} onChange={setTeamSize} placeholder="5" />
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <div style={{ marginBottom: '8px' }}>&gt; Problem (one line):</div>
        <TerminalInput value={problem} onChange={setProblem} placeholder="5min dashboard load blocking marketing team" />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <div style={{ marginBottom: '8px' }}>&gt; Your Solution (3-5 bullets):</div>
        {contributions.map((contrib, i) => (
          <div key={i} style={{ marginBottom: '10px', display: 'flex', gap: '10px' }}>
            <TerminalInput 
              value={contrib} 
              onChange={(val) => updateContribution(i, val)} 
              placeholder="WebSocket-based real-time updates" 
            />
            <TerminalButton onClick={() => removeContribution(i)}>
              [-]
            </TerminalButton>
          </div>
        ))}
        <TerminalButton onClick={addContribution}>
          [+ Add Bullet]
        </TerminalButton>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <div style={{ marginBottom: '8px' }}>&gt; Impact Metrics:</div>
        {metrics.map((metric, i) => (
          <div key={i} style={{ 
            border: '1px solid #00ff00', 
            padding: '15px', 
            marginBottom: '10px' 
          }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '10px' }}>
              <div>
                <div style={{ marginBottom: '5px', fontSize: '12px' }}>Value:</div>
                <TerminalInput 
                  value={metric.primary} 
                  onChange={(val) => updateMetric(i, 'primary', val)} 
                  placeholder="96%" 
                />
              </div>
              <div>
                <div style={{ marginBottom: '5px', fontSize: '12px' }}>Label:</div>
                <TerminalInput 
                  value={metric.label} 
                  onChange={(val) => updateMetric(i, 'label', val)} 
                  placeholder="faster" 
                />
              </div>
            </div>
            <div style={{ marginBottom: '10px' }}>
              <div style={{ marginBottom: '5px', fontSize: '12px' }}>Detail (optional):</div>
              <TerminalInput 
                value={metric.detail} 
                onChange={(val) => updateMetric(i, 'detail', val)} 
                placeholder="5min→2sec" 
              />
            </div>
            <TerminalButton onClick={() => removeMetric(i)}>
              [Remove Metric]
            </TerminalButton>
          </div>
        ))}
        <TerminalButton onClick={addMetric}>
          [+ Add Metric]
        </TerminalButton>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <div style={{ marginBottom: '8px' }}>&gt; Tech Stack:</div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '10px' }}>
          {techStack.map(tech => (
            <div key={tech} style={{ 
              border: '1px solid #00ff00', 
              padding: '5px 10px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              {tech}
              <button 
                onClick={() => removeTech(tech)}
                style={{ 
                  background: 'none', 
                  border: 'none', 
                  color: '#00ff00', 
                  cursor: 'pointer',
                  padding: '0'
                }}
              >
                ×
              </button>
            </div>
          ))}
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <TerminalInput 
            value={newTech} 
            onChange={setNewTech} 
            placeholder="React" 
          />
          <TerminalButton onClick={addTech}>
            [Add]
          </TerminalButton>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '20px', marginTop: '40px' }}>
        <TerminalButton onClick={handleSave} disabled={!isValid}>
          [Save Project]
        </TerminalButton>
        <TerminalButton onClick={onCancel}>
          [Cancel]
        </TerminalButton>
      </div>
    </div>
  );
};

// Profile View Component
const ProfileView = ({ user, projects, onBack }) => {
  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '40px', display: 'flex', alignItems: 'center', gap: '20px' }}>
        <TerminalButton onClick={onBack}>
          <ArrowLeft size={16} style={{ display: 'inline', marginRight: '8px' }} />
          [Back to Dashboard]
        </TerminalButton>
      </div>

      <div style={{ 
        border: '1px solid #00ff00',
        padding: '40px',
        marginBottom: '40px'
      }}>
        <div style={{ fontSize: '32px', marginBottom: '10px', textTransform: 'uppercase' }}>
          {user.name}
        </div>
        <div style={{ fontSize: '18px', color: '#00aa00', marginBottom: '20px' }}>
          Developer Profile
        </div>
        {user.github && (
          <div style={{ marginBottom: '10px' }}>
            <Github size={16} style={{ display: 'inline', marginRight: '8px' }} />
            github.com/{user.github}
          </div>
        )}
        <div style={{ 
          borderTop: '1px solid #00ff00',
          marginTop: '20px',
          paddingTop: '20px'
        }}>
          {projects.length} {projects.length === 1 ? 'Project' : 'Projects'} • 
          {' '}{projects.reduce((sum, p) => sum + p.metrics.length, 0)} Achievements
        </div>
      </div>

      {projects.map(project => (
        <ProjectCard key={project.id} project={project} />
      ))}
    </div>
  );
};

// Main App Component
export default function App() {
  const [page, setPage] = useState('landing'); // landing, onboarding, dashboard, builder, profile
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
    <>
      <style>{terminalStyles}</style>
      <div style={{ minHeight: '100vh', background: '#0a0a0a' }}>
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
      </div>
    </>
  );
}