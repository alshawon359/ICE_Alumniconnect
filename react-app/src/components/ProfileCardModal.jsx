import { useMemo } from 'react'
import {
  buildTimelineEntries,
  normalizeProfileResponse,
  splitTags,
} from '../utils/profile-utils'
import { resolveAvatarUrl } from '../services/api'
import '../styles/profile-page.css'

const renderContactValue = (value, fallback = '—') => value || fallback
const normalizeExternalLink = (value) => {
  if (!value) return ''
  const text = String(value).trim()
  if (!text) return ''
  return /^https?:\/\//i.test(text) ? text : `https://${text}`
}

export default function ProfileCardModal({ profile: rawProfile, onClose, isOpen }) {
  const profile = useMemo(() => normalizeProfileResponse(rawProfile || {}), [rawProfile])

  const avatarUrl = resolveAvatarUrl(profile)
  const timelineEntries = useMemo(() => buildTimelineEntries(profile), [profile])
  const expertiseTags = useMemo(() => splitTags(profile.research_interests), [profile.research_interests])
  const activityTags = useMemo(() => splitTags(profile.extracurricular), [profile.extracurricular])

  const socialLinks = [
    { key: 'linkedin', icon: 'fa-brands fa-linkedin-in', value: profile.linkedin, label: 'LinkedIn' },
    { key: 'github', icon: 'fa-brands fa-github', value: profile.github, label: 'GitHub' },
    { key: 'website', icon: 'fa-solid fa-globe', value: profile.website, label: 'Website' },
  ]

  if (!isOpen) return null

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '20px',
      overflowY: 'auto',
    }} onClick={onClose}>
      <div style={{
        background: '#fff',
        borderRadius: '44px',
        maxWidth: '900px',
        width: '100%',
        maxHeight: '90vh',
        overflowY: 'auto',
        position: 'relative',
      }} onClick={(e) => e.stopPropagation()}>
        
        {/* Close button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            background: 'linear-gradient(135deg,#0f4ea8,#00a3a3)',
            color: 'white',
            border: 'none',
            borderRadius: '50%',
            width: '40px',
            height: '40px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10000,
            fontSize: '18px',
          }}
          title="Close profile card"
        >
          <i className="fa-solid fa-xmark"></i>
        </button>

        {/* Profile Card Content */}
        <div style={{ padding: '22px' }}>
          <article className="profile-cardboard">
            <div className="profile-cardboard__crest">RU</div>

            <div className="profile-cardboard__hero">
              <div className="profile-cardboard__avatar-column">
                <div className="profile-cardboard__avatar">
                  {avatarUrl ? (
                    <img src={avatarUrl} alt={profile.name || 'Profile'} />
                  ) : (
                    <span>{(profile.name || 'U').charAt(0).toUpperCase()}</span>
                  )}
                </div>
                {profile.user_type !== 'student' && profile.status === 'approved' && (
                  <div className="profile-cardboard__verified">
                    <i className="fa-solid fa-circle-check" /> Verified alumnus
                  </div>
                )}
              </div>

              <div className="profile-cardboard__about-column">
                <div className="profile-cardboard__eyebrow">ABOUT</div>
                <h1>{profile.name || 'Unnamed Profile'}</h1>
                <p>{profile.bio || 'No bio has been added yet.'}</p>

                <div className="profile-cardboard__meta-pills">
                  <span>{profile.department || 'ICE'}</span>
                  <span>{profile.session || profile.graduation_year || 'Batch not set'}</span>
                  <span>{profile.student_id || 'ID unavailable'}</span>
                  <span>{profile.hall_name || 'Hall not set'}</span>
                </div>

                <div className="profile-cardboard__social-row">
                  {socialLinks.map((item) => {
                    const href = normalizeExternalLink(item.value)
                    return href ? (
                      <a key={item.key} href={href} target="_blank" rel="noreferrer" aria-label={item.label}>
                        <i className={item.icon} />
                      </a>
                    ) : (
                      <span key={item.key} className="profile-cardboard__social-muted" title={`${item.label} unavailable`}>
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
                    <dd>{renderContactValue(profile.designation, 'Not set')}</dd>
                  </div>
                  <div>
                    <dt>Organization</dt>
                    <dd>{renderContactValue(profile.company, 'Not set')}</dd>
                  </div>
                  <div>
                    <dt>Department</dt>
                    <dd>{renderContactValue(profile.department, 'ICE')}</dd>
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
                  <p className="profile-cardboard__empty">No timeline entries available yet.</p>
                )}
              </div>

              <div className="profile-cardboard__block">
                <h2>Contact & Personal Info</h2>
                <dl>
                  <div>
                    <dt>Department</dt>
                    <dd>{renderContactValue(profile.department, 'ICE')}</dd>
                  </div>
                  <div>
                    <dt>Session</dt>
                    <dd>{renderContactValue(profile.session || profile.graduation_year, 'Not set')}</dd>
                  </div>
                  <div>
                    <dt>Student ID</dt>
                    <dd>{renderContactValue(profile.student_id, 'Not set')}</dd>
                  </div>
                  <div>
                    <dt>Email</dt>
                    <dd>{renderContactValue(profile.email)}</dd>
                  </div>
                  <div>
                    <dt>Phone</dt>
                    <dd>{renderContactValue(profile.phone)}</dd>
                  </div>
                  <div>
                    <dt>Address</dt>
                    <dd>{renderContactValue(profile.address)}</dd>
                  </div>
                </dl>
              </div>
            </section>

            <section className="profile-cardboard__expertise">
              <h2>Expertise</h2>
              <div className="profile-cardboard__tag-group">
                <h3>Research Interests</h3>
                <div className="profile-cardboard__tags">
                  {(expertiseTags.length ? expertiseTags : ['No research interests']).map((tag) => (
                    <span key={`ri-${tag}`}>{tag}</span>
                  ))}
                </div>
              </div>
              <div className="profile-cardboard__tag-group">
                <h3>Extracurricular Activities</h3>
                <div className="profile-cardboard__tags">
                  {(activityTags.length ? activityTags : ['No extracurricular activities']).map((tag) => (
                    <span key={`ea-${tag}`}>{tag}</span>
                  ))}
                </div>
              </div>
            </section>
          </article>
        </div>
      </div>
    </div>
  )
}
