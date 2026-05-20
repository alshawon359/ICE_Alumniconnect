/**
 * Global API Configuration
 * Uses RELATIVE PATHS for maximum compatibility
 * Works from ANY domain/IP/network automatically
 */

const isDev = import.meta.env.DEV;

// ─── Configuration ───────────────────────────────────
export const CONFIG = {
  IS_DEV: isDev,
  IS_PROD: !isDev,
};

// ─── API Paths (relative - works everywhere) ─────────
export const getAPIBaseURL = () => {
  if (isDev) {
    // Development: API on localhost:5000
    return 'http://localhost:5000/api';
  }
  
  // Production: Use relative path /iceaa/api
  // Browser automatically uses current domain/IP/protocol
  return '/iceaa/api';
};

export const getUploadBaseURL = () => {
  if (isDev) {
    return 'http://localhost:5000/uploads';
  }
  
  // Production: Relative path for uploads
  return '/iceaa/uploads';
};

// ─── Helper: Construct API URL ───────────────────
export const buildAPIURL = (endpoint = '') => {
  const base = getAPIBaseURL();
  if (endpoint.startsWith('/')) {
    return `${base}${endpoint}`;
  }
  return `${base}/${endpoint}`;
};

export default CONFIG;
