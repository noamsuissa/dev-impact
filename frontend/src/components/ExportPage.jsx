import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Download, FileText, Code, FileJson, Globe } from 'lucide-react';
import TerminalButton from './common/TerminalButton';

const ExportPage = ({ user, projects }) => {
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
    const githubUsername = user.github?.username || '';
    let md = `# ${user.name}\n\n`;
    if (githubUsername) {
      md += `GitHub: [@${githubUsername}](https://github.com/${githubUsername})\n\n`;
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
    const githubUsername = user.github?.username || '';
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
  ${githubUsername ? `<p>GitHub: <a href="https://github.com/${githubUsername}" style="color: #ff8c42;">@${githubUsername}</a></p>` : ''}
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
    const githubUsername = user.github?.username || '';
    const width = 80;
    
    let text = `${'='.repeat(width)}\n`;
    text += `  ${user.name.toUpperCase()}\n`;
    if (githubUsername) {
      text += `  GitHub: @${githubUsername}\n`;
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
    <div className="p-10 max-w-[1000px] mx-auto">
      <div className="mb-10 flex items-center gap-5">
        <Link to="/dashboard">
          <TerminalButton>
            <ArrowLeft size={16} className="inline mr-2" />
            [Back]
          </TerminalButton>
        </Link>
      </div>

      <div className="mb-8">
        <div className="text-base mb-2.5 text-[#c9c5c0]">
          Export your profile in different formats:
        </div>
      </div>

      <div className="grid grid-cols-[repeat(auto-fit,minmax(280px,1fr))] gap-5 mb-8">
        {exportFormats.map(format => {
          const Icon = format.icon;
          return (
            <div
              key={format.id}
              className={`bg-terminal-bg-lighter border-2 p-6 cursor-pointer transition-all duration-200 relative hover:border-terminal-orange ${
                selectedFormat === format.id ? 'border-terminal-orange' : 'border-terminal-border'
              }`}
              onClick={() => handleExport(format.id)}
            >
              <div className="flex items-center gap-4 mb-2.5">
                <Icon size={28} color={format.color} />
                <div className="text-lg font-medium">
                  {format.name}
                </div>
              </div>
              <div className="text-[#c9c5c0] text-sm">
                {format.description}
              </div>
              <div className="absolute top-4 right-4 opacity-50">
                <Download size={20} />
              </div>
            </div>
          );
        })}
      </div>

      {exportStatus && (
        <div className={`bg-terminal-bg-lighter border ${
          exportStatus.includes('✓') ? 'border-terminal-orange text-terminal-orange' : 'border-terminal-border text-terminal-text'
        } py-4 px-5 text-center text-sm`}>
          {exportStatus}
        </div>
      )}

      <div className="mt-10 p-5 bg-terminal-bg-lighter border border-terminal-border">
        <div className="text-sm text-[#c9c5c0] mb-2.5">
          &gt; Export Information
        </div>
        <ul className="text-terminal-text text-[13px] leading-relaxed">
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

