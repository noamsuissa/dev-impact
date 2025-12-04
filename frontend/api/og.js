import { ImageResponse } from '@vercel/og';

export const config = {
  runtime: 'nodejs',
};

export default async function handler(req) {
  try {
    // Extract URL from request - Vercel serverless functions provide req.url
    const url = new URL(req.url || `https://${req.headers?.host || 'dev-impact.io'}/api/og`);
    const { searchParams } = url;
    
    // Get query parameters
    const title = searchParams.get('title');
    const description = searchParams.get('description') || 'Show Your Developer Impact';
    const username = searchParams.get('username');
    const name = searchParams.get('name');
    const projects = searchParams.get('projects') || '0';
    const achievements = searchParams.get('achievements') || '0';
    const avatar = searchParams.get('avatar');

    // Determine if this is a profile page, custom page, or homepage
    const isProfile = username && name;
    const isCustomPage = title && !isProfile;

    const imageResponse = new ImageResponse(
      (
        <div
          style={{
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
          }}
        >
          {isProfile ? (
            // Profile OG Image
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                width: '100%',
                height: '100%',
              }}
            >
              {/* Avatar */}
              {avatar && (
                <img
                  src={avatar}
                  alt={name}
                  width="120"
                  height="120"
                  style={{
                    borderRadius: '50%',
                    border: '4px solid #ff6b35',
                    marginBottom: '40px',
                  }}
                />
              )}
              
              {/* Name */}
              <div
                style={{
                  fontSize: '64px',
                  fontWeight: 'bold',
                  marginBottom: '20px',
                  textTransform: 'uppercase',
                  color: '#ff6b35',
                }}
              >
                {name}
              </div>

              {/* Stats */}
              <div
                style={{
                  display: 'flex',
                  gap: '40px',
                  fontSize: '32px',
                  color: '#c9c5c0',
                  marginBottom: '40px',
                }}
              >
                <div>{projects} {projects === '1' ? 'Project' : 'Projects'}</div>
                <div>•</div>
                <div>{achievements} Achievements</div>
              </div>

              {/* Username */}
              <div
                style={{
                  fontSize: '28px',
                  color: '#888',
                }}
              >
                dev-impact.io/{username}
              </div>
            </div>
          ) : (
            // Homepage or Custom Page OG Image
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                width: '100%',
                height: '100%',
              }}
            >
              {/* Logo/Title */}
              <div
                style={{
                  fontSize: isCustomPage ? '64px' : '80px',
                  fontWeight: 'bold',
                  marginBottom: '30px',
                  textTransform: 'uppercase',
                  color: '#ff6b35',
                  letterSpacing: isCustomPage ? '2px' : '4px',
                }}
              >
                {isCustomPage ? title : 'dev-impact'}
              </div>

              {/* Tagline */}
              <div
                style={{
                  fontSize: isCustomPage ? '32px' : '36px',
                  color: '#c9c5c0',
                  marginBottom: '40px',
                  textAlign: 'center',
                  maxWidth: '900px',
                }}
              >
                {description}
              </div>

              {/* Subtitle - only show on homepage */}
              {!isCustomPage && (
                <div
                  style={{
                    fontSize: '28px',
                    color: '#888',
                    textAlign: 'center',
                  }}
                >
                  Show real impact, not just bullet points.
                </div>
              )}
            </div>
          )}

          {/* Footer */}
          <div
            style={{
              position: 'absolute',
              bottom: '40px',
              fontSize: '24px',
              color: '#666',
            }}
          >
            dev-impact.io
          </div>
        </div>
      ),
      {
        width: 1200,
        height: 630,
      }
    );

    return imageResponse;
  } catch (e) {
    console.error('Error generating OG image:', e);
    return new Response('Failed to generate OG image', { 
      status: 500,
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}

