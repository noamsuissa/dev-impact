import { ImageResponse } from '@vercel/og';
import React from 'react';

export const runtime = 'edge';

export default async function handler(request) {
  try {
    // In Vercel Edge Functions, request is a Request object
    // Handle both full URLs and relative paths (for preview/production)
    let url;
    try {
      // Try to use request.url directly (should be full URL)
      url = new URL(request.url);
    } catch {
      // If that fails, construct from headers (for preview/production URLs)
      const host = request.headers.get('host') || request.headers.get('x-forwarded-host') || 'dev-impact.io';
      const protocol = request.headers.get('x-forwarded-proto') || 
                      (host.includes('localhost') ? 'http' : 'https');
      const path = request.url.startsWith('/') ? request.url : `/${request.url}`;
      url = new URL(`${protocol}://${host}${path}`);
    }
    const { searchParams } = url;
    
    const title = searchParams.get('title');
    const description = searchParams.get('description') || 'Show Your Developer Impact';
    const username = searchParams.get('username');
    const name = searchParams.get('name');
    const projects = searchParams.get('projects') || '0';
    const achievements = searchParams.get('achievements') || '0';
    const avatar = searchParams.get('avatar');

    const isProfile = username && name;
    const isCustomPage = title && !isProfile;

    // Use React.createElement instead of JSX for Edge Functions
    const element = React.createElement(
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
          position: 'relative',
        },
      },
      isProfile
        ? React.createElement(
            'div',
            {
              style: {
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                width: '100%',
                height: '100%',
              },
            },
            avatar &&
              React.createElement('img', {
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
            React.createElement(
              'div',
              {
                style: {
                  display: 'flex',
                  fontSize: '64px',
                  fontWeight: 'bold',
                  marginBottom: '20px',
                  textTransform: 'uppercase',
                  color: '#ff6b35',
                },
              },
              name
            ),
            React.createElement(
              'div',
              {
                style: {
                  display: 'flex',
                  gap: '40px',
                  fontSize: '32px',
                  color: '#c9c5c0',
                  marginBottom: '40px',
                },
              },
              React.createElement(
                'div',
                { style: { display: 'flex' } },
                `${projects} ${projects === '1' ? 'Project' : 'Projects'}`
              ),
              React.createElement('div', { style: { display: 'flex' } }, '•'),
              React.createElement(
                'div',
                { style: { display: 'flex' } },
                `${achievements} Achievements`
              )
            ),
            React.createElement(
              'div',
              {
                style: {
                  display: 'flex',
                  fontSize: '28px',
                  color: '#888',
                },
              },
              `dev-impact.io/${username}`
            )
          )
        : React.createElement(
            'div',
            {
              style: {
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                width: '100%',
                height: '100%',
              },
            },
            React.createElement(
              'div',
              {
                style: {
                  display: 'flex',
                  fontSize: isCustomPage ? '64px' : '80px',
                  fontWeight: 'bold',
                  marginBottom: '30px',
                  textTransform: 'uppercase',
                  color: '#ff6b35',
                  letterSpacing: isCustomPage ? '2px' : '4px',
                },
              },
              isCustomPage ? title : 'dev-impact'
            ),
            React.createElement(
              'div',
              {
                style: {
                  display: 'flex',
                  fontSize: isCustomPage ? '32px' : '36px',
                  color: '#c9c5c0',
                  marginBottom: '40px',
                  textAlign: 'center',
                  maxWidth: '900px',
                },
              },
              description
            ),
            !isCustomPage &&
              React.createElement(
                'div',
                {
                  style: {
                    display: 'flex',
                    fontSize: '28px',
                    color: '#888',
                    textAlign: 'center',
                  },
                },
                'Show real impact, not just bullet points.'
              )
          ),
      React.createElement(
        'div',
        {
          style: {
            display: 'flex',
            position: 'absolute',
            bottom: '40px',
            fontSize: '24px',
            color: '#666',
          },
        },
        'dev-impact.io'
      )
    );

    return new ImageResponse(element, {
      width: 1200,
      height: 630,
    });
  } catch (e) {
    console.error('Error generating OG image:', e.message);
    console.error('Stack:', e.stack);
    
    const errorElement = React.createElement(
      'div',
      {
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
      },
      'dev-impact'
    );

    return new ImageResponse(errorElement, {
      width: 1200,
      height: 630,
    });
  }
}

