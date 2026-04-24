import React, { useState } from 'react';
import { MessageCircle, X, Send } from 'lucide-react';
import '../styles/Chatbot.css'; // We will create this file next

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { text: "Hello! I'm your Coffee Expert. How can I help you with your coffee plants today?", isBot: true }
  ]);

  const toggleChat = () => setIsOpen(!isOpen);

  const handleSend = async () => {
    if (!input.trim()) return;

    // 1. Add User Message to UI
    const userMsg = { text: input, isBot: false };
    setMessages((prev) => [...prev, userMsg]);
    const currentInput = input;
    setInput("");

    try {
      // 2. Send to Backend
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: currentInput }),
      });
      const data = await response.json();

      // 3. Add Bot Reply to UI
      setMessages((prev) => [...prev, { text: data.reply, isBot: true }]);
    } catch (error) {
      setMessages((prev) => [...prev, { text: "Connection error. Is the backend running?", isBot: true }]);
    }
  };

  return (
    <div className="chatbot-wrapper">
      {/* The Chat Window */}
      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <span>Coffee Assistant</span>
            <X className="close-icon" onClick={toggleChat} size={20} />
          </div>
          
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <div key={index} className={`message-bubble ${msg.isBot ? 'bot' : 'user'}`}>
                {msg.text}
              </div>
            ))}
          </div>

          <div className="chat-footer">
            <input 
              type="text" 
              value={input} 
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask about coffee..."
            />
            <button onClick={handleSend}>
              <Send size={18} />
            </button>
          </div>
        </div>
      )}

      {/* The Floating Button */}
      <button className="chat-fab" onClick={toggleChat}>
        <MessageCircle size={30} color="white" />
      </button>
    </div>
  );
};

export default Chatbot;