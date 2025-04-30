import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { toast } from "react-hot-toast";
import { api } from "../lib/axios";
import { PlusCircle, Send, Loader, Menu } from "lucide-react";

// Define interface types for better type safety
interface Message {
  role: string;
  content: string;
  timestamp: Date;
}

interface Session {
  session_id: string;
  created_at: Date;
  title: string;
}

const Chat = () => {
  const { isAuthenticated, user, fetchUser } = useAuthStore();
  const navigate = useNavigate();
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSession, setCurrentSession] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [showSidebar, setShowSidebar] = useState(true);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, navigate]);

  // Fetch user's sessions on component mount
  useEffect(() => {
    fetchSessions();
    fetchUser();
  }, []);

  // Watch for session changes to load messages
  useEffect(() => {
    if (currentSession) {
      fetchMessages(currentSession);
    } else {
      setMessages([]);
    }
  }, [currentSession]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchSessions = async () => {
    try {
      const response = await api.get("/sessions");
      setSessions(response.data.sessions || []);

      // If there are sessions, select the most recent one
      if (response.data.sessions && response.data.sessions.length > 0) {
        const lastSession =
          response.data.sessions[response.data.sessions.length - 1];
        setCurrentSession(lastSession.session_id);
      }
    } catch (error) {
      toast.error("Failed to load chat sessions");
      console.error("Error fetching sessions:", error);
    }
  };

  const fetchMessages = async (sessionId: string) => {
    try {
      setIsLoading(true);
      const response = await api.get(`/sessions/${sessionId}`);
      setMessages(response.data.messages || []);
    } catch (error) {
      toast.error("Failed to load chat history");
      console.error("Error fetching messages:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const createNewSession = async () => {
    try {
      setIsLoading(true);
      const response = await api.post("/sessions", {
        query: "Hello", // Initial query to create session
      });

      if (response.data.session_id) {
        await fetchSessions();
        setCurrentSession(response.data.session_id);
      }
    } catch (error) {
      toast.error("Failed to create a new chat");
      console.error("Error creating session:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || !currentSession) return;

    try {
      // Optimistically add user message to UI
      const userMessage = {
        role: "user",
        content: input,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);

      setIsLoading(true);
      const userInput = input;
      setInput(""); // Clear input right away

      const response = await api.post(`/sessions/${currentSession}/messages`, {
        query: userInput,
      });

      if (response.data.response) {
        // Add AI response to messages
        const aiMessage = {
          role: "assistant",
          content: response.data.response,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiMessage]);
      }
    } catch (error) {
      toast.error("Failed to send message");
      console.error("Error sending message:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e as unknown as React.FormEvent);
    }
  };

  const autoResizeTextarea = () => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`;
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar with chat history */}
      <div
        className={`${
          showSidebar ? "w-64" : "w-0"
        } transition-all duration-300 bg-gray-800 flex flex-col overflow-hidden`}
      >
        <div className="p-4 flex justify-between items-center">
          <h2 className="text-white font-semibold text-lg">Chat Sessions</h2>
          <button
            onClick={createNewSession}
            className="p-2 bg-gray-700 rounded-full hover:bg-gray-600 text-white"
            title="New chat"
          >
            <PlusCircle size={16} />
          </button>
        </div>

        <div className="overflow-y-auto flex-grow">
          {sessions
            .slice()
            .reverse()
            .map((session) => (
              <div
                key={session.session_id}
                onClick={() => setCurrentSession(session.session_id)}
                className={`px-4 py-3 cursor-pointer hover:bg-gray-700 transition-colors ${
                  currentSession === session.session_id ? "bg-gray-700" : ""
                }`}
              >
                <span className="text-white text-sm">
                  {new String(session.title || "New Chat")}
                </span>
                
              </div>
            ))}

          {sessions.length === 0 && (
            <div className="text-gray-400 text-center p-4">
              No chat sessions yet
            </div>
          )}
        </div>

        {/* User info */}
        <div className="p-4 border-t border-gray-700 text-white">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
              {user?.username?.charAt(0) || "U"}
            </div>
            <span className="ml-2 truncate">{user?.username || "User"}</span>
          </div>
        </div>
      </div>

      {/* Main chat area */}
      <div className="flex flex-col flex-grow overflow-hidden">
        {/* Chat header */}
        <div className="bg-white shadow p-4 flex items-center">
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="p-2 mr-2 bg-gray-100 hover:bg-gray-200 rounded-md"
          >
            <Menu size={18} />
          </button>
          <h1 className="text-lg font-semibold">UniBro</h1>
        </div>

        {/* Messages container */}
        <div className="flex-grow overflow-y-auto p-4 bg-white">
          {currentSession ? (
            <>
              {messages.length === 0 ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center text-gray-500">
                    <h3 className="text-xl font-semibold mb-2">
                      Start a new conversation
                    </h3>
                    <p>Ask the AI assistant anything</p>
                  </div>
                </div>
              ) : (
                messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`mb-4 ${
                      msg.role === "user"
                        ? "flex justify-end"
                        : "flex justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-3/4 p-3 rounded-lg ${
                        msg.role === "user"
                          ? "bg-blue-500 text-white rounded-br-none"
                          : "bg-gray-200 text-gray-800 rounded-bl-none"
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                    </div>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-500">
                <h3 className="text-xl font-semibold mb-2">
                  Welcome to UniBro
                </h3>
                <p className="mb-4">Create a new conversation to get started</p>
                <button
                  onClick={createNewSession}
                  className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition"
                >
                  New Chat
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Input area */}
        {currentSession && (
          <div className="border-t p-4 bg-white">
            <form onSubmit={handleSendMessage} className="flex items-end">
              <textarea
                ref={inputRef}
                className="flex-grow p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 mr-2"
                placeholder="Type your message..."
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  autoResizeTextarea();
                }}
                onKeyDown={handleKeyDown}
                rows={1}
                disabled={isLoading}
              />
              <button
                type="submit"
                className={`p-3 rounded-full ${
                  isLoading || !input.trim()
                    ? "bg-gray-300 cursor-not-allowed"
                    : "bg-blue-500 hover:bg-blue-600"
                } text-white`}
                disabled={isLoading || !input.trim()}
              >
                {isLoading ? (
                  <Loader className="animate-spin" size={18} />
                ) : (
                  <Send size={18} />
                )}
              </button>
            </form>
            {isLoading && (
              <div className="text-xs text-gray-500 mt-1">
                AI is thinking...
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat;
