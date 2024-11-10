import React, { useState, useRef, useEffect } from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { ChatBubble, ChatBubbleMessage } from '@/components/ui/chat/chat-bubble';
import { ChatInput } from '@/components/ui/chat/chat-input';
import { CornerDownLeft } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';

type Message = {
  id: number;
  role: 'user' | 'assistant';
  message: string;
  isLoading?: boolean;
};

type ChatWidgetProps = {
  onCombinedAssessmentResult: (city: string) => Promise<void>;
};

const ChatWidget: React.FC<ChatWidgetProps> = ({ onCombinedAssessmentResult }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesContainerRef.current?.scrollTo(0, messagesContainerRef.current.scrollHeight);
  }, [messages]);

  const addMessage = (role: 'user' | 'assistant', text: string) => {
    const newMessage = { id: Date.now(), role, message: text };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleSendMessage = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim().toLowerCase();

    if (userMessage.startsWith('calculate energy in ')) {
      const cityName = userMessage.replace('calculate energy in ', '').trim();
      setIsLoading(true);
      try {
        await onCombinedAssessmentResult(cityName);
        addMessage('assistant', `Energy assessment for ${cityName} has been completed.`);
      } catch (error) {
        addMessage('assistant', 'Error: Unable to perform energy assessment. Please try again.');
        console.error(error);
      } finally {
        setIsLoading(false);
      }
    } else {
      addMessage('user', input.trim());
      setInput('');
      setIsLoading(true);

      try {
        const response = await fetch('http://127.0.0.1:8000/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: input.trim() }),
        });

        const data = await response.json();
        if (response.ok) {
          addMessage('assistant', data.response);
        } else {
          addMessage('assistant', 'Error: Unable to fetch response. Please try again later.');
        }
      } catch (error) {
        addMessage('assistant', 'Error: Unable to fetch response. Please try again later.');
        console.error(error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="w-full lg:w-[28rem] h-full shadow-lg rounded-lg overflow-hidden bg-white border">
      <div className="relative flex flex-col h-full p-2">
        <div ref={messagesContainerRef} className="overflow-y-auto flex-grow max-h-[20rem] p-2">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="flex flex-col gap-2"
              >
                <ChatBubble variant={message.role === 'assistant' ? 'received' : 'sent'}>
                  <Avatar>
                    <AvatarImage src={message.role === 'assistant' ? '/bot-avatar.png' : '/user-avatar.png'} />
                    <AvatarFallback>{message.role === 'assistant' ? '🤖' : 'U'}</AvatarFallback>
                  </Avatar>
                  <ChatBubbleMessage isLoading={message.isLoading}>
                    {message.message}
                  </ChatBubbleMessage>
                </ChatBubble>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
        
        <form onSubmit={handleSendMessage} className="flex items-center space-x-2 p-2 border-t">
          <ChatInput
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 p-1"
          />
          <Button type="submit" disabled={!input || isLoading} size="sm">
            <CornerDownLeft />
          </Button>
        </form>
      </div>
    </div>
  );
};

export default ChatWidget;
