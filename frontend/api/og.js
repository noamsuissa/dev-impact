import { ImageResponse } from '@vercel/og';
import React from 'react';

export const runtime = 'edge';

export default {
  async fetch(request) {
    try {
      const { searchParams } = new URL(request.url);
      
      const title = searchParams.get('title');
      const description = searchParams.get('description') || 'Show Your Developer Impact';
      const username = searchParams.get('username');
      const name = searchParams.get('name');
      const projects = searchParams.get('projects') || '0';
      const achievements = searchParams.get('achievements') || '0';
      const avatar = searchParams.get('avatar');

      const isProfile = username && name;
      const isCustomPage = title && !isProfile;

      // Build the OG image using React.createElement (no JSX in Edge runtime)
      const ogImage = isProfile ? (
        React.createElement(
          'div',
          {
            style: {
              height: '100%',
              width: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: '#2d2d2d',
              backgroundImage: 'linear-gradient(to bottom, #2d2d2d, #1a1a1a)',
              fontFamily: 'monospace',
              color: '#ff6b35',
              padding: '80px',
            },
          },
          avatar && React.createElement('img', {
            src: avatar,
            alt: name,
            width: '120',
            height: '120',
            style: {
              borderRadius: '50%',
              border: '4px solid #ff6b35',
              marginBottom: '40px',
            },
          }),
          React.createElement('div', {
            style: {
              fontSize: '64px',
              fontWeight: 'bold',
              marginBottom: '20px',
              textTransform: 'uppercase',
              color: '#ff6b35',
            },
          }, name),
          React.createElement('div', {
            style: {
              display: 'flex',
              gap: '40px',
              fontSize: '32px',
              color: '#c9c5c0',
              marginBottom: '40px',
            },
          },
            React.createElement('div', null, `${projects} ${projects === '1' ? 'Project' : 'Projects'}`),
            React.createElement('div', null, '•'),
            React.createElement('div', null, `${achievements} Achievements`)
          ),
          React.createElement('div', {
            style: {
              fontSize: '28px',
              color: '#888',
            },
          }, `dev-impact.io/${username}`),
          React.createElement('div', {
            style: {
              position: 'absolute',
              bottom: '40px',
              fontSize: '24px',
              color: '#666',
            },
          }, 'dev-impact.io')
        )
      ) : (
        React.createElement(
          'div',
          {
            style: {
              height: '100%',
              width: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: '#2d2d2d',
              backgroundImage: 'linear-gradient(to bottom, #2d2d2d, #1a1a1a)',
              fontFamily: 'monospace',
              color: '#ff6b35',
              padding: '80px',
            },
          },
          React.createElement('div', {
            style: {
              fontSize: isCustomPage ? '64px' : '80px',
              fontWeight: 'bold',
              marginBottom: '30px',
              textTransform: 'uppercase',
              color: '#ff6b35',
              letterSpacing: isCustomPage ? '2px' : '4px',
            },
          }, isCustomPage ? title : 'dev-impact'),
          React.createElement('div', {
            style: {
              fontSize: isCustomPage ? '32px' : '36px',
              color: '#c9c5c0',
              marginBottom: '40px',
              textAlign: 'center',
              maxWidth: '900px',
            },
          }, description),
          !isCustomPage && React.createElement('div', {
            style: {
              fontSize: '28px',
              color: '#888',
              textAlign: 'center',
            },
          }, 'Show real impact, not just bullet points.'),
          React.createElement('div', {
            style: {
              position: 'absolute',
              bottom: '40px',
              fontSize: '24px',
              color: '#666',
            },
          }, 'dev-impact.io')
        )
      );

      return new ImageResponse(ogImage, {
        width: 1200,
        height: 630,
      });
    } catch (e) {
      console.error('Error generating OG image:', e.message);
      return new ImageResponse(
        React.createElement('div', {
          style: {
            height: '100%',
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#2d2d2d',
            color: '#ff6b35',
            fontSize: '40px',
          },
        }, 'dev-impact'),
        {
          width: 1200,
          height: 630,
        }
      );
    }
  },
};
