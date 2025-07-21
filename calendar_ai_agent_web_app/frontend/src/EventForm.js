import React, { useState } from 'react';
import axios from 'axios';

const EventForm = () => {
    const [eventDescription, setEventDescription] = useState('');
    const [participants, setParticipants] = useState('');
    const [confirmation, setConfirmation] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:8000/process', {
              user_input: eventDescription,
              participants: participants.split(',')
            });
            setConfirmation(response.data);
        } catch (error) {
            console.error('Error processing the event', error);
        }
    };

    return (
        <div>
            <h2>Schedule Your Event</h2>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Event Description:</label>
                    <textarea
                        value={eventDescription}
                        onChange={(e) => setEventDescription(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>Participants Emails: </label>
                    <input
                        type="text"
                        value={participants}
                        placeholder="email1@example.com, email2@example.com"
                        onChange={(e) => setParticipants(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">Submit</button>
            </form>
            {confirmation && (
                <div>
                    <h3>Response:</h3>
                    {confirmation.error ? (
                        <p style={{ color: 'red' }}>{confirmation.error}</p>
                    ) : (
                        <>
                            <p>{confirmation.confirmation_message}</p>
                            {confirmation.calendar_link && (
                                <a href={confirmation.calendar_link} target="_blank" rel="noopener noreferrer">
                                    View Calendar Event
                                </a>
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    );
};

export default EventForm;
