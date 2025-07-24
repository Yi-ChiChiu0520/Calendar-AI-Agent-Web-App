import React, { useState } from 'react';
import axios from 'axios';
import './tailwind.output.css'; // Tailwind output CSS

const EventForm = () => {
    const [eventDescription, setEventDescription] = useState('');
    const [participants, setParticipants] = useState('');
    const [confirmation, setConfirmation] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:8000/process', {
                user_input: eventDescription,
                participants: participants.split(',').map(email => email.trim())
            });
            setConfirmation(response.data);
        } catch (error) {
            console.error('Error processing the event', error);
            setConfirmation({ error: 'An error occurred while processing your request.' });
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

                {/* Form Card */}
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
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            className="w-full bg-blue-600 text-black py-3 rounded-md font-semibold hover:bg-blue-700 transition"
                        >
                            Submit
                        </button>
                    </form>
                </div>

                {/* AI Response */}
                {confirmation && (
                    <div className="bg-white rounded-xl shadow p-6">
                        <h3 className="text-lg font-semibold text-gray-800 mb-2">🧠 AI Response</h3>
                        <div className="text-gray-700 whitespace-pre-line">
                            {confirmation.error ? (
                                <p className="text-red-500 font-medium">{confirmation.error}</p>
                            ) : (
                                <>
                                    <p>{confirmation.confirmation_message}</p>
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
            </div>
        </div>
    );
};

export default EventForm;
