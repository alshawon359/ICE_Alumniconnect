/**
 * Hardcoded Configuration for AlumniConnect
 * Dynamically detects domain from current location
 * Works across multiple networks and environments
 */

const isDev = import.meta.env.DEV;

// ─── Dynamic domain detection ───────────────────────────
const getCurrentDomain = () => {
  if (typeof window === 'undefined') {
    return isDev ? 'http://localhost:5173' : 'https://csf.ru.ac.bd';
  }
  
  // Use current domain from browser location
  return window.location.origin;
};

const getBasePath = () => {
  if (typeof window === 'undefined') {
    return isDev ? '/' : '/iceaa';
  }
  
  // Check if we're running in dev mode
  if (isDev) return '/';
  
  // Production: check if already under /iceaa
  const pathname = window.location.pathname;
  if (pathname.startsWith('/iceaa')) {
    return '/iceaa';
  }
  
  // Default to /iceaa for production
  return '/iceaa';
};

// ─── Configuration ───────────────────────────────────
export const CONFIG = {
  IS_DEV: isDev,
  IS_PROD: !isDev,
};

// ─── Derived URLs ───────────────────────────────────
export const getBaseURL = () => {
  const domain = getCurrentDomain();
  const basePath = getBasePath();
  
  if (basePath === '/') {
    return domain;
  }
  
  return `${domain}${basePath}`;
};

export const getAPIBaseURL = () => {
  const domain = getCurrentDomain();
  
  if (isDev) {
    // Development: API is on localhost:5000
    return 'http://localhost:5000/api';
  }
  
  // Production: API is at same domain under /iceaa/api
  return `${domain}/iceaa/api`;
};

export const getUploadBaseURL = () => {
  const domain = getCurrentDomain();
  
  if (isDev) {
    return 'http://localhost:5000/uploads';
  }
  
  // Production: uploads served from /iceaa/uploads (reverse-proxied by nginx)
  return `${domain}/iceaa/uploads`;
};

// ─── Helper: Construct full URL ───────────────────
export const buildFullURL = (pathname = '') => {
  const base = getBaseURL();
  if (pathname.startsWith('/')) {
    return `${base}${pathname}`;
  }
  return `${base}/${pathname}`;
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
