import React from 'react'
import { Container, Row, Col } from 'react-bootstrap'
import '../styles/meet-the-team.css'

function MeetTheTeam() {
  const creators = [
    {
      name: 'S. M ABDULLAH AL SHAWON',
      session: '2022-23',
      role: 'Frontend Developer',
      description: 'Passionate about creating beautiful and intuitive user interfaces. Specialized in React and modern web technologies.',
      linkedin: '#',
      github: '#',
      email: 'dev1@alumni.edu'
    },
    {
      name: 'PARVEJ MOSHAROF',
      session: '2022-23',
      role: 'Backend Developer',
      description: 'Expert in building scalable and robust server-side applications. Proficient with Python, databases, and APIs.',
      linkedin: '#',
      github: '#',
      email: 'dev2@alumni.edu'
    },
    {
      name: 'MEHEDI HASAN',
      session: '2022-23',
      role: 'UI/UX Designer',
      description: 'Creative designer focused on user experience and visual design. Committed to crafting elegant digital solutions.',
      linkedin: '#',
      github: '#',
      email: 'dev3@alumni.edu'
    }
  ]

  return (
    <section className="meet-the-team-section">
      <Container fluid>
        <div className="team-header">
          <p className="team-tagline">BUILT BY STUDENTS, GUIDED BY EXPERTS</p>
          <h2 className="team-title">
            Meet the Team Behind <span className="highlight">AlumniConnect</span>
          </h2>
          <p className="team-description">
            A passionate team of students and our mentor working together to build a stronger community.
          </p>
        </div>

        <div className="team-content">
          {/* Creators Section */}
          <div className="creators-section">
            <div className="section-label">👨‍💻 Our Creators</div>
            <div className="creators-grid">
              {creators.map((creator, idx) => (
                <div className="creator-cell" key={idx}>
                  <div className="creator-card">
                    <div className="photo-frame">
                      <div className="placeholder-avatar creator-avatar">
                        <i className="fas fa-user"></i>
                      </div>
                    </div>
                    <h3 className="creator-name">{creator.name}</h3>
                    {creator.session && <p className="creator-session">{creator.session}</p>}
                    <p className="creator-role">{creator.role}</p>
                    <p className="creator-description">{creator.description}</p>
                    <div className="social-icons">
                      <a href={creator.linkedin} className="social-link" title="LinkedIn">
                        <i className="fab fa-linkedin-in"></i>
                      </a>
                      <a href={creator.github} className="social-link" title="GitHub">
                        <i className="fab fa-github"></i>
                      </a>
                      <a href={`mailto:${creator.email}`} className="social-link" title="Email">
                        <i className="fas fa-envelope"></i>
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Container>
    </section>
  )
}

export default MeetTheTeam
