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
    const avatar = params.get('avatar'); // optional remote image (won't be embedded)

    const isProfile = username && name;
    const isCustomPage = title && !isProfile;

    // Build an SVG string (1200x630)
    const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-label="${escapeXml(title)}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#2d2d2d"/>
      <stop offset="100%" stop-color="#111"/>
    </linearGradient>
    <style>
      .title { font: 700 64px system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; fill: #ff6b35; letter-spacing: 1px; }
      .subtitle { font: 400 28px system-ui, -apple-system, "Segoe UI", Roboto; fill: #c9c5c0; }
      .meta { font: 600 20px system-ui, -apple-system, "Segoe UI", Roboto; fill: #ddd; }
      .small { font: 600 18px system-ui, -apple-system, "Segoe UI", Roboto; fill: #666; }
    </style>
  </defs>

  <rect width="1200" height="630" fill="url(#g)" />
  <g transform="translate(80,80)">

    <g transform="translate(0,0)">
      <text x="0" y="110" class="title">${escapeXml(isProfile ? name : (isCustomPage ? title : 'dev-impact'))}</text>
      <text x="0" y="170" class="subtitle">${escapeXml(isProfile ? `@${username} — ${description}` : description)}</text>
    </g>

    <g transform="translate(0,260)" >
      <text x="0" y="40" class="meta">Projects: ${escapeXml(projects)} — Achievements: ${escapeXml(achievements)}</text>
    </g>

    <g transform="translate(0,340)">
      <text x="0" y="40" class="small">dev-impact.io${isProfile ? `/${escapeXml(username)}` : ''}</text>
    </g>

  </g>
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
