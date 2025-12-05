// repo/frontend/api/og.mjs
export const config = { runtime: 'edge' };

/**
 * Works with both Edge Request.headers (Headers with .get)
 * and Node-style plain object headers.
 */
function getHeader(req, name) {
  if (!req || !req.headers) return undefined;
  if (typeof req.headers.get === 'function') return req.headers.get(name);
  return req.headers[name.toLowerCase()] || req.headers[name];
}

function escapeXml(str = '') {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

export default async function handler(request) {
  try {
    // safe base for relative URLs
    const host = getHeader(request, 'host') || 'localhost';
    const base = `https://${host}`;
    const url = new URL(request.url, base);
    const params = url.searchParams;

    const title = params.get('title') || 'dev-impact';
    const description = params.get('description') || 'Show Your Developer Impact';
    const username = params.get('username');
    const name = params.get('name');
    const projects = params.get('projects') || '0';
    const achievements = params.get('achievements') || '0';

    const isProfile = username && name;
    const isCustomPage = title && !isProfile;
    const heroTitle = isProfile ? name : (isCustomPage ? title : 'dev-impact');
    const heroSubtitle = isProfile ? 'Developer Profile' : description;
    const statLine = `${projects} Projects • ${achievements} Achievements`;
    const bannerText = description || 'Show real impact, not just bullet points.';
    const projectCards = ['TechCorp', 'StartupXYZ', 'CloudScale']
      .map((company, index) => {
        const problems = [
          'Problem: Scale and reliability',
          'Problem: Manual dashboards',
          'Problem: Legacy deployments',
        ];
        const solutions = [
          'Solution: Real-time data pipeline',
          'Solution: Interactive analytics UI',
          'Solution: Microservices + CI/CD',
        ];
        const metrics = ['60% Faster', '10x Faster', '95% Faster'];
        return `
      <g transform="translate(${index * 360}, 0)">
        <rect x="0" y="0" width="340" height="220" fill="none" stroke="#666" stroke-width="2" stroke-dasharray="6 6" />
        <text x="16" y="30" font-size="20" fill="#ff6b35" font-family="IBM Plex Mono, monospace" font-weight="700">Company: ${escapeXml(company)}</text>
        <text x="16" y="60" font-size="18" fill="#c9c5c0" font-family="IBM Plex Mono, monospace">${escapeXml(problems[index])}</text>
        <text x="16" y="90" font-size="18" fill="#c9c5c0" font-family="IBM Plex Mono, monospace">${escapeXml(solutions[index])}</text>
        <text x="16" y="190" font-size="20" fill="#ffffff" font-family="IBM Plex Mono, monospace">${escapeXml(metrics[index])}</text>
      </g>`;
      })
      .join('');

    const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-label="${escapeXml(heroTitle)}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1a1a1a"/>
      <stop offset="100%" stop-color="#0d0d0d"/>
    </linearGradient>
    <style>
      .mono { font-family: "IBM Plex Mono", "Space Mono", monospace; }
    </style>
  </defs>

  <rect width="1200" height="630" fill="url(#bg)" />

  <rect x="80" y="30" width="1040" height="45" rx="6" fill="#23170d" stroke="#ff6b35" stroke-width="1" />
  <text x="96" y="60" font-size="20" fill="#ff8b3c" class="mono">> ${escapeXml(bannerText)} Create your own profile →</text>

  <rect x="80" y="100" width="1040" height="200" rx="12" fill="#2f2f2f" stroke="#444" stroke-width="1" />
  <circle cx="140" cy="200" r="55" fill="#0d0d0d" stroke="#ff6b35" stroke-width="4" />
  <text x="210" y="170" font-size="48" fill="#ff8b35" letter-spacing="2" class="mono">${escapeXml(heroTitle.toUpperCase())}</text>
  <text x="210" y="210" font-size="24" fill="#c9c5c0" class="mono">${escapeXml(heroSubtitle)}</text>
  <text x="210" y="250" font-size="20" fill="#8b8b8b" class="mono">${isProfile && username ? `github.com/${escapeXml(username)}` : 'Showcase your projects'}</text>
  <line x1="210" y1="265" x2="980" y2="265" stroke="#333" stroke-width="1" />
  <text x="210" y="300" font-size="22" fill="#ffffff" class="mono">${escapeXml(statLine)}</text>

  <text x="80" y="340" font-size="28" fill="#ffffff" class="mono">> Projects (${escapeXml(projects)})</text>

  <g transform="translate(80, 360)">
    ${projectCards}
  </g>

  <rect x="80" y="580" width="1040" height="1" fill="#333" />
</svg>`;

    return new Response(svg, {
      status: 200,
      headers: {
        'Content-Type': 'image/svg+xml; charset=utf-8',
        // tune caching as you like
        'Cache-Control': 'public, max-age=3600, stale-while-revalidate=86400',
      },
    });
  } catch (err) {
    console.error('OG SVG error', err);
    const fallback = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630"><rect width="100%" height="100%" fill="#222"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#ff6b35" font-size="48">dev-impact</text></svg>`;
    return new Response(fallback, {
      status: 200,
      headers: { 'Content-Type': 'image/svg+xml; charset=utf-8' },
    });
  }
}
