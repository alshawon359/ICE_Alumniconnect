import { getUploadUrl } from '../services/api'
import '../styles/event-details.css'

export default function EventDetailsModal({ event, isOpen, onClose }) {
  if (!isOpen || !event) return null

  const parseDateValue = (value) => {
    if (!value) return null
    const text = String(value).trim()

    const direct = new Date(text)
    if (!Number.isNaN(direct.getTime())) return direct

    const midnight = new Date(`${text}T00:00:00`)
    if (!Number.isNaN(midnight.getTime())) return midnight

    return null
  }

  const formatDate = (dateStr) => {
    const parsed = parseDateValue(dateStr)
    if (!parsed) return String(dateStr || 'Date TBD')
    return parsed.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
  }

  const formatTime = (timeStr) => {
    if (!timeStr) return 'Time TBD'
    const text = String(timeStr).trim()
    const normalized = text
      .replace(/\s+/g, ' ')
      .replace(/\b([ap])\.?(m)\.?$/i, (_, p1, p2) => `${p1}${p2}`.toUpperCase())

    const timeMatch = normalized.match(/^(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\s*([AP]M))?$/i)
    if (timeMatch) {
      const hours = Number(timeMatch[1])
      const minutes = Number(timeMatch[2])
      const seconds = Number(timeMatch[3] || 0)
      const meridiem = timeMatch[4]?.toUpperCase()
      const date = new Date(2000, 0, 1, hours, minutes, seconds)

      if (!Number.isNaN(date.getTime())) {
        if (meridiem) {
          return `${hours % 12 || 12}:${String(minutes).padStart(2, '0')} ${meridiem}`
        }
        return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
      }
    }

    const parsed = parseDateValue(text)
    if (parsed) return parsed.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })

    return text
  }

  const badge = event.audience === 'both' ? 'For Alumni & Students' : event.audience === 'alumni' ? 'Alumni Only' : 'Students Only'
  const bannerUrl = event.banner_image_url ? event.banner_image_url : (event.banner_image ? getUploadUrl(event.banner_image) : null)
  const attachmentHref = event.attachment_url || (event.attachment ? getUploadUrl(event.attachment) : '')

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        overflow: 'auto',
        padding: '20px',
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: '#fff',
          borderRadius: '12px',
          width: '100%',
          maxWidth: '700px',
          maxHeight: '85vh',
          overflow: 'auto',
          boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          style={{
            position: 'sticky',
            top: 10,
            right: 10,
            zIndex: 10,
            background: '#fff',
            border: '2px solid #00a3a3',
            color: '#00a3a3',
            width: '40px',
            height: '40px',
            borderRadius: '50%',
            cursor: 'pointer',
            fontSize: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            float: 'right',
            marginBottom: '10px',
          }}
        >
          ✕
        </button>

        <div className="ed-container" style={{ padding: '20px' }}>
          {bannerUrl && (
            <div className="ed-banner" style={{ marginBottom: '20px' }}>
              <img src={bannerUrl} alt={event.title} />
            </div>
          )}

          <div className="ed-content">
            <div className="ed-header">
              <div className="ed-header-top">
                <div className="ed-badge">{badge}</div>
                <div className="ed-id">Event #{event.id}</div>
              </div>
              <h1 className="ed-title">{event.title}</h1>
            </div>

            <div className="ed-info-grid">
              <div className="ed-info-box">
                <div className="ed-info-icon">
                  <i className="fa-solid fa-calendar"></i>
                </div>
                <div className="ed-info-content">
                  <div className="ed-info-label">Date</div>
                  <div className="ed-info-value">{formatDate(event.date)}</div>
                </div>
              </div>

              <div className="ed-info-box">
                <div className="ed-info-icon">
                  <i className="fa-solid fa-clock"></i>
                </div>
                <div className="ed-info-content">
                  <div className="ed-info-label">Time</div>
                  <div className="ed-info-value">{formatTime(event.event_time || event.time)}</div>
                </div>
              </div>

              {/* Attachment thumbnail placed as the 3rd info-grid item */}
              <div className="ed-info-box">
                <div className="ed-info-icon">
                  <i className="fa-solid fa-paperclip"></i>
                </div>
                <div className="ed-info-content">
                  <div className="ed-info-label">Attachment</div>
                  <div className="ed-info-value">
                    {attachmentHref ? (
                      <a href={attachmentHref} target="_blank" rel="noopener noreferrer" style={{ display: 'inline-flex', alignItems: 'center', gap: '10px', textDecoration: 'none', color: '#0f4ea8' }}>
                        {/* thumbnail preview if image-like */}
                        {!attachmentHref.toLowerCase().endsWith('.pdf') ? (
                          <img src={attachmentHref} alt={`${event.title} attachment`} style={{ width: 80, height: 56, objectFit: 'cover', borderRadius: 8, border: '1px solid #e6eef8' }} />
                        ) : (
                          <div style={{ width: 80, height: 56, display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 8, border: '1px solid #e6eef8', background: '#fff' }}>
                            <i className="fa-solid fa-file-pdf" style={{ color: '#c41d38', fontSize: 20 }}></i>
                          </div>
                        )}
                        <span style={{ fontWeight: 700, fontSize: 13 }}>{attachmentHref.toLowerCase().endsWith('.pdf') ? 'Open PDF' : 'Open Image'}</span>
                      </a>
                    ) : (
                      <span style={{ color: '#666' }}>No attachment</span>
                    )}
                  </div>
                </div>
              </div>

              <div className="ed-info-box">
                <div className="ed-info-icon">
                  <i className="fa-solid fa-location-dot"></i>
                </div>
                <div className="ed-info-content">
                  <div className="ed-info-label">Location</div>
                  <div className="ed-info-value">{event.location || 'Location TBD'}</div>
                </div>
              </div>

              {Number(event.fee) > 0 && (
                <div className="ed-info-box">
                  <div className="ed-info-icon">
                    <i className="fa-solid fa-bangladeshi-taka-sign"></i>
                  </div>
                  <div className="ed-info-content">
                    <div className="ed-info-label">Registration Fee</div>
                    <div className="ed-info-value">৳{Number(event.fee).toLocaleString()}</div>
                  </div>
                </div>
              )}

              {event.registration_deadline && (
                <div className="ed-info-box">
                  <div className="ed-info-icon">
                    <i className="fa-solid fa-hourglass-end"></i>
                  </div>
                  <div className="ed-info-content">
                    <div className="ed-info-label">Registration Deadline</div>
                    <div className="ed-info-value">{formatDate(event.registration_deadline)}</div>
                  </div>
                </div>
              )}

              {event.payment_account && (
                <div className="ed-info-box">
                  <div className="ed-info-icon">
                    <i className="fa-solid fa-building-columns"></i>
                  </div>
                  <div className="ed-info-content">
                    <div className="ed-info-label">Payment Account</div>
                    <div className="ed-info-value">{event.payment_account}</div>
                  </div>
                </div>
              )}

            </div>

            {attachmentHref && (
              <div className="ed-attachment-section" style={{ marginBottom: '20px', padding: '16px', backgroundColor: '#f7fbff', borderRadius: '12px', border: '1px solid #d9e8f6' }}>
                <h3 style={{ margin: '0 0 12px 0', fontSize: '15px', fontWeight: '700', color: '#0f4ea8' }}>
                  <i className="fa-solid fa-paperclip" style={{ marginRight: '8px' }}></i>
                  Attachment
                </h3>
                {attachmentHref.toLowerCase().endsWith('.pdf') ? (
                  <iframe
                    src={attachmentHref}
                    title={`${event.title} attachment`}
                    style={{ width: '100%', height: '360px', border: '1px solid #d9e8f6', borderRadius: '10px', background: '#fff' }}
                  />
                ) : (
                  <img
                    src={attachmentHref}
                    alt={`${event.title} attachment`}
                    style={{ width: '100%', maxHeight: '360px', objectFit: 'contain', borderRadius: '10px', background: '#fff', border: '1px solid #d9e8f6' }}
                  />
                )}
                <div style={{ marginTop: '12px' }}>
                  <a
                    href={attachmentHref}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '8px',
                      padding: '9px 14px',
                      backgroundColor: '#00a3a3',
                      color: '#fff',
                      borderRadius: '8px',
                      textDecoration: 'none',
                      fontSize: '13px',
                      fontWeight: '600',
                    }}
                  >
                    <i className={attachmentHref.toLowerCase().endsWith('.pdf') ? 'fa-solid fa-file-pdf' : 'fa-solid fa-image'} />
                    View Document
                  </a>
                </div>
              </div>
            )}

            <div className="ed-description-section">
              <h2 className="ed-section-title">About This Event</h2>
              <div className="ed-description">
                {event.description || 'No description provided'}
              </div>
            </div>

            <div className="ed-metadata">
              {event.created_at && (
                <div className="ed-meta-item">
                  <span className="ed-meta-label">Created:</span>
                  <span className="ed-meta-value">
                    {formatDate(event.created_at)}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
