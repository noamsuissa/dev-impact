const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Initiate GitHub Device Flow
 * @returns {Promise<{deviceCode: string, userCode: string, verificationUri: string, expiresIn: number, interval: number}>}
 */
export async function initiateDeviceFlow() {
  const response = await fetch(`${API_BASE_URL}/api/auth/github/device/code`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to initiate device flow');
  }

  const data = await response.json();
  return {
    deviceCode: data.device_code,
    userCode: data.user_code,
    verificationUri: data.verification_uri,
    expiresIn: data.expires_in,
    interval: data.interval,
  };
}

/**
 * Poll for GitHub access token
 * @param {string} deviceCode
 * @returns {Promise<{status: 'pending'|'success', accessToken?: string, tokenType?: string, scope?: string}>}
 */
export async function pollForToken(deviceCode) {
  const response = await fetch(`${API_BASE_URL}/api/auth/github/device/poll`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ device_code: deviceCode }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to poll for token');
  }

  const data = await response.json();

  if (data.status === 'pending') {
    return { status: 'pending' };
  }

  return {
    status: 'success',
    accessToken: data.access_token,
    tokenType: data.token_type,
    scope: data.scope,
  };
}

/**
 * Get GitHub user profile
 * @param {string} accessToken
 * @returns {Promise<{login: string, avatar_url: string, name?: string, email?: string}>}
 */
export async function getUserProfile(accessToken) {
  const response = await fetch(`${API_BASE_URL}/api/auth/github/user`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ access_token: accessToken }),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch user profile');
  }

  return await response.json();
}

/**
 * Complete GitHub OAuth flow
 * Initiates device flow, polls for token, and fetches user profile
 * @param {Function} onCodeReady - Callback when device code is ready (receives {userCode, verificationUri})
 * @param {Function} onProgress - Optional callback for progress updates
 * @returns {Promise<{token: string, username: string, avatar_url: string, name?: string}>}
 */
export async function completeGitHubAuth(onCodeReady, onProgress = () => {}) {
  // Step 1: Initiate device flow
  onProgress('Initiating device flow...');
  const { deviceCode, userCode, verificationUri, interval } = await initiateDeviceFlow();

  // Step 2: Show code to user
  onCodeReady({ userCode, verificationUri });

  // Step 3: Poll for authorization
  onProgress('Waiting for authorization...');
  let accessToken = null;
  const maxAttempts = 60; // 5 minutes max (60 * 5 seconds)
  let attempts = 0;

  while (!accessToken && attempts < maxAttempts) {
    await new Promise(resolve => setTimeout(resolve, interval * 1000));

    try {
      const result = await pollForToken(deviceCode);

      if (result.status === 'success') {
        accessToken = result.accessToken;
        break;
      }
    } catch (error) {
      // If it's an expiration or denial error, throw it
      if (error.message.includes('expired') || error.message.includes('denied')) {
        throw error;
      }
      // Otherwise, continue polling
    }

    attempts++;
  }

  if (!accessToken) {
    throw new Error('Authorization timeout');
  }

  // Step 4: Get user profile
  onProgress('Fetching user profile...');
  const profile = await getUserProfile(accessToken);

  return {
    token: accessToken,
    username: profile.login,
    avatar_url: profile.avatar_url,
    name: profile.name,
  };
}
