import { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { toast } from "react-hot-toast";
import { api } from "../lib/axios";
import { PlusCircle, Send, Loader, Menu, Moon, Sun, GraduationCap, FileText, ChevronDown, Trash2 } from "lucide-react";

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
  const { isAuthenticated, user, fetchUser, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSession, setCurrentSession] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showUserDropdown, setShowUserDropdown] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

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

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const toggleDropdown = () => {
    setShowDropdown(!showDropdown);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    setShowDropdown(false);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const toggleUserDropdown = () => {
    setShowUserDropdown(!showUserDropdown);
  };

  const handleDeleteClick = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setSessionToDelete(sessionId);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!sessionToDelete) return;
    
    try {
      await api.delete(`/sessions/${sessionToDelete}`);
      await fetchSessions(); // Refresh the sessions list
      
      // If the deleted session was the current one, clear it
      if (currentSession === sessionToDelete) {
        setCurrentSession(null);
        setMessages([]);
      }
      
      toast.success("Session deleted successfully");
    } catch (error) {
      toast.error("Failed to delete session");
      console.error("Error deleting session:", error);
    } finally {
      setShowDeleteModal(false);
      setSessionToDelete(null);
    }
  };

  const cancelDelete = () => {
    setShowDeleteModal(false);
    setSessionToDelete(null);
  };

  return (
    <div className={`flex h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-50'} transition-colors duration-200`}>
      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className={`${darkMode ? 'bg-gray-800' : 'bg-white'} rounded-lg p-6 max-w-sm w-full mx-4 shadow-xl`}>
            <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              Delete Chat Session
            </h3>
            <p className={`mb-6 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              Are you sure you want to delete this chat session? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={cancelDelete}
                className={`px-4 py-2 rounded-lg ${
                  darkMode 
                    ? 'bg-gray-700 hover:bg-gray-600 text-white' 
                    : 'bg-gray-200 hover:bg-gray-300 text-gray-800'
                } transition-colors`}
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Sidebar with chat history */}
      <div
        className={`${
          showSidebar ? "w-72" : "w-0"
        } transition-all duration-300 ${darkMode ? 'bg-gray-800' : 'bg-indigo-700'} flex flex-col overflow-hidden`}
      >
        <div className="p-5 flex justify-between items-center">
          <div className="flex items-center">
            <GraduationCap className="w-6 h-6 text-white mr-2" />
            <h2 className="text-white font-semibold text-lg">UniBro</h2>
          </div>
          <button
            onClick={createNewSession}
            className={`p-2 ${darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-indigo-600 hover:bg-indigo-500'} rounded-full text-white shadow-md transition-colors`}
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
                className={`px-5 py-3 mx-3 my-1 cursor-pointer rounded-lg transition-colors ${
                  currentSession === session.session_id 
                    ? darkMode ? 'bg-gray-700 text-white' : 'bg-indigo-600 text-white' 
                    : darkMode ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-indigo-600/70 text-white/90'
                }`}
              >
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">
                    {new String(session.title || "New Chat")}
                  </span>
                  <button
                    onClick={(e) => handleDeleteClick(session.session_id, e)}
                    className={`p-1 rounded-full hover:bg-opacity-20 ${
                      darkMode 
                        ? 'hover:bg-red-400 text-gray-300 hover:text-red-400' 
                        : 'hover:bg-red-400 text-white/90 hover:text-red-400'
                    } transition-colors`}
                    title="Delete chat"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}

          {sessions.length === 0 && (
            <div className="text-center p-6">
              <div className={`${darkMode ? 'text-gray-400' : 'text-indigo-100'} text-sm`}>
                No chat sessions yet
              </div>
            </div>
          )}
          
          {/* Navigation links */}
          <div className="mt-6 border-t border-gray-700 pt-4 px-3">
            <div
              onClick={() => navigate('/sop')}
              className={`px-4 py-3 my-1 flex items-center cursor-pointer rounded-lg transition-colors ${
                darkMode ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-indigo-600/70 text-white/90'
              }`}
            >
              <FileText size={18} className="mr-2" />
              <span className="text-sm font-medium">SOP Review</span>
            </div>
          </div>
        </div>

        {/* User info */}
        <div className={`p-4 border-t ${darkMode ? 'border-gray-700' : 'border-indigo-600'} text-white relative`}>
          <div className="flex items-center justify-between">
            <div 
              className="flex items-center cursor-pointer"
              onClick={toggleUserDropdown}
            >
              <div className={`w-9 h-9 ${darkMode ? 'bg-gray-600' : 'bg-indigo-600'} rounded-full flex items-center justify-center shadow-md`}>
                {user?.username?.charAt(0) || "U"}
              </div>
              <span className="ml-3 truncate font-medium">{user?.username || "User"}</span>
            </div>
            <button
              onClick={toggleDarkMode}
              className={`p-2 rounded-full ${darkMode ? 'text-gray-300 hover:text-white' : 'text-white/80 hover:text-white'} transition`}
            >
              {darkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </div>

          {/* User Dropdown Menu */}
          {showUserDropdown && (
            <div className={`absolute bottom-full left-0 mb-2 w-48 rounded-md shadow-lg ${
              darkMode ? 'bg-gray-700' : 'bg-white'
            } ring-1 ring-black ring-opacity-5 z-50`}>
              <div className="py-1">
                <button
                  onClick={handleLogout}
                  className={`block w-full text-left px-4 py-2 text-sm ${
                    darkMode 
                      ? 'text-gray-100 hover:bg-gray-600' 
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main chat area */}
      <div className={`flex flex-col flex-grow overflow-hidden ${darkMode ? 'bg-gray-900' : 'bg-gray-50'} transition-colors duration-200`}>
        {/* Chat header */}
        <div className={`${darkMode ? 'bg-gray-800 shadow-md text-white' : 'bg-white shadow text-gray-800'} p-4 flex items-center justify-between transition-colors duration-200`}>
          <div className="flex items-center">
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className={`p-2 mr-3 rounded-md ${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'} transition-colors`}
            >
              <Menu size={20} />
            </button>
            <div className="relative">
              <button
                onClick={toggleDropdown}
                className="flex items-center text-lg font-semibold hover:opacity-80 transition-opacity"
              >
                {location.pathname === '/sop' ? 'SOP Review' : 'Chat with UniBro'}
                <ChevronDown size={20} className="ml-2" />
              </button>
              
              {showDropdown && (
                <div className={`absolute top-full left-0 mt-2 w-48 rounded-md shadow-lg ${
                  darkMode ? 'bg-gray-700' : 'bg-white'
                } ring-1 ring-black ring-opacity-5 z-50`}>
                  <div className="py-1">
                    <button
                      onClick={() => handleNavigation('/')}
                      className={`block w-full text-left px-4 py-2 text-sm ${
                        darkMode 
                          ? 'text-gray-100 hover:bg-gray-600' 
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      Chat with UniBro
                    </button>
                    <button
                      onClick={() => handleNavigation('/sop')}
                      className={`block w-full text-left px-4 py-2 text-sm ${
                        darkMode 
                          ? 'text-gray-100 hover:bg-gray-600' 
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      SOP Review
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* New Chat button in header */}
          <button
            onClick={createNewSession}
            className={`flex items-center px-2 py-2 rounded-lg text-sm font-medium ${
              darkMode 
                ? 'bg-gray-700 hover:bg-gray-600 text-white' 
                : 'bg-indigo-600 hover:bg-indigo-700 text-white'
            } transition-colors shadow-sm`}
            disabled={isLoading}
            title="New Chat"
          >
            <PlusCircle size={16} className="mr-2 ml-2" />
          </button>
        </div>

        {/* Messages container */}
        <div className={`flex-grow overflow-y-auto ${darkMode ? 'bg-gray-900' : 'bg-gray-50'} transition-colors duration-200`}>
          <div className="max-w-4xl mx-auto">
            {currentSession ? (
              <>
                {messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full p-8">
                    <div className={`text-center ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                      <h3 className="text-xl font-semibold mb-3">
                        How can I assist you today?
                      </h3>
                      <p className="max-w-md mx-auto">Ask me any questions about graduate studies, universities, searching professors and more.</p>
                    </div>
                  </div>
                ) : (
                  <div className="py-6 px-4">
                    {messages.map((msg, index) => (
                      <div
                        key={index}
                        className={`mb-8 max-w-3xl mx-auto ${
                          msg.role === "user" ? "flex justify-end" : "flex justify-start"
                        }`}
                      >
                        <div className="flex gap-4 items-start">
                          {msg.role !== "user" && (
                            <div className={`w-8 h-8 mt-1 ${darkMode ? 'bg-indigo-500' : 'bg-indigo-600'} rounded-full flex items-center justify-center text-white`}>
                              U
                            </div>
                          )}
                          <div
                            className={`p-4 rounded-2xl max-w-[85%] ${
                              msg.role === "user"
                                ? darkMode 
                                  ? "bg-indigo-600 text-white" 
                                  : "bg-indigo-600 text-white"
                                : darkMode 
                                  ? "bg-gray-800 text-gray-100 border border-gray-700" 
                                  : "bg-white text-gray-800 shadow-sm"
                            } transition-colors duration-200`}
                          >
                            <div className="whitespace-pre-wrap text-sm">{msg.content}</div>
                          </div>
                          {msg.role === "user" && (
                            <div className={`w-8 h-8 mt-1 ${darkMode ? 'bg-indigo-500' : 'bg-indigo-600'} rounded-full flex items-center justify-center text-white`}>
                              {user?.username?.charAt(0) || "U"}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                <div className="h-24" /> {/* Extra padding at bottom */}
                <div ref={messagesEndRef} />
              </>
            ) : (
              <div className="flex items-center justify-center h-full p-8">
                <div className={`text-center ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  <div className="bg-indigo-100 p-3 rounded-full mx-auto mb-6 w-16 h-16 flex items-center justify-center">
                    <GraduationCap className="w-8 h-8 text-indigo-600" />
                  </div>
                  <h3 className="text-2xl font-bold mb-4">
                    Welcome to UniBro
                  </h3>
                  <p className="mb-6 max-w-md mx-auto">Start a new conversation with your AI assistant for personalized academic help.</p>
                  <button
                    onClick={createNewSession}
                    className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition shadow-md font-medium"
                  >
                    New Chat
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Input area */}
        {currentSession && (
          <div className={`px-4 py-4 ${darkMode ? 'bg-gray-800 border-t border-gray-700' : 'bg-white border-t border-gray-200'} transition-colors duration-200`}>
            <div className="max-w-4xl mx-auto">
              <form onSubmit={handleSendMessage} className="flex items-end relative">
                <textarea
                  ref={inputRef}
                  className={`flex-grow p-4 ${
                    darkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:ring-indigo-500' 
                      : 'bg-gray-50 border-gray-300 text-gray-800 focus:ring-indigo-500'
                  } border rounded-xl resize-none focus:outline-none focus:ring-2 mr-3 shadow-sm transition-colors duration-200`}
                  placeholder="Type your message..."
                  value={input}
                  onChange={(e) => {
                    setInput(e.target.value);
                    autoResizeTextarea();
                  }}
                  onKeyDown={handleKeyDown}
                  rows={1}
                  disabled={isLoading}
                  style={{ maxHeight: '200px' }}
                />
                <button
                  type="submit"
                  className={`p-3 rounded-xl ${
                    isLoading || !input.trim()
                      ? darkMode ? 'bg-gray-600 cursor-not-allowed' : 'bg-gray-300 cursor-not-allowed'
                      : 'bg-indigo-600 hover:bg-indigo-700'
                  } text-white shadow-md transition-colors`}
                  disabled={isLoading || !input.trim()}
                >
                  {isLoading ? (
                    <Loader className="animate-spin" size={20} />
                  ) : (
                    <Send size={20} />
                  )}
                </button>
              </form>
              {isLoading && (
                <div className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'} mt-2 text-center`}>
                  AI is thinking...
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat;
