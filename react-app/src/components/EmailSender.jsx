/**
 * EmailSender.jsx - Reusable React component for sending emails via AlumniConnect API
 *
 * Features:
 * - Send single or bulk emails
 * - Form validation
 * - Loading states
 * - Error handling
 * - Success feedback
 * - Support for both public and admin endpoints
 *
 * Usage:
 * import EmailSender from './EmailSender';
 * <EmailSender mode="admin" adminToken={token} />
 */

import React, { useState } from 'react';
import './EmailSender.css';
import { getAPIBaseURL } from '../services/api';

const EmailSender = ({ mode = 'admin', adminToken = null, onSuccess = null, onError = null }) => {
  const [formData, setFormData] = useState({
    recipientEmails: '',
    subject: '',
    message: '',
    preheader: '',
    ctaText: 'Visit AlumniConnect',
  });

  const [status, setStatus] = useState({
    isLoading: false,
    message: '',
    type: '', // 'success', 'error', 'info'
  });

  const API_URL = getAPIBaseURL();

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Validate form
  const validateForm = () => {
    if (!formData.recipientEmails.trim()) {
      setStatus({ isLoading: false, message: 'Please enter recipient email(s)', type: 'error' });
      return false;
    }

    if (!formData.subject.trim()) {
      setStatus({ isLoading: false, message: 'Please enter email subject', type: 'error' });
      return false;
    }

    if (!formData.message.trim()) {
      setStatus({ isLoading: false, message: 'Please enter email message', type: 'error' });
      return false;
    }

    // Validate email format
    const emailRegex = /^[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}$/i;
    const emails = formData.recipientEmails.split(',').map((e) => e.trim());

    for (let email of emails) {
      if (!emailRegex.test(email)) {
        setStatus({ isLoading: false, message: `Invalid email format: ${email}`, type: 'error' });
        return false;
      }
    }

    return true;
  };

  // Send email
  const handleSendEmail = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    setStatus({ isLoading: true, message: 'Sending email...', type: 'info' });

    try {
      const emails = formData.recipientEmails.split(',').map((e) => e.trim());

      const payload = {
        recipient_emails: emails,
        subject: formData.subject,
        message: formData.message,
        preheader: formData.preheader || formData.subject,
        cta_text: formData.ctaText,
      };

      const headers = {
        'Content-Type': 'application/json',
      };

      // Add authentication if admin mode
      if (mode === 'admin' && adminToken) {
        headers['Authorization'] = `Bearer ${adminToken}`;
      }

      const response = await fetch(`${API_URL}/api/email/send`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setStatus({
          isLoading: false,
          message: `✓ ${data.message}`,
          type: 'success',
        });

        // Clear form on success
        setFormData({
          recipientEmails: '',
          subject: '',
          message: '',
          preheader: '',
          ctaText: 'Visit AlumniConnect',
        });

        // Call success callback if provided
        if (onSuccess) {
          onSuccess(data);
        }
      } else {
        const errorMsg = data.message || 'Failed to send email';
        setStatus({
          isLoading: false,
          message: `✗ ${errorMsg}`,
          type: 'error',
        });

        if (onError) {
          onError(data);
        }
      }
    } catch (error) {
      console.error('Error sending email:', error);
      setStatus({
        isLoading: false,
        message: `✗ Network error: ${error.message}`,
        type: 'error',
      });

      if (onError) {
        onError(error);
      }
    }
  };

  return (
    <div className="email-sender-container">
      <div className="email-sender-card">
        <h2 className="email-sender-title">
          📧 Send Email
          {mode === 'admin' && ' (Admin)'}
        </h2>

        {/* Status Message */}
        {status.message && (
          <div className={`email-sender-status email-sender-status--${status.type}`}>
            {status.message}
          </div>
        )}

        <form onSubmit={handleSendEmail} className="email-sender-form">
          {/* Recipient Emails */}
          <div className="email-sender-group">
            <label htmlFor="recipientEmails" className="email-sender-label">
              Recipient Email(s) *
            </label>
            <textarea
              id="recipientEmails"
              name="recipientEmails"
              placeholder="Enter email addresses separated by commas&#10;e.g., user1@example.com, user2@example.com"
              value={formData.recipientEmails}
              onChange={handleChange}
              className="email-sender-textarea"
              rows="3"
              disabled={status.isLoading}
            />
            <small className="email-sender-help">
              Separate multiple emails with commas
            </small>
          </div>

          {/* Subject */}
          <div className="email-sender-group">
            <label htmlFor="subject" className="email-sender-label">
              Email Subject *
            </label>
            <input
              id="subject"
              name="subject"
              type="text"
              placeholder="e.g., Welcome to AlumniConnect"
              value={formData.subject}
              onChange={handleChange}
              className="email-sender-input"
              disabled={status.isLoading}
            />
          </div>

          {/* Message */}
          <div className="email-sender-group">
            <label htmlFor="message" className="email-sender-label">
              Email Message *
            </label>
            <textarea
              id="message"
              name="message"
              placeholder="Enter your email message here..."
              value={formData.message}
              onChange={handleChange}
              className="email-sender-textarea"
              rows="6"
              disabled={status.isLoading}
            />
            <small className="email-sender-help">
              Supports plain text. HTML formatting will be applied automatically.
            </small>
          </div>

          {/* Preheader (Optional) */}
          <div className="email-sender-group">
            <label htmlFor="preheader" className="email-sender-label">
              Email Preheader (Optional)
            </label>
            <input
              id="preheader"
              name="preheader"
              type="text"
              placeholder="Preview text shown in email clients (defaults to subject)"
              value={formData.preheader}
              onChange={handleChange}
              className="email-sender-input"
              disabled={status.isLoading}
            />
            <small className="email-sender-help">
              This text appears in email client previews
            </small>
          </div>

          {/* CTA Text (Optional) */}
          <div className="email-sender-group">
            <label htmlFor="ctaText" className="email-sender-label">
              Call-to-Action Button Text (Optional)
            </label>
            <input
              id="ctaText"
              name="ctaText"
              type="text"
              placeholder="e.g., View Message"
              value={formData.ctaText}
              onChange={handleChange}
              className="email-sender-input"
              disabled={status.isLoading}
            />
            <small className="email-sender-help">
              Text for the button in the email (default: "Visit AlumniConnect")
            </small>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="email-sender-button"
            disabled={status.isLoading}
          >
            {status.isLoading ? 'Sending...' : 'Send Email'}
          </button>
        </form>

        {/* Info Box */}
        <div className="email-sender-info">
          <h4>💡 Tips</h4>
          <ul>
            <li>Use plain text in the message field - formatting is applied automatically</li>
            <li>Enter multiple recipients separated by commas</li>
            <li>The email will include your organization's branding and footer</li>
            <li>Emails are logged in the system for auditing</li>
            {mode === 'admin' && <li>Only admin users can send bulk emails</li>}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default EmailSender;
