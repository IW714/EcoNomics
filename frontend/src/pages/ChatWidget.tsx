import React, { useState, useRef, useEffect } from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { ChatBubble, ChatBubbleMessage, ChatBubbleAction } from '@/components/ui/chat/chat-bubble';
import { ChatInput } from '@/components/ui/chat/chat-input';
import { ChatMessageList } from '@/components/ui/chat/chat-message-list';
import { CornerDownLeft, CopyIcon, RefreshCcw } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import { SolarAssessmentResponse, WindDataResponse } from '@/models/types';
import ReactMarkdown from 'react-markdown';

type Message = {
  id: number;
  role: 'user' | 'assistant';
  message: string;
  isLoading?: boolean;
};

type ChatWidgetProps = {
  onCombinedAssessmentResult: (solarAssessment: SolarAssessmentResponse, windAssessment: WindDataResponse) => void;
};

const ChatWidget: React.FC<ChatWidgetProps> = ({ onCombinedAssessmentResult }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const sessionId = 'unique-session-id';

  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const addMessage = (role: 'user' | 'assistant', text: string, loading: boolean = false) => {
    const newMessage = { id: Date.now(), role, message: text, isLoading: loading };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e as unknown as React.FormEvent<HTMLFormElement>);
    }
  };

  const handleSendMessage = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userInput = input.trim();
    addMessage('user', userInput);
    setInput('');
    setIsLoading(true);
    
    // Add a loading message
    const loadingMessageId = Date.now();
    setMessages(prev => [...prev, {
      id: loadingMessageId,
      role: 'assistant',
      message: '...',
      isLoading: true
    }]);

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userInput, session_id: sessionId }),
      });

      const data = await response.json();
      
      // Remove loading message and add actual response
      setMessages(prev => {
        const filtered = prev.filter(msg => msg.id !== loadingMessageId);
        return [...filtered, {
          id: Date.now(),
          role: 'assistant',
          message: data.response,
          isLoading: false
        }];
      });

      if (data.solar_assessment && data.wind_assessment) {
        onCombinedAssessmentResult(data.solar_assessment, data.wind_assessment);
      }
    } catch (error) {
      setMessages(prev => {
        const filtered = prev.filter(msg => msg.id !== loadingMessageId);
        return [...filtered, {
          id: Date.now(),
          role: 'assistant',
          message: 'Error: Unable to fetch response. Please try again later.',
          isLoading: false
        }];
      });
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const copyMessage = (message: string) => {
    navigator.clipboard.writeText(message);
  };

  return (
    <div className="flex flex-col h-[700px] w-full rounded-xl bg-muted/20 dark:bg-muted/40 p-4">
      <div 
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto"
      >
        <ChatMessageList>
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                // ... motion settings ...
                className="flex flex-col gap-2 p-4"
              >
                <ChatBubble variant={message.role === 'assistant' ? 'received' : 'sent'}>
                  <Avatar>
                    <AvatarImage 
                      src={message.role === 'assistant' ? '/bot-avatar.png' : '/user-avatar.png'} 
                      className={message.role === 'assistant' ? "dark:invert" : ""}
                    />
                    <AvatarFallback>{message.role === 'assistant' ? '🤖' : 'U'}</AvatarFallback>
                  </Avatar>
                  <ChatBubbleMessage isLoading={message.isLoading}>
                    {message.isLoading ? (
                      <div className="flex items-center space-x-2">
                        <div className="animate-pulse">Thinking...</div>
                      </div>
                    ) : (
                      <>
                        <div className="prose dark:prose-invert max-w-none break-words">
                          <ReactMarkdown>{message.message}</ReactMarkdown>
                        </div>
                        {message.role === 'assistant' && (
                          <div className="flex items-center mt-1.5 gap-1">
                            <ChatBubbleAction
                              variant="outline"
                              className="size-6"
                              icon={<CopyIcon className="size-3" />}
                              onClick={() => copyMessage(message.message)}
                            />
                            <ChatBubbleAction
                              variant="outline"
                              className="size-6"
                              icon={<RefreshCcw className="size-3" />}
                              onClick={() => {/* TODO: Implement retry logic */}}
                            />
                          </div>
                        )}
                      </>
                    )}
                  </ChatBubbleMessage>
                </ChatBubble>
              </motion.div>
            ))}
          </AnimatePresence>
        </ChatMessageList>
      </div>

      <form 
        onSubmit={handleSendMessage} 
        className="mt-4"
      >
        <div className="relative flex items-center">
          <ChatInput
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            className="flex-1 min-h-12 resize-none rounded-lg bg-background border p-3 shadow-none focus-visible:ring-0"
          />
          <Button
            disabled={!input || isLoading}
            type="submit"
            size="sm"
            className="ml-2 gap-1.5"
          >
            Send Message
            <CornerDownLeft className="size-3.5" />
          </Button>
        </div>
      </form>
    </div>
  );
};

export default ChatWidget;