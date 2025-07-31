import React from 'react';
import ReactDOM from 'react-dom/client';
import EventForm from './EventForm';
import EmailConfirmationPrompt from './EmailConfirmationPrompt'
import './index.css'; // 👈 MUST be imported here

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <EventForm />
    <EmailConfirmationPrompt />
  </React.StrictMode>
);
