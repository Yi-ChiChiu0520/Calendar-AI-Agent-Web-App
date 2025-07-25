import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './tailwind.output.css'; // Tailwind output CSS

const EmailConfirmationPrompt = ({ draft, onSendComplete }) => {
  if (!draft) return null;

  const [subject, setSubject] = useState(draft.subject || '');
  const [message, setMessage] = useState(draft.confirmation_message || '');
  const [isEditing, setIsEditing] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const textareaRef = useRef(null);

  const autoResizeTextarea = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  };

  const handleInputChange = (e) => {
    setMessage(e.target.value);
    autoResizeTextarea();
  };

  useEffect(() => {
    autoResizeTextarea();
  }, [isEditing, message]);

  const handleSend = async () => {
    setSending(true);
    setError(null);
    try {
      console.log({
        confirmation_message: message,
        calendar_link: draft.calendar_link,
        to_emails: draft.to_emails,
        subject: subject,
        requires_confirmation: true
      });

      await axios.post('http://localhost:8000/send_confirmation_email', {
        confirmation_message: message,
        calendar_link: draft.calendar_link,
        to_emails: draft.to_emails,
        subject: subject,
        requires_confirmation: true
      });

      onSendComplete();
    } catch (err) {
      setError('Failed to send email. Please try again.');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-6 p-6 border rounded-lg shadow">
      <h3 className="text-xl font-semibold mb-2">✉️ Review Email Before Sending</h3>

      <label className="block text-sm font-medium mb-1">Subject</label>
      <input
        type="text"
        value={subject}
        onChange={(e) => setSubject(e.target.value)}
        className="w-full border px-3 py-2 rounded mb-4"
        disabled={!isEditing}
      />

      <label className="block text-sm font-medium mb-1">Message</label>
      <textarea
        ref={textareaRef}
        value={message}
        onChange={handleInputChange}
        className="w-full border px-3 py-2 rounded mb-4 resize-none overflow-hidden"
        disabled={!isEditing}
      />

      {error && <p className="text-red-500 mb-4">{error}</p>}

      <div className="flex gap-3">
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="px-4 py-2 bg-yellow-500 text-black rounded hover:bg-yellow-600"
          >
            ✏️ Edit
          </button>
        )}
        <button
          onClick={handleSend}
          disabled={sending}
          className="px-4 py-2 bg-green-600 text-black rounded hover:bg-green-700"
        >
          {sending ? 'Sending...' : '✅ Send Email'}
        </button>
      </div>
    </div>
  );
};

export default EmailConfirmationPrompt;
