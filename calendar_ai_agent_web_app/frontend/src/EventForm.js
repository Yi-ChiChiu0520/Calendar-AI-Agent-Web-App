import React, { useState } from 'react';
import axios from 'axios';
import EmailConfirmationPrompt from './EmailConfirmationPrompt';

const EventForm = () => {
    const [eventDescription, setEventDescription] = useState('');
    const [participants, setParticipants] = useState('');
    const [confirmation, setConfirmation] = useState(null);
    const [draft, setDraft] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const response = await axios.post('https://calendar-agent-app.com/process', {
                user_input: eventDescription,
                participants: participants.split(',').map(email => email.trim())
            });

            const data = response.data;

            if (data.confirmation_message && data.requires_confirmation) {
                setDraft({
                    requires_confirmation: true,
                    subject: data.subject || "Meeting Confirmation",
                    confirmation_message: data.confirmation_message,
                    to_emails: participants.split(',').map(email => email.trim()),
                    calendar_link: data.calendar_link
                });
                setConfirmation(null);
            } else {
                setConfirmation(data);
                setDraft(null);
            }
        } catch (error) {
            console.error('Error processing the event', error);
            setConfirmation({ error: 'An error occurred while processing your request.' });
            setDraft(null);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 py-10 px-4 flex justify-center items-start">
            <div className="w-full max-w-2xl space-y-6">
                {/* Header */}
                <div className="text-center">
                    <h2 className="text-3xl font-bold text-gray-800">📅 Calendar AI Assistant</h2>
                    <p className="text-gray-500 mt-1">Schedule or reschedule your meetings with natural language</p>
                </div>

                {/* Form */}
                <div className="bg-white rounded-xl shadow p-6">
                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div>
                            <label htmlFor="eventDescription" className="block text-sm font-medium text-gray-700 mb-1">
                                Event Description
                            </label>
                            <textarea
                                id="eventDescription"
                                rows="4"
                                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none"
                                placeholder="e.g. Move the meeting with Ethan from Thursday 6–7am to Friday 7–8am"
                                value={eventDescription}
                                onChange={(e) => setEventDescription(e.target.value)}
                                required
                                disabled={loading}
                            />
                        </div>

                        <div>
                            <label htmlFor="participants" className="block text-sm font-medium text-gray-700 mb-1">
                                Participants Emails
                            </label>
                            <input
                                type="text"
                                id="participants"
                                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none"
                                placeholder="email1@example.com, email2@example.com"
                                value={participants}
                                onChange={(e) => setParticipants(e.target.value)}
                                disabled={loading}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className={`w-full py-3 rounded-md font-semibold transition ${
                                loading
                                    ? 'bg-gray-400 text-white cursor-not-allowed'
                                    : 'bg-blue-600 text-black hover:bg-blue-700'
                            }`}
                        >
                            {loading ? 'Submitting...' : 'Submit'}
                        </button>
                    </form>
                </div>

                {/* Chat-based confirmation */}
                {draft && draft.requires_confirmation && (
                    <EmailConfirmationPrompt
                        draft={draft}
                        onSendComplete={() => {
                            alert('✅ Email sent!');
                            setDraft(null);
                        }}
                    />
                )}

                {/* Normal AI Response */}
                {confirmation && (
                    <div className="bg-white rounded-xl shadow p-6">
                        <h3 className="text-lg font-semibold text-gray-800 mb-2">🧠 AI Response</h3>
                        <div className="text-gray-700 whitespace-pre-line">
                            {confirmation.error ? (
                                <p className="text-red-500 font-medium">{confirmation.error}</p>
                            ) : (
                                <>
                                    <p>{confirmation.confirmation_message || confirmation.message}</p>
                                    {confirmation.calendar_link && (
                                        <a
                                            href={confirmation.calendar_link}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="inline-block mt-4 text-green-600 hover:underline font-medium"
                                        >
                                            ➜ View Calendar Event
                                        </a>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                )}

                {Optional: Loading indicator}
                {{loading && <p className="text-center text-sm text-gray-500">🔄 Processing your request...</p>}}
            </div>
        </div>
    );
};

export default EventForm;
