import React, { useState } from 'react';
import axios from 'axios';
import './tailwind.output.css'; // Tailwind output CSS

const EmailConfirmationPrompt = ({ draft, onSendComplete }) => {
  if (!draft) return null; // Prevent rendering if draft is undefined

  const [subject, setSubject] = useState(draft.subject || '');
  const [message, setMessage] = useState(draft.confirmation_message || ''); // ✅ not confirmation_message
  const [isEditing, setIsEditing] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);

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
          calendar_link: draft.calendar_link, // optional, can be omitted
          to_emails: draft.to_emails,
          subject: subject,
          requires_confirmation: true
      });
      onSendComplete(); // optional callback to notify parent
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
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        className="w-full border px-3 py-2 rounded mb-4 h-40"
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
