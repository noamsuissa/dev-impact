/**
 * Vercel Serverless Function to generate dynamic sitemap
 * This function fetches published portfolios and generates a sitemap including:
 * - Static pages (/, /pricing, /about, etc.)
 * - Dynamic user profile pages
 * 
 * Environment variables needed:
 * - VITE_API_URL or API_URL: Backend API URL
 * - VITE_BASE_DOMAIN: Base domain for portfolio subdomains (default: dev-impact.io)
 */

/* eslint-env node */

// Helper function to generate a sitemap URL entry
function generateSitemapUrl(loc, lastmod = null, changefreq = 'weekly', priority = 0.8) {
  const baseUrl = 'https://www.dev-impact.io';
  const fullUrl = loc.startsWith('http') ? loc : `${baseUrl}${loc}`;
  const lastmodStr = lastmod ? `    <lastmod>${lastmod}</lastmod>\n` : '';
  
  return `  <url>
    <loc>${fullUrl}</loc>
${lastmodStr}    <changefreq>${changefreq}</changefreq>
    <priority>${priority}</priority>
  </url>`;
}

// Get static pages for sitemap
function getStaticPages() {
  const now = new Date().toISOString().split('T')[0];
  
  return [
    {
      loc: '/',
      lastmod: now,
      changefreq: 'weekly',
      priority: 1.0
    },
    {
      loc: '/pricing',
      lastmod: now,
      changefreq: 'monthly',
      priority: 0.9
    },
    {
      loc: '/about',
      lastmod: now,
      changefreq: 'monthly',
      priority: 0.8
    },
    {
      loc: '/example',
      lastmod: now,
      changefreq: 'monthly',
      priority: 0.8
    },
    {
      loc: '/terms',
      lastmod: now,
      changefreq: 'yearly',
      priority: 0.5
    },
    {
      loc: '/privacy',
      lastmod: now,
      changefreq: 'yearly',
      priority: 0.5
    }
  ];
}

// Generate portfolio URL (production subdomain format)
function generatePortfolioUrl(username, portfolioSlug = null) {
  // eslint-disable-next-line no-undef
  const baseDomain = process.env.VITE_BASE_DOMAIN || 'dev-impact.io';
  if (portfolioSlug) {
    return `https://${username}.${baseDomain}/${portfolioSlug}`;
  }
  return `https://${username}.${baseDomain}`;
}

// Fetch all published portfolios from the API
async function fetchPublishedPortfolios() {
  // eslint-disable-next-line no-undef
  const apiUrl = process.env.VITE_API_URL || process.env.API_URL || 'https://api.dev-impact.io';
  const limit = 1000; // Fetch up to 1000 portfolios
  const portfolios = [];
  let offset = 0;
  let hasMore = true;

  try {
    while (hasMore) {
      const response = await fetch(`${apiUrl}/api/portfolios/published?limit=${limit}&offset=${offset}`, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        console.error(`Failed to fetch portfolios: ${response.status}`);
        break;
      }

      const data = await response.json();
      
      if (data.portfolios && data.portfolios.length > 0) {
        portfolios.push(...data.portfolios);
        offset += limit;
        hasMore = data.portfolios.length === limit;
      } else {
        hasMore = false;
      }
    }
  } catch (error) {
    console.error('Error fetching portfolios:', error);
    // Continue with static pages even if portfolio fetch fails
  }

  return portfolios;
}

// Generate sitemap XML
function generateSitemap(staticPages, portfolios) {
  const urlEntries = [];

  // Add static pages
  staticPages.forEach(page => {
    urlEntries.push(generateSitemapUrl(
      page.loc,
      page.lastmod,
      page.changefreq,
      page.priority
    ));
  });

  // Add portfolio pages
  portfolios.forEach(portfolio => {
    const username = portfolio.username;
    // portfolio_slug can be null for default portfolios
    const portfolioSlug = portfolio.portfolio_slug || null;
    const updatedAt = portfolio.updated_at ? new Date(portfolio.updated_at).toISOString().split('T')[0] : null;
    
    // Generate URL (handles both with and without portfolio slug)
    const portfolioUrl = generatePortfolioUrl(username, portfolioSlug);
    urlEntries.push(generateSitemapUrl(
      portfolioUrl,
      updatedAt,
      'weekly', // Profiles change more frequently
      0.7 // Slightly lower priority than main pages
    ));
  });

  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urlEntries.join('\n')}
</urlset>`;
}

// Vercel serverless function handler
export default async function handler(req, res) {
  try {
    // Set cache headers (cache for 1 hour, revalidate)
    res.setHeader('Cache-Control', 'public, s-maxage=3600, stale-while-revalidate=86400');
    res.setHeader('Content-Type', 'application/xml');

    // Get static pages
    const staticPages = getStaticPages();

    // Fetch published portfolios
    const portfolios = await fetchPublishedPortfolios();

    // Generate sitemap
    const sitemap = generateSitemap(staticPages, portfolios);

    // Return sitemap
    res.status(200).send(sitemap);
  } catch (error) {
    console.error('Error generating sitemap:', error);
    
    // Fallback to static pages only if there's an error
    const staticPages = getStaticPages();
    const fallbackSitemap = generateSitemap(staticPages, []);
    res.status(200).send(fallbackSitemap);
  }
}

