/**
 * Hardcoded Configuration for AlumniConnect
 * Production: https://csf.ru.ac.bd/iceaa/
 * Development: http://localhost:5173/ (Vite default)
 */

const isDev = import.meta.env.DEV;

// ─── Hardcoded URLs ───────────────────────────────
export const CONFIG = {
  // Production domain
  PRODUCTION_DOMAIN: 'https://csf.ru.ac.bd',
  PRODUCTION_BASE_PATH: '/iceaa',
  
  // Development domain
  DEV_DOMAIN: 'http://localhost:5173',
  DEV_API_DOMAIN: 'http://localhost:5000',
  
  // Current environment
  IS_DEV: isDev,
  IS_PROD: !isDev,
};

// ─── Derived URLs ───────────────────────────────
export const getBaseURL = () => {
  if (isDev) {
    return CONFIG.DEV_DOMAIN;
  }
  return `${CONFIG.PRODUCTION_DOMAIN}${CONFIG.PRODUCTION_BASE_PATH}`;
};

export const getAPIBaseURL = () => {
  if (isDev) {
    return `${CONFIG.DEV_API_DOMAIN}/api`;
  }
  // In production, API is at /iceaa/api (same domain, reverse-proxied by nginx)
  return `${CONFIG.PRODUCTION_DOMAIN}${CONFIG.PRODUCTION_BASE_PATH}/api`;
};

export const getUploadBaseURL = () => {
  if (isDev) {
    return `${CONFIG.DEV_DOMAIN}/uploads`;
  }
  // In production, uploads are served from /iceaa/uploads
  return `${CONFIG.PRODUCTION_DOMAIN}${CONFIG.PRODUCTION_BASE_PATH}/uploads`;
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
