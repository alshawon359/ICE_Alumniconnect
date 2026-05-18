import { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import {
  buildTimelineEntries,
  normalizeProfileResponse,
  splitTags,
} from '../utils/profile-utils'
import { resolveAvatarUrl, getAlumni, getStudents } from '../services/api'
import ProfileCardFrame from '../components/profile/ProfileCardFrame'
import useNavigationHistory from '../hooks/useNavigationHistory'
import '../styles/profile-page.css'

const renderContactValue = (value, fallback = '—') => value || fallback

const normalizeExternalLink = (value) => {
  if (!value) return ''
  const text = String(value).trim()
  if (!text) return ''
  return /^https?:\/\//i.test(text) ? text : `https://${text}`
}

export default function ProfileViewPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const { stack, goBack } = useNavigationHistory()
  
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Fetch profile data
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Try to fetch from alumni endpoint first
        const alumniResp = await getAlumni()
        let prof = null
        
        if (alumniResp.ok && Array.isArray(alumniResp.data)) {
          prof = alumniResp.data.find((a) => String(a.alumni_id) === String(id))
        }
        
        // If not found, try students endpoint
        if (!prof) {
          const studentsResp = await getStudents()
          if (studentsResp.ok && Array.isArray(studentsResp.data)) {
            prof = studentsResp.data.find((s) => String(s.student_id) === String(id))
          }
        }
        
        if (prof) {
          setProfile(prof)
        } else {
          setError('Profile not found')
        }
      } catch (err) {
        setError(err.message || 'Failed to load profile')
      } finally {
        setLoading(false)
      }
    }

    if (id) {
      fetchProfile()
    }
  }, [id])

  const normalizedProfile = useMemo(
    () => normalizeProfileResponse(profile || {}),
    [profile]
  )

  const avatarUrl = resolveAvatarUrl(normalizedProfile)
  const timelineEntries = useMemo(
    () => buildTimelineEntries(normalizedProfile),
    [normalizedProfile]
  )
  const expertiseTags = useMemo(
    () => splitTags(normalizedProfile.research_interests),
    [normalizedProfile.research_interests]
  )
  const activityTags = useMemo(
    () => splitTags(normalizedProfile.extracurricular),
    [normalizedProfile.extracurricular]
  )

  const socialLinks = [
    {
      key: 'linkedin',
      icon: 'fa-brands fa-linkedin-in',
      value: normalizedProfile.linkedin,
      label: 'LinkedIn',
    },
    {
      key: 'github',
      icon: 'fa-brands fa-github',
      value: normalizedProfile.github,
      label: 'GitHub',
    },
    {
      key: 'website',
      icon: 'fa-solid fa-globe',
      value: normalizedProfile.website,
      label: 'Website',
    },
  ]

  const handleBack = () => {
    // Prefer referrerPath for exact restoration (pathname + search)
    const referrerPath = location.state?.referrerPath
    if (referrerPath) {
      navigate(referrerPath, { replace: true })
      // Restore scroll position after a small delay
      setTimeout(() => {
        const scrollY = location.state?.scrollY
        if (scrollY !== undefined) window.scrollTo(0, scrollY)
      }, 0)
      return
    }

    // Try stack-based goBack
    if (stack && stack.length > 0) {
      goBack()
      return
    }

    // Fallback to referrer mapping (referrer is just a key like 'alumni-dashboard')
    const referrer = location.state?.referrer
    if (referrer === 'alumni-dashboard') {
      navigate('alumni-dashboard', { replace: true })
      return
    }
    if (referrer === 'student-dashboard') {
      navigate('student-dashboard', { replace: true })
      return
    }

    // Final fallback
    navigate(-1)
  }

  if (loading) {
    return (
      <ProfileCardFrame onBack={handleBack}>
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <p>Loading profile...</p>
        </div>
      </ProfileCardFrame>
    )
  }

  if (error) {
    return (
      <ProfileCardFrame onBack={handleBack}>
        <div style={{ padding: '20px', textAlign: 'center', color: 'red' }}>
          <p>Error: {error}</p>
        </div>
      </ProfileCardFrame>
    )
  }

  return (
    <ProfileCardFrame onBack={handleBack}>
      <div className="profile-cardboard__hero">
        <div className="profile-cardboard__avatar-column">
          <div className="profile-cardboard__avatar">
            {avatarUrl ? (
              <img src={avatarUrl} alt={normalizedProfile.name || 'Profile'} />
            ) : (
              <span>{(normalizedProfile.name || 'U').charAt(0).toUpperCase()}</span>
            )}
          </div>
          {normalizedProfile.user_type !== 'student' &&
            normalizedProfile.status === 'approved' && (
              <div className="profile-cardboard__verified">
                <i className="fa-solid fa-circle-check" /> Verified alumnus
              </div>
            )}
        </div>

        <div className="profile-cardboard__about-column">
          <div className="profile-cardboard__eyebrow">ABOUT</div>
          <h1>{normalizedProfile.name || 'Unnamed Profile'}</h1>
          <p>{normalizedProfile.bio || 'No bio has been added yet.'}</p>

          <div className="profile-cardboard__meta-pills">
            <span>{normalizedProfile.department || 'ICE'}</span>
            <span>
              {normalizedProfile.session ||
                normalizedProfile.graduation_year ||
                'Batch not set'}
            </span>
            <span>{normalizedProfile.student_id || 'ID unavailable'}</span>
            <span>{normalizedProfile.hall_name || 'Hall not set'}</span>
          </div>

          <div className="profile-cardboard__social-row">
            {socialLinks.map((item) => {
              const href = normalizeExternalLink(item.value)
              return href ? (
                <a
                  key={item.key}
                  href={href}
                  target="_blank"
                  rel="noreferrer"
                  aria-label={item.label}
                >
                  <i className={item.icon} />
                </a>
              ) : (
                <span
                  key={item.key}
                  className="profile-cardboard__social-muted"
                  title={`${item.label} unavailable`}
                >
                  <i className={item.icon} />
                </span>
              )
            })}
          </div>
        </div>
      </div>

      <section className="profile-cardboard__tri-grid">
        <div className="profile-cardboard__block">
          <h2>Professional Identity</h2>
          <dl>
            <div>
              <dt>Designation</dt>
              <dd>{renderContactValue(normalizedProfile.designation, 'Not set')}</dd>
            </div>
            <div>
              <dt>Organization</dt>
              <dd>{renderContactValue(normalizedProfile.company, 'Not set')}</dd>
            </div>
            <div>
              <dt>Department</dt>
              <dd>{renderContactValue(normalizedProfile.department, 'ICE')}</dd>
            </div>
          </dl>
        </div>

        <div className="profile-cardboard__block profile-cardboard__block--timeline">
          <h2>Academic & Career Timeline</h2>
          {timelineEntries.length ? (
            <ul>
              {timelineEntries.map((entry, index) => (
                <li key={`${entry.title}-${index}`}>
                  <strong>{entry.title || 'Timeline update'}</strong>
                  <span>{entry.meta || entry.date || 'No details yet.'}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="profile-cardboard__empty">
              No timeline entries available yet.
            </p>
          )}
        </div>

        <div className="profile-cardboard__block">
          <h2>Contact & Personal Info</h2>
          <dl>
            <div>
              <dt>Department</dt>
              <dd>{renderContactValue(normalizedProfile.department, 'ICE')}</dd>
            </div>
            <div>
              <dt>Session</dt>
              <dd>
                {renderContactValue(
                  normalizedProfile.session || normalizedProfile.graduation_year,
                  'Not set'
                )}
              </dd>
            </div>
            <div>
              <dt>Student ID</dt>
              <dd>{renderContactValue(normalizedProfile.student_id, 'Not set')}</dd>
            </div>
            <div>
              <dt>Email</dt>
              <dd>{renderContactValue(normalizedProfile.email)}</dd>
            </div>
            <div>
              <dt>Phone</dt>
              <dd>{renderContactValue(normalizedProfile.phone)}</dd>
            </div>
            <div>
              <dt>Address</dt>
              <dd>{renderContactValue(normalizedProfile.address)}</dd>
            </div>
          </dl>
        </div>
      </section>

      <section className="profile-cardboard__expertise">
        <h2>Expertise</h2>
        <div className="profile-cardboard__tag-group">
          <h3>Research Interests</h3>
          <div className="profile-cardboard__tags">
            {(expertiseTags.length
              ? expertiseTags
              : ['No research interests']
            ).map((tag) => (
              <span key={`ri-${tag}`}>{tag}</span>
            ))}
          </div>
        </div>
        <div className="profile-cardboard__tag-group">
          <h3>Extracurricular Activities</h3>
          <div className="profile-cardboard__tags">
            {(activityTags.length
              ? activityTags
              : ['No extracurricular activities']
            ).map((tag) => (
              <span key={`ea-${tag}`}>{tag}</span>
            ))}
          </div>
        </div>
      </section>
    </ProfileCardFrame>
  )
}
