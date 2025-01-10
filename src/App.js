import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css'; // For styling

const App = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Scroll to the bottom of the chat when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle sending a query
  const handleSendQuery = async () => {
    if (!query.trim() || isLoading) return;

    setIsLoading(true);
    setMessages((prev) => [...prev, { role: 'user', content: query }]);
    setQuery('');

    try {
      const response = await axios.post('http://localhost:1255/search', {
        query,
        context: messages.filter((msg) => msg.role !== 'useringr'), // Include past AI responses as context
      });

      const aiResponse = response.data.choices[0].message.content;
      setMessages((prev) => [...prev, { role: 'assistant', content: aiResponse }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages((prev) => [...prev, { role: 'assistant', content: 'An error occurred. Please try again.' + error }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="chat-container">
        <div className="messages">
          {messages.map((msg, index) => (
            <React.Fragment key={index}>
              {msg.role === 'user' ? (
                <h1 className="user-query">{msg.content}</h1>
              ) : (
                <p className="ai-response">
                  {msg.content.split(' ').map((word, wordIndex) => (
                    <span key={wordIndex} className="fade-in-word" style={{ animationDelay: `${wordIndex * 0.1}s` }}>
                      {word}{' '}
                    </span>
                  ))}
                </p>
              )}
              {index < messages.length - 1 && <hr className="divider" />}
            </React.Fragment>
          ))}
          <div ref={messagesEndRef} />
        </div>
        <div className="input-container">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendQuery()}
            placeholder="Ask me anything..."
            disabled={isLoading}
          />
          <button onClick={handleSendQuery} disabled={isLoading}>
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;