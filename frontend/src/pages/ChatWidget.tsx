import * as React from "react";
import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface ChatInputProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

const ChatInput = React.forwardRef<HTMLTextAreaElement, ChatInputProps>(
  ({ className, ...props }, ref) => (
    <Textarea
      autoComplete="off"
      ref={ref}
      name="message"
      className={cn(
        "max-h-12 px-4 py-3 bg-background text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 w-full rounded-md flex items-center h-16 resize-none",
        className
      )}
      {...props}
    />
  )
);
ChatInput.displayName = "ChatInput";

interface ChatMessageListProps extends React.HTMLAttributes<HTMLDivElement> {
  chatMessages: string[];
}

const ChatMessageList: React.FC<ChatMessageListProps> = ({
  className,
  chatMessages,
  ...props
}) => (
  <div
    className={cn(
      "flex flex-col w-full h-full p-4 gap-6 overflow-y-auto",
      className
    )}
    {...props}
  >
    {chatMessages.map((message, index) => (
      <div
        key={index}
        className="bg-gray-100 p-3 rounded-md shadow-sm dark:bg-neutral-800 dark:text-neutral-50"
      >
        {message}
      </div>
    ))}
  </div>
);

interface ChatWidgetProps {
  chatMessages: string[];
  onChatSubmit: (message: string) => void;
}

const ChatWidget: React.FC<ChatWidgetProps> = ({ chatMessages, onChatSubmit }) => {
  const [message, setMessage] = useState("");

  const handleChatSubmit = () => {
    if (message.trim()) {
      onChatSubmit(message);
      setMessage("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleChatSubmit();
    }
  };

  return (
    <div className="border-t p-4 bg-gray-50 dark:bg-neutral-900">
      <div className="flex items-center gap-2">
        <ChatInput
          placeholder="Send a message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          className="flex-1"
        />
        <Button size="icon" onClick={handleChatSubmit}>
          <svg
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
          >
            <path
              d="M22 2L11 13"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M22 2L15 22L11 13L2 9L22 2Z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </Button>
      </div>
      <ChatMessageList chatMessages={chatMessages} className="mt-4" />
    </div>
  );
};

export { ChatWidget };