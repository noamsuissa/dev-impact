import React, { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import TerminalInput from './common/TerminalInput';

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

export default ProjectBuilder;

