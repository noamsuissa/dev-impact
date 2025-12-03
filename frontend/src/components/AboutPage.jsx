import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Code, Target, Zap, Users } from 'lucide-react';
import TerminalButton from './common/TerminalButton';

const AboutPage = () => {
  const principles = [
    {
      icon: Target,
      title: 'Show Real Impact',
      description: 'Move beyond generic bullet points. Quantify your contributions with metrics that matter—performance improvements, user growth, cost savings, and technical achievements.'
    },
    {
      icon: Code,
      title: 'Developer-First Design',
      description: 'Built by developers, for developers. We understand what recruiters and hiring managers actually want to see: concrete evidence of your technical impact.'
    },
    {
      icon: Zap,
      title: 'Focus on Outcomes',
      description: 'Every project tells a story of problem-solving. We help you structure your experience to highlight the challenges you faced, the solutions you built, and the results you delivered.'
    },
    {
      icon: Users,
      title: 'Authentic Representation',
      description: 'Your resume should reflect who you are as a developer. No fluff, no buzzwords—just clear, honest communication of your technical contributions and their impact.'
    }
  ];

  return (
    <div className="min-h-screen p-5">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-10">
          <Link to="/" className="inline-flex items-center gap-2 text-terminal-text hover:text-terminal-orange transition-colors mb-5">
            <ArrowLeft size={16} />
            <span>&gt; Back to home</span>
          </Link>
          <div className="fade-in">
            <div className="text-2xl mb-2">&gt; About dev-impact</div>
            <div className="text-terminal-gray">
              A new standard for developer resumes.
            </div>
          </div>
        </div>

        {/* Philosophy Section */}
        <div className="fade-in mb-12 border border-terminal-border p-8 bg-terminal-bg">
          <div className="text-xl mb-4 text-terminal-orange">&gt; Our Philosophy</div>
          <div className="space-y-4 text-terminal-text">
            <p>
              Traditional resumes fail developers. They force you to compress years of technical work into 
              generic bullet points that say nothing about your actual impact. Recruiters skim past them. 
              Hiring managers can't tell the difference between you and the next candidate.
            </p>
            <p>
              <span className="text-terminal-orange">dev-impact</span> changes that. We believe your resume 
              should tell a story—not just what you did, but <span className="text-terminal-green">why it mattered</span>.
            </p>
            <p>
              Every line of code you write, every system you design, every bug you fix has a measurable impact. 
              Maybe you reduced API response times by 60%. Maybe you scaled a service to handle 10x traffic. 
              Maybe you refactored legacy code that saved your team 20 hours per week.
            </p>
            <p>
              These aren't just accomplishments—they're proof of your value. And that's what we help you showcase.
            </p>
          </div>
        </div>

        {/* Core Principles */}
        <div className="fade-in mb-12">
          <div className="text-xl mb-6">&gt; Core Principles</div>
          <div className="grid md:grid-cols-2 gap-6">
            {principles.map((principle, index) => {
              const Icon = principle.icon;
              return (
                <div
                  key={principle.title}
                  className="border border-terminal-border p-6 bg-terminal-bg hover:border-terminal-orange transition-colors"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0">
                      <Icon size={24} className="text-terminal-orange" />
                    </div>
                    <div>
                      <div className="text-lg mb-2 text-terminal-orange">{principle.title}</div>
                      <div className="text-terminal-gray text-sm">{principle.description}</div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Mission Statement */}
        <div className="fade-in mb-12 border border-terminal-orange p-8 bg-terminal-bg-lighter">
          <div className="text-xl mb-4 text-terminal-orange">&gt; Our Mission</div>
          <div className="text-terminal-text space-y-3">
            <p>
              We're building a platform where developers can showcase their work in a way that truly represents 
              their skills and impact. No more one-page constraints. No more ATS-friendly keyword stuffing. 
              No more hiding your best work.
            </p>
            <p>
              With <span className="text-terminal-orange">dev-impact</span>, you create a living portfolio that 
              demonstrates not just what you've built, but the measurable difference you've made. Whether you're 
              looking for your next role, building your personal brand, or simply documenting your journey — we give 
              you the tools to tell your story.
            </p>
            <p className="text-terminal-green">
              Show real impact, not just bullet points.
            </p>
          </div>
        </div>

        {/* CTA Section */}
        <div className="fade-in text-center border border-terminal-border p-8 bg-terminal-bg">
          <div className="text-xl mb-4">&gt; Ready to get started?</div>
          <div className="text-terminal-gray mb-6">
            Join developers who are already showcasing their impact.
          </div>
          <div className="flex gap-5 justify-center flex-wrap">
            <Link to="/signup">
              <TerminalButton>
                [Start Building]
              </TerminalButton>
            </Link>
            <Link to="/pricing">
              <TerminalButton>
                [View Pricing]
              </TerminalButton>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;

