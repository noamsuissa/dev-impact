import React, { useState } from 'react';
import { ArrowLeft, Download, FileText, Code, FileJson, Globe } from 'lucide-react';
import TerminalButton from './common/TerminalButton';

const ExportPage = ({ user, projects, onBack }) => {
  const [selectedFormat, setSelectedFormat] = useState(null);
  const [exportStatus, setExportStatus] = useState('');

  const exportFormats = [
    {
      id: 'pdf',
      name: 'PDF Document',
      icon: FileText,
      description: 'Professional PDF resume',
      color: '#ff8c42'
    },
    {
      id: 'markdown',
      name: 'Markdown',
      icon: FileText,
      description: 'GitHub-flavored markdown',
      color: '#e8e6e3'
    },
    {
      id: 'json',
      name: 'JSON',
      icon: FileJson,
      description: 'Structured data export',
      color: '#e8e6e3'
    },
    {
      id: 'html',
      name: 'HTML',
      icon: Globe,
      description: 'Standalone web page',
      color: '#e8e6e3'
    },
    {
      id: 'text',
      name: 'Plain Text',
      icon: Code,
      description: 'ASCII art version',
      color: '#e8e6e3'
    }
  ];

  const handleExport = (format) => {
    setSelectedFormat(format);
    setExportStatus('Preparing export...');

    setTimeout(() => {
      switch (format) {
        case 'json':
          exportJSON();
          break;
        case 'markdown':
          exportMarkdown();
          break;
        case 'html':
          exportHTML();
          break;
        case 'text':
          exportText();
          break;
        case 'pdf':
          setExportStatus('PDF export coming soon!');
          setTimeout(() => setExportStatus(''), 2000);
          break;
        default:
          setExportStatus('');
      }
    }, 500);
  };

  const exportJSON = () => {
    const data = {
      user,
      projects,
      exportedAt: new Date().toISOString()
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    downloadFile(blob, `${user.name.replace(/\s+/g, '-')}-profile.json`);
    setExportStatus('✓ JSON exported successfully!');
    setTimeout(() => setExportStatus(''), 2000);
  };

  const exportMarkdown = () => {
    let md = `# ${user.name}\n\n`;
    if (user.github) {
      md += `GitHub: [@${user.github}](https://github.com/${user.github})\n\n`;
    }
    md += `---\n\n`;

    projects.forEach(project => {
      md += `## ${project.projectName}\n\n`;
      md += `**${project.company}** | ${project.role} | Team of ${project.teamSize}\n\n`;
      md += `### Problem\n${project.problem}\n\n`;
      md += `### Solution\n`;
      project.contributions.forEach(contrib => {
        md += `- ${contrib}\n`;
      });
      md += `\n### Impact\n`;
      project.metrics.forEach(metric => {
        md += `- **${metric.primary}** ${metric.label}`;
        if (metric.detail) md += ` (${metric.detail})`;
        md += `\n`;
      });
      md += `\n### Tech Stack\n${project.techStack.join(' • ')}\n\n`;
      md += `---\n\n`;
    });

    const blob = new Blob([md], { type: 'text/markdown' });
    downloadFile(blob, `${user.name.replace(/\s+/g, '-')}-profile.md`);
    setExportStatus('✓ Markdown exported successfully!');
    setTimeout(() => setExportStatus(''), 2000);
  };

  const exportHTML = () => {
    let html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${user.name} - Developer Profile</title>
  <style>
    body { 
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
      max-width: 900px; 
      margin: 40px auto; 
      padding: 20px;
      background: #2d2d2d;
      color: #e8e6e3;
    }
    h1 { color: #ff8c42; margin-bottom: 10px; }
    h2 { color: #ff8c42; border-bottom: 2px solid #5a5a5a; padding-bottom: 10px; }
    .project { 
      background: #3a3a3a; 
      padding: 20px; 
      margin: 20px 0; 
      border: 1px solid #5a5a5a;
      border-radius: 8px;
    }
    .metrics { display: flex; gap: 15px; flex-wrap: wrap; margin: 15px 0; }
    .metric { 
      background: #2d2d2d; 
      padding: 15px; 
      border: 1px solid #5a5a5a;
      border-radius: 4px;
      text-align: center;
    }
    .metric-value { font-size: 24px; font-weight: bold; color: #ff8c42; }
    .tech-stack { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }
    .tech { 
      background: #2d2d2d; 
      padding: 5px 12px; 
      border: 1px solid #ff8c42;
      border-radius: 4px;
      font-size: 14px;
    }
    ul { margin: 10px 0; }
    li { margin: 8px 0; }
  </style>
</head>
<body>
  <h1>${user.name}</h1>
  ${user.github ? `<p>GitHub: <a href="https://github.com/${user.github}" style="color: #ff8c42;">@${user.github}</a></p>` : ''}
  <hr style="border: 1px solid #5a5a5a; margin: 20px 0;">
`;

    projects.forEach(project => {
      html += `
  <div class="project">
    <h2>${project.projectName}</h2>
    <p><strong>${project.company}</strong> | ${project.role} | Team of ${project.teamSize}</p>
    <h3>Problem</h3>
    <p>${project.problem}</p>
    <h3>Solution</h3>
    <ul>
      ${project.contributions.map(c => `<li>${c}</li>`).join('\n      ')}
    </ul>
    <h3>Impact</h3>
    <div class="metrics">
      ${project.metrics.map(m => `
      <div class="metric">
        <div class="metric-value">${m.primary}</div>
        <div>${m.label}</div>
        ${m.detail ? `<div style="font-size: 12px; margin-top: 5px;">${m.detail}</div>` : ''}
      </div>
      `).join('')}
    </div>
    <h3>Tech Stack</h3>
    <div class="tech-stack">
      ${project.techStack.map(tech => `<span class="tech">${tech}</span>`).join('\n      ')}
    </div>
  </div>
`;
    });

    html += `
</body>
</html>`;

    const blob = new Blob([html], { type: 'text/html' });
    downloadFile(blob, `${user.name.replace(/\s+/g, '-')}-profile.html`);
    setExportStatus('✓ HTML exported successfully!');
    setTimeout(() => setExportStatus(''), 2000);
  };

  const exportText = () => {
    const width = 80;
    
    let text = `${'='.repeat(width)}\n`;
    text += `  ${user.name.toUpperCase()}\n`;
    if (user.github) {
      text += `  GitHub: @${user.github}\n`;
    }
    text += `${'='.repeat(width)}\n\n`;

    projects.forEach(project => {
      text += `┌${'─'.repeat(width - 2)}┐\n`;
      text += `│ ${project.projectName.padEnd(width - 4)} │\n`;
      text += `│ ${project.company.padEnd(width - 4)} │\n`;
      text += `│ ${`${project.role} • Team of ${project.teamSize}`.padEnd(width - 4)} │\n`;
      text += `├${'─'.repeat(width - 2)}┤\n`;
      text += `│ ${''.padEnd(width - 4)} │\n`;
      text += `│ Problem: ${project.problem.padEnd(width - 12)} │\n`;
      text += `│ ${''.padEnd(width - 4)} │\n`;
      text += `│ Solution:${' '.repeat(width - 13)}│\n`;
      project.contributions.forEach(contrib => {
        text += `│ • ${contrib.padEnd(width - 6)} │\n`;
      });
      text += `│ ${''.padEnd(width - 4)} │\n`;
      text += `│ Impact:${' '.repeat(width - 11)}│\n`;
      project.metrics.forEach(metric => {
        const metricText = `${metric.primary} ${metric.label}${metric.detail ? ` (${metric.detail})` : ''}`;
        text += `│   ${metricText.padEnd(width - 6)} │\n`;
      });
      text += `│ ${''.padEnd(width - 4)} │\n`;
      text += `│ ${project.techStack.join(' • ').padEnd(width - 4)} │\n`;
      text += `└${'─'.repeat(width - 2)}┘\n\n`;
    });

    const blob = new Blob([text], { type: 'text/plain' });
    downloadFile(blob, `${user.name.replace(/\s+/g, '-')}-profile.txt`);
    setExportStatus('✓ Text exported successfully!');
    setTimeout(() => setExportStatus(''), 2000);
  };

  const downloadFile = (blob, filename) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ padding: '40px', maxWidth: '1000px', margin: '0 auto' }}>
      <div style={{ marginBottom: '40px', display: 'flex', alignItems: 'center', gap: '20px' }}>
        <TerminalButton onClick={onBack}>
          <ArrowLeft size={16} style={{ display: 'inline', marginRight: '8px' }} />
          [Back]
        </TerminalButton>
      </div>

      <div style={{ marginBottom: '30px' }}>
        <div style={{ fontSize: '16px', marginBottom: '10px', color: '#c9c5c0' }}>
          Export your profile in different formats:
        </div>
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '20px',
        marginBottom: '30px'
      }}>
        {exportFormats.map(format => {
          const Icon = format.icon;
          return (
            <div
              key={format.id}
              style={{
                background: '#3a3a3a',
                border: `2px solid ${selectedFormat === format.id ? '#ff8c42' : '#5a5a5a'}`,
                padding: '25px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                position: 'relative'
              }}
              onClick={() => handleExport(format.id)}
              onMouseEnter={(e) => {
                if (selectedFormat !== format.id) {
                  e.currentTarget.style.borderColor = '#ff8c42';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedFormat !== format.id) {
                  e.currentTarget.style.borderColor = '#5a5a5a';
                }
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '10px' }}>
                <Icon size={28} color={format.color} />
                <div style={{ fontSize: '18px', fontWeight: '500' }}>
                  {format.name}
                </div>
              </div>
              <div style={{ color: '#c9c5c0', fontSize: '14px' }}>
                {format.description}
              </div>
              <div style={{ 
                position: 'absolute', 
                top: '15px', 
                right: '15px',
                opacity: 0.5
              }}>
                <Download size={20} />
              </div>
            </div>
          );
        })}
      </div>

      {exportStatus && (
        <div style={{
          background: exportStatus.includes('✓') ? '#3a3a3a' : '#3a3a3a',
          border: `1px solid ${exportStatus.includes('✓') ? '#ff8c42' : '#5a5a5a'}`,
          padding: '15px 20px',
          color: exportStatus.includes('✓') ? '#ff8c42' : '#e8e6e3',
          textAlign: 'center',
          fontSize: '14px'
        }}>
          {exportStatus}
        </div>
      )}

      <div style={{ 
        marginTop: '40px',
        padding: '20px',
        background: '#3a3a3a',
        border: '1px solid #5a5a5a'
      }}>
        <div style={{ fontSize: '14px', color: '#c9c5c0', marginBottom: '10px' }}>
          &gt; Export Information
        </div>
        <ul style={{ color: '#e8e6e3', fontSize: '13px', lineHeight: '1.8' }}>
          <li><strong>JSON:</strong> Perfect for importing into other tools or backing up your data</li>
          <li><strong>Markdown:</strong> Great for GitHub READMEs and documentation</li>
          <li><strong>HTML:</strong> Standalone webpage you can host or share</li>
          <li><strong>Plain Text:</strong> ASCII art format that maintains the terminal aesthetic</li>
          <li><strong>PDF:</strong> Professional format for traditional applications (coming soon)</li>
        </ul>
      </div>
    </div>
  );
};

export default ExportPage;

