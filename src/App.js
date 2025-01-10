import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { InlineMath, BlockMath } from 'react-katex';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css'; // Import KaTeX CSS
import './App.css'; // For styling

const App = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [streamingResponse, setStreamingResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false); // New state for streaming
  const messagesEndRef = useRef(null);

  // Scroll to the bottom of the chat when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingResponse]);

  // Handle sending a query
  const handleSendQuery = async () => {
    if (!query.trim() || isLoading) return;
    setIsLoading(true);
    setIsStreaming(true); // Set streaming to true
    setMessages((prev) => [...prev, { role: 'user', content: query }]);
    setQuery('');

    try {
      const response = await fetch('http://localhost:1255/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          context: messages.filter((msg) => msg.role !== 'useringr'),
        }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let aiResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        aiResponse += chunk;

        // Update the streaming response incrementally
        setStreamingResponse((prev) => prev + chunk);
      }

      // Add the final response to the messages
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: aiResponse },
      ]);

      setStreamingResponse(''); // Clear the streaming response
    } catch (error) {
      console.error('Error:', error);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'An error occurred. Please try again.' + error },
      ]);
    } finally {
      setIsLoading(false);
      setIsStreaming(false); // Set streaming to false
    }
  };

  // Handle resetting the conversation
  const handleResetConversation = () => {
    setMessages([]);
    setStreamingResponse('');
  };

  // Handle opening a new tab
  const handleOpenNewTab = () => {
    window.open('http://localhost:3000', '_blank');
  };

  return (
    <div className="app">
      <div className="header">
        <button className="reset-button" onClick={handleResetConversation}>
          Reset Conversation
        </button>
        <button className="new-tab-button" onClick={handleOpenNewTab}>
          New Tab
        </button>
      </div>
      <div className="chat-container">
        <div className="messages">
          {messages.map((msg, index) => (
            <React.Fragment key={index}>
              {msg.role === 'user' ? (
                <div className="user-query">
                  <ReactMarkdown
                    remarkPlugins={[remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                    components={{
                      math: ({ node, inline, ...props }) =>
                        inline ? <InlineMath {...props} /> : <BlockMath {...props} />,
                      inlineMath: ({ node, ...props }) => <InlineMath {...props} />,
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className="ai-response">
                  <ReactMarkdown
                    remarkPlugins={[remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                    components={{
                      math: ({ node, inline, ...props }) =>
                        inline ? <InlineMath {...props} /> : <BlockMath {...props} />,
                      inlineMath: ({ node, ...props }) => <InlineMath {...props} />,
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
              )}
              {index < messages.length - 1 && <hr className="divider" />}
            </React.Fragment>
          ))}
          {/* Render the streaming response incrementally */}
          {streamingResponse && (
            <div className="ai-response">
              <ReactMarkdown
                remarkPlugins={[remarkMath]}
                rehypePlugins={[rehypeKatex]}
                components={{
                  math: ({ node, inline, ...props }) =>
                    inline ? <InlineMath {...props} /> : <BlockMath {...props} />,
                  inlineMath: ({ node, ...props }) => <InlineMath {...props} />,
                }}
              >
                {streamingResponse}
              </ReactMarkdown>
            </div>
          )}
          {/* Subdued text during streaming */}
          {isStreaming && (
            <div className="subdued-text">
              Generation may take a while to begin
            </div>
          )}
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