import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { NavigationHistoryProvider } from './context/NavigationHistoryContext'
import { ROUTES } from './shared/constants/routes'
import Home from './pages/Home'
import AlumniLogin from './pages/AlumniLogin'
import AlumniRegister from './pages/AlumniRegister'
import AdminLogin from './pages/AdminLogin'
import AdminDashboard from './pages/AdminDashboard'
import AlumniDashboard from './pages/AlumniDashboard'
import StudentLogin from './pages/StudentLogin'
import StudentRegister from './pages/StudentRegister'
import StudentDashboard from './pages/StudentDashboard'
import AlumniForgotPassword from './pages/AlumniForgotPassword'
import StudentForgotPassword from './pages/StudentForgotPassword'
import EditProfilePage from './pages/EditProfilePage'
import ProfileViewPage from './pages/ProfileViewPage'
import './styles/style.css'
import './styles/profile-image.css'

const routerBasename = import.meta.env.BASE_URL && import.meta.env.BASE_URL !== '/' ? import.meta.env.BASE_URL.replace(/\/$/, '') : undefined

function App() {
  return (
    <BrowserRouter basename={routerBasename}>
      <NavigationHistoryProvider>
        <Routes>
          <Route path={ROUTES.HOME} element={<Home />} />
          <Route path={ROUTES.ALUMNI_LOGIN} element={<AlumniLogin />} />
          <Route path={ROUTES.ALUMNI_FORGOT_PASSWORD} element={<AlumniForgotPassword />} />
          <Route path={ROUTES.ALUMNI_REGISTER} element={<AlumniRegister />} />
          <Route path={ROUTES.ALUMNI_DASHBOARD} element={<AlumniDashboard />} />
          <Route path={ROUTES.ADMIN_LOGIN} element={<AdminLogin />} />
          <Route path={ROUTES.ADMIN_DASHBOARD} element={<AdminDashboard />} />
          <Route path={ROUTES.STUDENT_LOGIN} element={<StudentLogin />} />
          <Route path={ROUTES.STUDENT_FORGOT_PASSWORD} element={<StudentForgotPassword />} />
          <Route path={ROUTES.STUDENT_REGISTER} element={<StudentRegister />} />
          <Route path={ROUTES.STUDENT_DASHBOARD} element={<StudentDashboard />} />
          <Route path={ROUTES.EDIT_PROFILE} element={<EditProfilePage />} />
          <Route path={ROUTES.PROFILE_VIEW} element={<ProfileViewPage />} />
        </Routes>
      </NavigationHistoryProvider>
    </BrowserRouter>
  )
}

export default App
