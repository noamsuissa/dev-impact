import React from 'react';
import TerminalButton from './common/TerminalButton';
import { repeat, padLine, centerText } from '../utils/helpers';

const ProjectCard = ({ project, onEdit, onDelete, compact = false }) => {
  const maxWidth = compact ? 60 : 80;
  
  const padLineLocal = (text) => padLine(text, maxWidth);
  
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
      <div>{padLineLocal(`🏢 ${project.company}`)}</div>
      <div>{padLineLocal(project.projectName)}</div>
      <div>{padLineLocal(`${project.role} • Team of ${project.teamSize}`)}</div>
      <div>├{repeat('─', maxWidth)}┤</div>
      <div>{padLineLocal('')}</div>
      <div>{padLineLocal(`Problem: ${project.problem}`)}</div>
      <div>{padLineLocal('')}</div>
      <div>{padLineLocal('Solution:')}</div>
      {project.contributions.map((contrib, idx) => (
        <div key={idx}>{padLineLocal(`• ${contrib}`)}</div>
      ))}
      <div>{padLineLocal('')}</div>
      
      {combinedMetrics.map((line, idx) => (
        <div key={idx}>{line}</div>
      ))}
      
      <div>{padLineLocal('')}</div>
      <div>{padLineLocal(project.techStack.join(' • '))}</div>
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

export default ProjectCard;

