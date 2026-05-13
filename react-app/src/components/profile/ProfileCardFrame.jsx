import React from 'react'
import '../../styles/profile-page.css'

/**
 * ProfileCardFrame: A reusable wrapper that renders profile content in a card layout.
 * Encapsulates the `.profile-page`, `.profile-device`, and `.profile-cardboard` structure.
 * 
 * Props:
 * - children: ReactNode - Content to display inside the card (rendered after the Back button)
 * - onBack: Function - Handler for the Back button click
 */
export default function ProfileCardFrame({ children, onBack }) {
  return (
    <div className="profile-page profile-page--card-mode">
      <div className="profile-page__ambient" />
      <main className="profile-page__shell profile-page__shell--card-mode">
        <section className="profile-device">
          <div className="profile-device__frame">
            <div className="profile-device__topbar" />
            <article className="profile-cardboard">
              <div className="profile-cardboard__crest">RU</div>
              {onBack && (
                <button
                  type="button"
                  className="profile-cardboard__back"
                  onClick={onBack}
                  aria-label="Go back"
                >
                  <i className="fa-solid fa-arrow-left" /> Back
                </button>
              )}
              {children}
            </article>
          </div>
        </section>
      </main>
    </div>
  )
}
