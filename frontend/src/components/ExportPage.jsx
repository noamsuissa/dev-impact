import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Download, FileText, Code, FileJson, Globe } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import PortfolioSelectionModal from './PortfolioSelectionModal';
import { useDashboard } from '../hooks/useDashboard';
import { isLegacyMetric, formatMetricValue, formatComparison } from '../utils/metrics';
import { wrapText } from '../utils/helpers';
import jsPDF from 'jspdf';

const ExportPage = ({ user, projects }) => {
  const { portfolios } = useDashboard();
  const [selectedFormat, setSelectedFormat] = useState(null);
  const [exportStatus, setExportStatus] = useState('');
  const [isPortfolioModalOpen, setIsPortfolioModalOpen] = useState(false);

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
          // Show portfolio selection modal first
          if (portfolios.list.length === 0) {
            setExportStatus('Please create a portfolio first before exporting to PDF.');
            setTimeout(() => setExportStatus(''), 3000);
          } else {
            setIsPortfolioModalOpen(true);
          }
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
    const contentWidth = width - 4; // Width for content inside borders (│ ... │)

    // Helper function to format a line within borders
    const formatLine = (content) => {
      const padded = content.padEnd(contentWidth);
      return `│ ${padded} │`;
    };

    let text = `${'='.repeat(width)}\n`;
    text += `  ${user.name.toUpperCase()}\n`;
    if (githubUsername) {
      text += `  GitHub: @${githubUsername}\n`;
    }
    text += `${'='.repeat(width)}\n\n`;

    projects.forEach(project => {
      // Top border
      text += `┌${'─'.repeat(width - 2)}┐\n`;

      // Project name (wrapped if needed)
      const projectNameLines = wrapText(project.projectName || 'Untitled Project', contentWidth);
      projectNameLines.forEach(line => {
        text += formatLine(line) + '\n';
      });

      // Company (wrapped if needed)
      const companyLines = wrapText(project.company || '', contentWidth);
      companyLines.forEach(line => {
        text += formatLine(line) + '\n';
      });

      // Role and team size
      const roleText = `${project.role || ''} • Team of ${project.teamSize || 1}`;
      const roleLines = wrapText(roleText, contentWidth);
      roleLines.forEach(line => {
        text += formatLine(line) + '\n';
      });

      // Divider
      text += `├${'─'.repeat(width - 2)}┤\n`;
      text += formatLine('') + '\n';

      // Problem
      text += formatLine('Problem:') + '\n';
      const problemLines = wrapText(project.problem || '', contentWidth);
      problemLines.forEach(line => {
        text += formatLine(line) + '\n';
      });
      text += formatLine('') + '\n';

      // Solution
      text += formatLine('Solution:') + '\n';
      if (project.contributions && project.contributions.length > 0) {
        project.contributions.forEach(contrib => {
          const contribLines = wrapText(contrib, contentWidth - 2); // -2 for "• "
          contribLines.forEach((line, idx) => {
            const prefix = idx === 0 ? '• ' : '  ';
            text += formatLine(prefix + line) + '\n';
          });
        });
      }
      text += formatLine('') + '\n';

      // Impact
      text += formatLine('Impact:') + '\n';
      if (project.metrics && project.metrics.length > 0) {
        project.metrics.forEach(metric => {
          let metricText = '';
          if (isLegacyMetric(metric)) {
            // Legacy format
            metricText = `${metric.primary} ${metric.label || ''}`;
            if (metric.detail) {
              metricText += ` (${metric.detail})`;
            }
          } else if (metric.type && metric.primary && typeof metric.primary === 'object') {
            // Standardized format
            const primaryValue = formatMetricValue(metric.primary.value, metric.primary.unit);
            metricText = `${primaryValue} ${metric.primary.label || ''}`;
            if (metric.comparison) {
              const comparisonStr = formatComparison(metric.comparison);
              if (comparisonStr) {
                metricText += ` (${comparisonStr})`;
              }
            }
            if (metric.timeframe) {
              metricText += ` - ${metric.timeframe}`;
            }
          }
          if (metricText) {
            const metricLines = wrapText(metricText, contentWidth - 2); // -2 for "  "
            metricLines.forEach((line, idx) => {
              const prefix = idx === 0 ? '  ' : '    ';
              text += formatLine(prefix + line) + '\n';
            });
          }
        });
      }
      text += formatLine('') + '\n';

      // Tech Stack
      const techStackText = project.techStack && project.techStack.length > 0
        ? project.techStack.join(' • ')
        : '';
      if (techStackText) {
        const techStackLines = wrapText(techStackText, contentWidth);
        techStackLines.forEach(line => {
          text += formatLine(line) + '\n';
        });
      }

      // Bottom border
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

  const exportPDF = (selectedPortfolio) => {
    try {
      setExportStatus('Generating PDF...');

      // Filter projects for the selected portfolio
      const portfolioProjects = projects.filter(p => {
        const pid = p.portfolio_id;
        return pid && pid === selectedPortfolio.id;
      });

      // Create new PDF document
      const doc = new jsPDF();
      let yPosition = 20;
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const margin = 20;
      const maxWidth = pageWidth - (margin * 2);

      // Helper function to add a new page if needed
      const checkPageBreak = (requiredSpace = 20) => {
        if (yPosition + requiredSpace > pageHeight - margin) {
          doc.addPage();
          yPosition = margin;
        }
      };

      // Helper function to add text with word wrapping
      const addWrappedText = (text, fontSize, isBold = false, color = [0, 0, 0]) => {
        doc.setFontSize(fontSize);
        doc.setTextColor(color[0], color[1], color[2]);
        if (isBold) {
          doc.setFont(undefined, 'bold');
        } else {
          doc.setFont(undefined, 'normal');
        }

        const lines = doc.splitTextToSize(text, maxWidth);
        lines.forEach((line) => {
          checkPageBreak(10);
          doc.text(line, margin, yPosition);
          yPosition += 7;
        });
        return lines.length * 7;
      };

      // Title
      doc.setFontSize(24);
      doc.setTextColor(255, 140, 66); // Terminal orange
      doc.setFont(undefined, 'bold');
      doc.text(user.name || 'Developer Profile', margin, yPosition);
      yPosition += 15;

      // Contact Information Section (no username, no duplicate name)
      doc.setFontSize(11);
      doc.setTextColor(0, 0, 0);
      doc.setFont(undefined, 'normal');

      // Email
      if (user.email) {
        checkPageBreak(10);
        doc.text(user.email, margin, yPosition);
        yPosition += 7;
      }

      // Location
      if (user.city || user.country) {
        checkPageBreak(10);
        const location = [user.city, user.country].filter(Boolean).join(', ');
        doc.text(location, margin, yPosition);
        yPosition += 7;
      }

      // GitHub
      if (user.github?.username) {
        checkPageBreak(10);
        doc.text(`GitHub: @${user.github.username}`, margin, yPosition);
        yPosition += 7;
      }

      yPosition += 10;

      // Portfolio Information
      if (selectedPortfolio) {
        checkPageBreak(20);
        doc.setFontSize(16);
        doc.setTextColor(255, 140, 66);
        doc.setFont(undefined, 'bold');
        doc.text('Portfolio', margin, yPosition);
        yPosition += 10;

        doc.setFontSize(11);
        doc.setTextColor(0, 0, 0);
        doc.setFont(undefined, 'normal');

        if (selectedPortfolio.name) {
          checkPageBreak(10);
          doc.text(`Portfolio Name: ${selectedPortfolio.name}`, margin, yPosition);
          yPosition += 7;
        }

        if (selectedPortfolio.description) {
          checkPageBreak(15);
          addWrappedText(`Description: ${selectedPortfolio.description}`, 11, false, [0, 0, 0]);
          yPosition += 5;
        }

        yPosition += 5;
      }

      // Projects Section
      if (portfolioProjects.length > 0) {
        checkPageBreak(20);
        doc.setFontSize(16);
        doc.setTextColor(255, 140, 66);
        doc.setFont(undefined, 'bold');
        doc.text('Projects', margin, yPosition);
        yPosition += 10;

        portfolioProjects.forEach((project, index) => {
          checkPageBreak(50);

          // Project Title
          doc.setFontSize(14);
          doc.setTextColor(255, 140, 66);
          doc.setFont(undefined, 'bold');
          doc.text(project.projectName || 'Untitled Project', margin, yPosition);
          yPosition += 10;

          doc.setFontSize(11);
          doc.setTextColor(0, 0, 0);
          doc.setFont(undefined, 'normal');

          // Company, Role, Team Size
          const projectMeta = [
            project.company && `Company: ${project.company}`,
            project.role && `Role: ${project.role}`,
            project.teamSize && `Team Size: ${project.teamSize}`
          ].filter(Boolean).join(' | ');

          if (projectMeta) {
            checkPageBreak(10);
            doc.text(projectMeta, margin, yPosition);
            yPosition += 7;
          }

          // Problem
          if (project.problem) {
            checkPageBreak(15);
            doc.setFont(undefined, 'bold');
            doc.text('Problem:', margin, yPosition);
            yPosition += 7;
            doc.setFont(undefined, 'normal');
            addWrappedText(project.problem, 11, false, [0, 0, 0]);
            yPosition += 3;
          }

          // Contributions/Solution
          if (project.contributions && project.contributions.length > 0) {
            checkPageBreak(15);
            doc.setFont(undefined, 'bold');
            doc.text('Solution:', margin, yPosition);
            yPosition += 7;
            doc.setFont(undefined, 'normal');
            project.contributions.forEach(contrib => {
              checkPageBreak(10);
              addWrappedText(`• ${contrib}`, 11, false, [0, 0, 0]);
            });
            yPosition += 3;
          }

          // Metrics
          if (project.metrics && project.metrics.length > 0) {
            checkPageBreak(15);
            doc.setFont(undefined, 'bold');
            doc.text('Impact:', margin, yPosition);
            yPosition += 7;
            doc.setFont(undefined, 'normal');
            project.metrics.forEach(metric => {
              checkPageBreak(10);
              let metricText = '';
              if (isLegacyMetric(metric)) {
                // Legacy format
                metricText = `${metric.primary} ${metric.label || ''}`;
                if (metric.detail) {
                  metricText += ` (${metric.detail})`;
                }
              } else if (metric.type && metric.primary && typeof metric.primary === 'object') {
                // Standardized format
                const primaryValue = formatMetricValue(metric.primary.value, metric.primary.unit);
                metricText = `${primaryValue} ${metric.primary.label || ''}`;
                if (metric.comparison) {
                  const comparisonStr = formatComparison(metric.comparison);
                  if (comparisonStr) {
                    metricText += ` (${comparisonStr})`;
                  }
                }
                if (metric.timeframe) {
                  metricText += ` - ${metric.timeframe}`;
                }
              }
              if (metricText) {
                addWrappedText(`• ${metricText}`, 11, false, [0, 0, 0]);
              }
            });
            yPosition += 3;
          }

          // Tech Stack
          if (project.techStack && project.techStack.length > 0) {
            checkPageBreak(10);
            doc.setFont(undefined, 'bold');
            doc.text('Tech Stack:', margin, yPosition);
            yPosition += 7;
            doc.setFont(undefined, 'normal');
            const techStackText = project.techStack.join(' • ');
            addWrappedText(techStackText, 11, false, [0, 0, 0]);
            yPosition += 5;
          }

          // Add spacing between projects
          if (index < portfolioProjects.length - 1) {
            yPosition += 10;
            doc.setLineWidth(0.5);
            doc.setDrawColor(200, 200, 200);
            doc.line(margin, yPosition, pageWidth - margin, yPosition);
            yPosition += 10;
          }
        });
      } else {
        checkPageBreak(20);
        doc.setFontSize(16);
        doc.setTextColor(255, 140, 66);
        doc.setFont(undefined, 'bold');
        doc.text('Projects', margin, yPosition);
        yPosition += 10;
        doc.setFontSize(11);
        doc.setTextColor(0, 0, 0);
        doc.setFont(undefined, 'normal');
        doc.text('No projects in this portfolio.', margin, yPosition);
      }

      // Footer
      const totalPages = doc.internal.pages.length - 1;
      for (let i = 1; i <= totalPages; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(150, 150, 150);
        doc.text(
          `Page ${i} of ${totalPages} | Exported from dev-impact.io`,
          pageWidth - margin,
          pageHeight - 10,
          { align: 'right' }
        );
      }

      // Save the PDF
      const filename = `${(user.name || 'portfolio').replace(/\s+/g, '-')}-${(selectedPortfolio?.name || 'export').replace(/\s+/g, '-')}.pdf`;
      doc.save(filename);

      setExportStatus('✓ PDF exported successfully!');
      setTimeout(() => setExportStatus(''), 2000);
    } catch (error) {
      console.error('PDF export error:', error);
      setExportStatus('✗ Error generating PDF: ' + error.message);
      setTimeout(() => setExportStatus(''), 3000);
    }
  };

  const handlePortfolioSelect = (portfolio) => {
    exportPDF(portfolio);
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
          <li><strong>PDF:</strong> Professional format for traditional applications with account information and portfolio projects</li>
        </ul>
      </div>

      {/* Portfolio Selection Modal for PDF Export */}
      <PortfolioSelectionModal
        isOpen={isPortfolioModalOpen}
        onClose={() => setIsPortfolioModalOpen(false)}
        portfolios={portfolios.list}
        onSelect={handlePortfolioSelect}
      />
    </div>
  );
};

export default ExportPage;
