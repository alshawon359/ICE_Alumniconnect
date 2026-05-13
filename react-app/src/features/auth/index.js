// Feature barrel for auth pages — exposes pages from new feature location and
// provides compatibility re-exports if older imports exist.
export { default as AlumniLogin } from './pages/AlumniLogin'
export { default as StudentLogin } from './pages/StudentLogin'
export { default as AdminLogin } from './pages/AdminLogin'
export { default as AlumniRegister } from './pages/AlumniRegister'

// More auth exports can be added here in future (forgot password, register pages)
