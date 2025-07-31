import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const EmailConfirmationPrompt = ({ draft, onSendComplete }) => {
  if (!draft) return null;

  const [subject, setSubject] = useState(draft.subject || '');
  const [message, setMessage] = useState(draft.confirmation_message || '');
  const [isEditing, setIsEditing] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const textareaRef = useRef(null);

  const autoResizeTextarea = () => {
  const text_area = textareaRef.current;
  if (text_area) {
    text_area.style.height = 'auto';
    text_area.style.height = `${text_area.scrollHeight}px`; // ✅ use `text_area` here
    }
  };


  const handleInputChange = (e) => {
    setMessage(e.target.value);
    autoResizeTextarea();
  };

  useEffect(() => {
    autoResizeTextarea();
  }, [isEditing, message]);

  useEffect(() => {
  if (draft) {
    setSubject(draft.subject || '');
    setMessage(draft.confirmation_message || '');
    }
  }, [draft]);

  const handleSend = async () => {
      setSending(true);
      setError(null);

      // Check if calendar link is already present in the message
      const linkAlreadyIncluded = message.includes(draft.calendar_link) ||
                                  message.includes("calendar/event?eid=");

      const messageWithLink = linkAlreadyIncluded
        ? message
        : `${message}

    You can view further details and access the event using the following calendar link: [Join the Event](${draft.calendar_link})`;

      try {
        await axios.post("https://calendar-agent-app.com/send_confirmation_email", {
          confirmation_message: messageWithLink,
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
