import { ImageResponse } from '@vercel/og';

export const runtime = 'edge';

// Create a simple element creator that mimics React.createElement
// @vercel/og should handle the conversion internally
const createElement = (type, props, ...children) => {
  return {
    type,
    props: {
      ...props,
      children: children.flat().filter(Boolean),
    },
  };
};

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

      // Use createElement - JSX doesn't work in Edge runtime .js files
      const ogImage = isProfile ? (
        createElement(
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
          avatar ? createElement('img', {
            src: avatar,
            alt: name,
            width: '120',
            height: '120',
            style: {
              borderRadius: '50%',
              border: '4px solid #ff6b35',
              marginBottom: '40px',
            },
          }) : null,
          createElement('div', {
            style: {
              display: 'flex',
              fontSize: '64px',
              fontWeight: 'bold',
              marginBottom: '20px',
              textTransform: 'uppercase',
              color: '#ff6b35',
            },
          }, name),
          createElement('div', {
            style: {
              display: 'flex',
              gap: '40px',
              fontSize: '32px',
              color: '#c9c5c0',
              marginBottom: '40px',
            },
          },
            createElement('div', {
              style: { display: 'flex' },
            }, `${projects} ${projects === '1' ? 'Project' : 'Projects'}`),
            createElement('div', {
              style: { display: 'flex' },
            }, '•'),
            createElement('div', {
              style: { display: 'flex' },
            }, `${achievements} Achievements`)
          ),
          createElement('div', {
            style: {
              display: 'flex',
              fontSize: '28px',
              color: '#888',
            },
          }, `dev-impact.io/${username}`),
          createElement('div', {
            style: {
              display: 'flex',
              position: 'absolute',
              bottom: '40px',
              fontSize: '24px',
              color: '#666',
            },
          }, 'dev-impact.io')
        )
      ) : (
        createElement(
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
          createElement('div', {
            style: {
              display: 'flex',
              fontSize: isCustomPage ? '64px' : '80px',
              fontWeight: 'bold',
              marginBottom: '30px',
              textTransform: 'uppercase',
              color: '#ff6b35',
              letterSpacing: isCustomPage ? '2px' : '4px',
            },
          }, isCustomPage ? title : 'dev-impact'),
          createElement('div', {
            style: {
              display: 'flex',
              fontSize: isCustomPage ? '32px' : '36px',
              color: '#c9c5c0',
              marginBottom: '40px',
              textAlign: 'center',
              maxWidth: '900px',
            },
          }, description),
          !isCustomPage ? createElement('div', {
            style: {
              display: 'flex',
              fontSize: '28px',
              color: '#888',
              textAlign: 'center',
            },
          }, 'Show real impact, not just bullet points.') : null,
          createElement('div', {
            style: {
              display: 'flex',
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
      console.error('Stack:', e.stack);
      // Return a simple fallback image
      return new ImageResponse(
        createElement('div', {
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
