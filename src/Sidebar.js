// Sidebar.js
import React from 'react';

const Sidebar = ({ conversations, activeConversation, setActiveConversation, deleteConversation, createNewConversation }) => {
  return (
    <div className="sidebar">
      <button onClick={createNewConversation} className="new-conversation-button">New Conversation</button>
      <ul>
        {conversations.map((conversation, index) => (
          <li key={index}>
            <button
              onClick={() => setActiveConversation(index)}
              className={activeConversation === index ? 'active-conversation' : ''}
            >
              {conversation.title}
            </button>
            <button onClick={() => deleteConversation(index)} className="delete-button">Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Sidebar;