import { ImageResponse } from '@vercel/og';

export const runtime = 'edge';

export default async function handler(request) {
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

    // @vercel/og accepts JSX directly in .jsx files
    return new ImageResponse(
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
              position: 'relative',
            }}
          >
            {isProfile ? (
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
                
                <div
                  style={{
                    display: 'flex',
                    fontSize: '64px',
                    fontWeight: 'bold',
                    marginBottom: '20px',
                    textTransform: 'uppercase',
                    color: '#ff6b35',
                  }}
                >
                  {name}
                </div>

                <div
                  style={{
                    display: 'flex',
                    gap: '40px',
                    fontSize: '32px',
                    color: '#c9c5c0',
                    marginBottom: '40px',
                  }}
                >
                  <div style={{ display: 'flex' }}>{projects} {projects === '1' ? 'Project' : 'Projects'}</div>
                  <div style={{ display: 'flex' }}>•</div>
                  <div style={{ display: 'flex' }}>{achievements} Achievements</div>
                </div>

                <div
                  style={{
                    display: 'flex',
                    fontSize: '28px',
                    color: '#888',
                  }}
                >
                  dev-impact.io/{username}
                </div>
              </div>
            ) : (
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
                <div
                  style={{
                    display: 'flex',
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

                <div
                  style={{
                    display: 'flex',
                    fontSize: isCustomPage ? '32px' : '36px',
                    color: '#c9c5c0',
                    marginBottom: '40px',
                    textAlign: 'center',
                    maxWidth: '900px',
                  }}
                >
                  {description}
                </div>

                {!isCustomPage && (
                  <div
                    style={{
                      display: 'flex',
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

            <div
              style={{
                display: 'flex',
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
  } catch (e) {
    console.error('Error generating OG image:', e.message);
    console.error('Stack:', e.stack);
    return new ImageResponse(
      (
        <div
          style={{
            height: '100%',
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#2d2d2d',
            color: '#ff6b35',
            fontSize: '40px',
          }}
        >
          dev-impact
        </div>
      ),
      {
        width: 1200,
        height: 630,
      }
    );
  }
}
