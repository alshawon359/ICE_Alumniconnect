import { useState, useEffect, useRef } from 'react'
import '../styles/success-story.css'
import {
  getSuccessStories,
  submitSuccessStory,
  updateSuccessStory,
  deleteSuccessStory,
  getMySuccessStories,
  getUploadUrl,
  resolveAvatarUrl
  , postStoryReact, getStoryComments, postStoryComment
} from '../services/api'

const SuccessStory = ({ currentAlumni }) => {
  const formCardRef = useRef(null)
  const [stories, setStories] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [loadingMore, setLoadingMore] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const [page, setPage] = useState(1)

  // Form states
  const [formData, setFormData] = useState({
    title: '',
    story: '',
    currentPosition: currentAlumni?.designation || '',
    batch: currentAlumni?.session || currentAlumni?.graduation_year || '',
    imageUrl: null
  })
  const [imagePreview, setImagePreview] = useState(null)
  const [imageFile, setImageFile] = useState(null)
  const [formError, setFormError] = useState(null)
  const [showMyStories, setShowMyStories] = useState(false)
  const [myStories, setMyStories] = useState([])
  const [editingId, setEditingId] = useState(null)
  const [commentsMap, setCommentsMap] = useState({})

  // Check if user is logged in
  useEffect(() => {
    console.log('currentAlumni prop:', currentAlumni)
    const alumniId = currentAlumni?.id || currentAlumni?.student_id
    if (currentAlumni && alumniId) {
      console.log('User is logged in as:', alumniId)
      setError(null)  // Clear any login error
    } else {
      console.warn('currentAlumni is missing or incomplete:', currentAlumni)
      // Don't block the view, just log the warning
      // User might still be able to view stories even if we can't post
    }
  }, [currentAlumni])

  // Fetch stories on mount and when page changes
  useEffect(() => {
    fetchStories(page === 1)
  }, [page])

  const fetchStories = async (reset = false) => {
    try {
      if (reset) setLoading(true)
      else setLoadingMore(true)

      console.log('Fetching stories for page:', page)
      const response = await getSuccessStories(page)
      console.log('API response:', response)
      
      // Extract the actual stories array from the API response
      // The API wrapper returns { ok, status, data: {success, data: [...], page, limit} }
      let newStories = []
      if (response?.data?.data && Array.isArray(response.data.data)) {
        newStories = response.data.data
      } else if (response?.data && Array.isArray(response.data)) {
        newStories = response.data
      }
      console.log('New stories:', newStories, 'count:', newStories.length)

      if (reset) {
        setStories(newStories)
      } else {
        setStories(prev => {
          // Ensure prev is an array
          const prevArray = Array.isArray(prev) ? prev : []
          return [...prevArray, ...newStories]
        })
      }

      // If we got fewer stories than expected, no more data
      if (newStories.length < 10) {
        setHasMore(false)
      }

      setError(null)
    } catch (err) {
      console.error('Failed to fetch stories:', err)
      setError('Failed to load success stories. Please try again later.')
      setStories([])  // Ensure stories is always an array on error
    } finally {
      setLoading(false)
      setLoadingMore(false)
    }
  }

  const handleImageChange = (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!['image/png', 'image/jpeg', 'image/gif', 'image/webp'].includes(file.type)) {
      setFormError('Please upload an image file (PNG, JPG, GIF, WebP)')
      return
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setFormError('Image size must be less than 10MB')
      return
    }

    setImageFile(file)
    const reader = new FileReader()
    reader.onload = (event) => {
      setImagePreview(event.target.result)
    }
    reader.readAsDataURL(file)
    setFormError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setFormError(null)

    // Validate user is logged in
      const alumniId = currentAlumni?.id || currentAlumni?.student_id
      if (!currentAlumni || !alumniId) {
      return
    }

    // Validate required fields
    if (!formData.story.trim()) {
      setFormError('Please share your success story')
      return
    }

    if (!formData.batch.trim()) {
      setFormError('Please enter your batch/graduation year')
      return
    }

    try {
      setSubmitting(true)

      // Prepare payload
      const payload = {
        alumni_id: currentAlumni?.id || '',
        student_id: currentAlumni?.student_id || '',
        title: formData.title || '',
        story: formData.story,
        current_position: formData.currentPosition || '',
        batch: formData.batch,
        department: currentAlumni?.department || 'ICE'
      }

      let response
      if (editingId) {
        response = await updateSuccessStory(editingId, payload)
      } else {
        const submitData = {
          title: payload.title,
          story: payload.story,
          current_position: payload.current_position,
          batch: payload.batch,
          department: payload.department,
          image_file: imageFile
        }
        response = await submitSuccessStory(submitData)
      }

      console.log('Submit response status:', response.status)
      const result = response.data || {}

      if (!response.ok) {
        throw new Error(result.message || `Request failed with status ${response.status}`)
      }

      // Reset form
      setFormData({
        title: '',
        story: '',
        currentPosition: currentAlumni?.designation || '',
        batch: currentAlumni?.session || currentAlumni?.graduation_year || '',
        imageUrl: null
      })
      setImagePreview(null)
      setImageFile(null)
      setEditingId(null)

      // Refresh stories from top
      setPage(1)
      setHasMore(true)

      // Show success message
      alert('Your success story has been posted! 🎉')
    } catch (err) {
      console.error('Failed to submit story:', err)
      setFormError(err.message || 'Failed to post your story. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleLoadMore = () => {
    setPage(prev => prev + 1)
  }

  const getCurrentOwnerPayload = () => {
    const hasAlumniId = Boolean(currentAlumni?.id)
    return {
      alumni_id: hasAlumniId ? currentAlumni.id : '',
      student_id: currentAlumni?.student_id || ''
    }
  }

  const getOwnStoriesFromFeed = () => {
    const owner = getCurrentOwnerPayload()
    const ownerName = String(currentAlumni?.name || '').trim().toLowerCase()
    const ownerBatch = String(currentAlumni?.session || currentAlumni?.graduation_year || '').trim().toLowerCase()

    return (Array.isArray(stories) ? stories : []).filter((story) => {
      if (owner.alumni_id && String(story.alumni_id || story.alumni?.id || '') === String(owner.alumni_id)) {
        return true
      }

      const storyName = String(story.alumni?.name || '').trim().toLowerCase()
      const storyBatch = String(story.batch || '').trim().toLowerCase()

      if (!ownerName || !storyName) {
        return false
      }

      return storyName === ownerName && (!ownerBatch || !storyBatch || storyBatch === ownerBatch)
    })
  }

  const fetchMyStories = async () => {
    try {
      if (!currentAlumni) return
      const owner = getCurrentOwnerPayload()
      const res = await getMySuccessStories(owner)
      const data = res.data || {}
      if (res.ok && data.success) {
        const fetchedStories = Array.isArray(data.data) ? data.data : []
        setMyStories(fetchedStories.length > 0 ? fetchedStories : getOwnStoriesFromFeed())
      } else {
        console.error('Failed to fetch my stories', data)
        setMyStories(getOwnStoriesFromFeed())
      }
    } catch (err) {
      console.error('Error fetching my stories', err)
      setMyStories(getOwnStoriesFromFeed())
    }
  }

  useEffect(() => {
    if (showMyStories) {
      setMyStories(getOwnStoriesFromFeed())
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showMyStories, stories, currentAlumni?.id, currentAlumni?.student_id, currentAlumni?.name, currentAlumni?.session, currentAlumni?.graduation_year])

  const handleEdit = (story) => {
    setFormData({
      title: story.title || '',
      story: story.story || '',
      currentPosition: story.current_position || '',
      batch: story.batch || '',
      imageUrl: story.image_url || null
    })
    setEditingId(story.id)
    // switch to form view
    setShowMyStories(false)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this story? This action cannot be undone.')) return
    try {
      const owner = getCurrentOwnerPayload()
      const res = await deleteSuccessStory(id, owner)
      const data = res.data || {}
      if (res.ok && data.success) {
        setMyStories(prev => prev.filter(s => s.id !== id))
        // refresh public feed
        setPage(1)
        setHasMore(true)
        fetchStories(true)
      } else {
        alert(data.message || 'Failed to delete')
      }
    } catch (err) {
      console.error('Delete failed', err)
      alert('Failed to delete story')
    }
  }

  const formatDate = (isoString) => {
    const date = new Date(isoString)
    const now = new Date()
    const diffMs = now - date
    const diffSecs = Math.floor(diffMs / 1000)
    const diffMins = Math.floor(diffSecs / 60)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffDays > 0) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
    if (diffHours > 0) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    if (diffMins > 0) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
    return 'Just now'
  }

  const fetchComments = async (storyId) => {
    try {
      setCommentsMap(prev => ({ ...prev, [storyId]: { ...(prev[storyId] || {}), loading: true } }))
      const res = await getStoryComments(storyId)
      if (res && res.ok) {
        const list = Array.isArray(res.data) ? res.data : (res.data?.data || [])
        setCommentsMap(prev => ({ ...prev, [storyId]: { comments: list, loading: false, open: true } }))
        // Update the story's comment count to reflect actual count
        setStories(prev => (Array.isArray(prev) ? prev.map(s => s.id === storyId ? { ...s, comment_count: list.length } : s) : prev))
      } else {
        setCommentsMap(prev => ({ ...prev, [storyId]: { comments: [], loading: false, open: true } }))
      }
    } catch (err) {
      console.error('Failed to fetch comments', err)
      setCommentsMap(prev => ({ ...prev, [storyId]: { comments: [], loading: false, open: true } }))
    }
  }

  const toggleComments = (storyId) => {
    const entry = commentsMap[storyId]
    if (!entry || (!entry.comments || entry.comments.length === 0)) {
      fetchComments(storyId)
    } else {
      setCommentsMap(prev => ({ ...prev, [storyId]: { ...entry, open: !entry.open } }))
    }
  }

  const handleSubmitComment = async (storyId, text, parentId = null) => {
    if (!text || !text.trim()) return
    const payload = {
      comment_text: text,
      parent_comment_id: parentId || null
    }
    if (currentAlumni?.id) payload.alumni_id = currentAlumni.id
    else if (currentAlumni?.student_id) payload.student_id = currentAlumni.student_id

    try {
      const res = await postStoryComment(storyId, payload)
      if (res && res.ok && res.data && res.data.comment) {
        const created = res.data.comment
        setCommentsMap(prev => {
          const existing = prev[storyId]?.comments || []
          return { ...prev, [storyId]: { ...(prev[storyId] || {}), comments: [...existing, created], open: true } }
        })
        // Update the story's comment count
        setStories(prev => (Array.isArray(prev) ? prev.map(s => s.id === storyId ? { ...s, comment_count: (s.comment_count || 0) + 1 } : s) : prev))
      } else {
        console.error('Failed to post comment', res)
        alert(res?.data?.message || 'Failed to post comment')
      }
    } catch (err) {
      console.error('Failed to post comment', err)
      alert('Failed to post comment')
    }
  }

  const handleToggleReact = async (story) => {
    if (!currentAlumni || (!currentAlumni.id && !currentAlumni.student_id)) {
      alert('Please login to react')
      return
    }
    try {
      const payload = {}
      if (currentAlumni.id) payload.alumni_id = currentAlumni.id
      if (currentAlumni.student_id) payload.student_id = currentAlumni.student_id
      const res = await postStoryReact(story.id, payload)
      if (res && res.ok && res.data) {
        const reacted = !!res.data.reacted
        const count = Number(res.data.count || 0)
        setStories(prev => (Array.isArray(prev) ? prev.map(s => s.id === story.id ? { ...s, reaction_count: count, viewer_reacted: reacted } : s) : prev))
      } else {
        console.error('React failed', res)
      }
    } catch (err) {
      console.error('React error', err)
    }
  }

  const handleGoToShareStory = () => {
    setShowMyStories(false)
    setEditingId(null)
    // Ensure the form is visible first, then scroll into view.
    setTimeout(() => {
      formCardRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 0)
  }

  return (
    <div className="ss-container">
      {/* Header */}
      <div className="ss-header">
        <div className="ss-header-inner">
          <h1 className="ss-title">Success Stories</h1>
          <p className="ss-subtitle">Inspire and share your journey</p>
        </div>
        <div className="ss-header-actions">
          <button
            type="button"
            className="ss-plus-btn"
            onClick={handleGoToShareStory}
            aria-label="Go to Share Your Story"
            title="Share Your Story"
          >
            <i className="fa-solid fa-plus" />
          </button>
          <button type="button" className={`ss-tab-btn ${!showMyStories ? 'active' : ''}`} onClick={() => { setShowMyStories(false); setEditingId(null); }}>
            Share Story
          </button>
          <button type="button" className={`ss-tab-btn ${showMyStories ? 'active' : ''}`} onClick={() => { setShowMyStories(true); fetchMyStories(); }}>
            My Posted Stories
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="ss-content">
        {/* Left: Feed */}
        <div className="ss-feed-section">
          {error && (
            <div className="ss-alert ss-alert-error">
              <i className="fa-solid fa-exclamation-circle"></i>
              {error}
            </div>
          )}

          {loading ? (
            <div className="ss-loading">
              <div className="ss-spinner"></div>
              <p>Loading success stories...</p>
            </div>
          ) : stories.length === 0 ? (
            <div className="ss-empty">
              <i className="fa-solid fa-book-open"></i>
              <p>No stories yet. Be the first to share yours!</p>
            </div>
          ) : (
            <>
              <div className="ss-feed">
                {stories.map((story) => (
                  <div key={story.id} className="ss-story-card">
                    {story.image_url && (
                      <div className="ss-card-image">
                        <img
                          src={getUploadUrl(story.image_url)}
                          alt="Story"
                          onError={(e) => {
                            e.target.style.display = 'none'
                          }}
                        />
                      </div>
                    )}

                    <div className="ss-card-header">
                      <div className="ss-card-avatar">
                        <img
                          src={
                            story.alumni?.photo
                              ? getUploadUrl(story.alumni.photo)
                              : `https://ui-avatars.com/api/?name=${encodeURIComponent(story.alumni?.name || 'User')}&background=5f2c82&color=fff&size=48`
                          }
                          alt={story.alumni?.name || 'User'}
                        />
                      </div>

                      <div className="ss-card-meta">
                        <h3 className="ss-card-name">{story.alumni?.name || 'Anonymous'}</h3>
                        <p className="ss-card-position">
                          {story.current_position && (
                            <>
                              <i className="fa-solid fa-briefcase"></i>
                              {story.current_position}
                            </>
                          )}
                        </p>
                        <p className="ss-card-info">
                          {story.batch && (
                            <>
                              <i className="fa-solid fa-graduation-cap"></i>
                              Batch {story.batch}
                            </>
                          )}
                          {story.department && (
                            <>
                              <span className="ss-divider">•</span>
                              <i className="fa-solid fa-building"></i>
                              {story.department}
                            </>
                          )}
                        </p>
                      </div>

                      <span className="ss-card-time">{formatDate(story.created_at)}</span>
                    </div>

                    {story.title && (
                      <h2 className="ss-card-title">{story.title}</h2>
                    )}

                    <p className="ss-card-story">{story.story}</p>
                    <div className="ss-actions">
                      <button type="button" className={`ss-action-btn ${story.viewer_reacted ? 'reacted' : ''}`} onClick={() => handleToggleReact(story)}>
                        <i className="fa-solid fa-heart"></i>
                        <span className="ss-reaction-count">{story.reaction_count || 0}</span>
                      </button>

                      <button type="button" className="ss-action-btn" onClick={() => toggleComments(story.id)}>
                        <i className="fa-solid fa-comment"></i>
                        <span className="ss-reaction-count">{(commentsMap[story.id]?.comments?.length) ?? story.comment_count ?? 0}</span>
                      </button>
                    </div>

                    {commentsMap[story.id] && commentsMap[story.id].open && (
                      <div className="ss-comments-section">
                        {commentsMap[story.id].loading ? (
                          <p>Loading comments...</p>
                        ) : (
                          <>
                            {(commentsMap[story.id].comments || []).map((c) => (
                              <div key={c.id} className="ss-comment">
                                <div className="ss-comment-meta">
                                  <strong>{c.alumni_name || 'Anonymous'}</strong>
                                  <span className="ss-comment-time">{c.created_at}</span>
                                </div>
                                <div className="ss-comment-text">{c.comment_text}</div>
                              </div>
                            ))}

                            <div className="ss-comment-form">
                              <input type="text" placeholder="Write a comment..." className="ss-comment-input" id={`comment-input-${story.id}`} />
                              <button type="button" className="ss-submit-comment-btn" onClick={() => {
                                const el = document.getElementById(`comment-input-${story.id}`)
                                if (el) {
                                  const v = el.value
                                  handleSubmitComment(story.id, v)
                                  el.value = ''
                                }
                              }}>Post</button>
                            </div>
                          </>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {hasMore && (
                <div className="ss-load-more-container">
                  <button
                    className="ss-load-more-btn"
                    onClick={handleLoadMore}
                    disabled={loadingMore}
                  >
                    {loadingMore ? (
                      <>
                        <span className="ss-spinner-small"></span>
                        Loading...
                      </>
                    ) : (
                      <>
                        <i className="fa-solid fa-arrow-down"></i>
                        Load More Stories
                      </>
                    )}
                  </button>
                </div>
              )}
            </>
          )}
        </div>

        {/* Right: Form */}
        <div className="ss-form-section">
          <div className="ss-form-card" ref={formCardRef}>
            <div className="ss-form-heading">
              <h2 className="ss-form-title">{showMyStories ? 'My Posted Stories' : (editingId ? 'Edit Your Story' : 'Share Your Story')}</h2>
              <p className="ss-form-subtitle">Inspire others with your journey</p>
            </div>

            {formError && (
              <div className="ss-alert ss-alert-error">
                <i className="fa-solid fa-exclamation-circle"></i>
                {formError}
              </div>
            )}

            {showMyStories ? (
              <div className="ss-my-stories">
                {myStories.length === 0 ? (
                  <p>You haven't posted any stories yet.</p>
                ) : (
                  myStories.map(s => (
                    <div key={s.id} className="ss-my-story-item">
                      <h4>{s.title || 'Untitled'}</h4>
                      <p className="ss-my-story-text">{s.story}</p>
                      <div className="ss-my-story-actions">
                        <button type="button" className="ss-edit-btn" onClick={() => handleEdit(s)}>Edit</button>
                        <button type="button" className="ss-delete-btn" onClick={() => handleDelete(s.id)}>Delete</button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="ss-form">
              {/* Title */}
              <div className="ss-form-group">
                <label htmlFor="title" className="ss-label">
                  Story Title <span className="ss-optional">(Optional)</span>
                </label>
                <input
                  type="text"
                  id="title"
                  className="ss-input"
                  placeholder="e.g., From Graduation to CEO"
                  value={formData.title}
                  onChange={(e) =>
                    setFormData({ ...formData, title: e.target.value })
                  }
                  maxLength={255}
                />
              </div>

              {/* Story */}
              <div className="ss-form-group">
                <label htmlFor="story" className="ss-label">
                  Your Story <span className="ss-required">*</span>
                </label>
                <textarea
                  id="story"
                  className="ss-textarea"
                  placeholder="Share your success journey, achievements, and lessons learned..."
                  value={formData.story}
                  onChange={(e) =>
                    setFormData({ ...formData, story: e.target.value })
                  }
                  rows={6}
                />
                <p className="ss-char-count">
                  {formData.story.length} characters
                </p>
              </div>

              {/* Current Position */}
              <div className="ss-form-group">
                <label htmlFor="position" className="ss-label">
                  Current Position <span className="ss-optional">(Optional)</span>
                </label>
                <input
                  type="text"
                  id="position"
                  className="ss-input"
                  placeholder="e.g., Software Engineer at Tech Co"
                  value={formData.currentPosition}
                  onChange={(e) =>
                    setFormData({ ...formData, currentPosition: e.target.value })
                  }
                  maxLength={255}
                />
              </div>

              {/* Batch */}
              <div className="ss-form-row">
                <div className="ss-form-group">
                  <label htmlFor="batch" className="ss-label">
                    Batch <span className="ss-required">*</span>
                  </label>
                  <input
                    type="text"
                    id="batch"
                    className="ss-input"
                    placeholder="e.g., 2020"
                    value={formData.batch}
                    onChange={(e) =>
                      setFormData({ ...formData, batch: e.target.value })
                    }
                    maxLength={50}
                  />
                </div>

                <div className="ss-form-group">
                  <label htmlFor="department" className="ss-label">
                    Department
                  </label>
                  <input
                    type="text"
                    id="department"
                    className="ss-input"
                    value={currentAlumni?.department || 'ICE'}
                    disabled
                  />
                </div>
              </div>

              {/* Image upload removed per request */}

              {/* Submit Button */}
              <button
                type="submit"
                className="ss-submit-btn"
                disabled={submitting || !formData.story.trim()}
              >
                {submitting ? (
                  <>
                    <span className="ss-spinner-small"></span>
                    Posting...
                  </>
                ) : (
                  <>
                    <i className="fa-solid fa-paper-plane"></i>
                    Post Your Story
                  </>
                )}
              </button>
            </form>
              )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default SuccessStory
