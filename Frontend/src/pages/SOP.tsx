import { useState, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { toast } from "react-hot-toast";
import { api } from "../lib/axios";
import { Upload, FileText, Loader, Menu, Moon, Sun, GraduationCap, AlertCircle, ChevronDown } from "lucide-react";

interface ReviewData {
  grammar_and_style?: string;
  structure?: string;
  clarity_and_coherence?: string;
  research_interests_strength?: string;
  overall_rating?: string;
  message?: string;
}

const SOP = () => {
  const { isAuthenticated, user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [review, setReview] = useState<ReviewData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showUserDropdown, setShowUserDropdown] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Redirect if not authenticated
  if (!isAuthenticated) {
    navigate("/login");
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      
      // Check if the file is a PDF
      if (!selectedFile.name.endsWith('.pdf')) {
        setError("Only PDF files are allowed.");
        setFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
        return;
      }
      
      setFile(selectedFile);
      setError(null);
      setReview(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setError("Please select a PDF file to upload.");
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/sop-review', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.review) {
        setReview(response.data.review);
        toast.success('SOP reviewed successfully!');
      }
    } catch (error: any) {
      let errorMessage = "Failed to review SOP. Please try again.";
      
      if (error.response) {
        errorMessage = error.response.data?.detail || errorMessage;
      }
      
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setReview(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
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

  return (
    <div className={`flex h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-50'} transition-colors duration-200`}>
      {/* Sidebar with navigation */}
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
        </div>

        <div className="overflow-y-auto flex-grow">
          <div
            onClick={() => navigate('/chat')}
            className={`px-5 py-3 mx-3 my-1 cursor-pointer rounded-lg transition-colors 
              ${darkMode ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-indigo-600/70 text-white/90'}`}
          >
            <span className="text-sm font-medium">Chat</span>
          </div>
          
          <div
            className={`px-5 py-3 mx-3 my-1 cursor-pointer rounded-lg transition-colors 
              ${darkMode ? 'bg-gray-700 text-white' : 'bg-indigo-600 text-white'}`}
          >
            <span className="text-sm font-medium">SOP Review</span>
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

      {/* Main content area */}
      <div className={`flex flex-col flex-grow overflow-hidden ${darkMode ? 'bg-gray-900' : 'bg-gray-50'} transition-colors duration-200`}>
        {/* Header */}
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
        </div>

        {/* Main content */}
        <div className={`flex-grow overflow-y-auto ${darkMode ? 'bg-gray-900' : 'bg-gray-50'} transition-colors duration-200`}>
          <div className="max-w-4xl mx-auto p-8">
            <div className={`bg-${darkMode ? 'gray-800' : 'white'} rounded-xl shadow-lg p-8 transition-colors duration-200`}>
              <h2 className={`text-2xl font-bold mb-6 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                Statement of Purpose Review
              </h2>
              
              {!review ? (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label 
                      htmlFor="file-upload" 
                      className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}
                    >
                      Upload your SOP (PDF only)
                    </label>
                    
                    <div className={`mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-lg ${
                      darkMode 
                        ? 'border-gray-600 hover:border-gray-500' 
                        : 'border-gray-300 hover:border-indigo-300'
                    } transition-colors cursor-pointer`}
                    onClick={() => fileInputRef.current?.click()}
                    >
                      <div className="space-y-1 text-center">
                        <FileText 
                          className={`mx-auto h-12 w-12 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}
                          aria-hidden="true" 
                        />
                        <div className="flex text-sm justify-center">
                          <label
                            htmlFor="file-upload"
                            className={`relative cursor-pointer rounded-md font-medium ${
                              darkMode ? 'text-indigo-400 hover:text-indigo-300' : 'text-indigo-600 hover:text-indigo-500'
                            }`}
                          >
                            <span>Upload a file</span>
                            <input
                              id="file-upload"
                              name="file-upload"
                              type="file"
                              className="sr-only"
                              ref={fileInputRef}
                              onChange={handleFileChange}
                              accept=".pdf"
                            />
                          </label>
                          <p className={`pl-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>or drag and drop</p>
                        </div>
                        <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                          PDF up to 10MB
                        </p>
                      </div>
                    </div>
                    
                    {file && (
                      <div className={`mt-3 flex items-center ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                        <FileText size={18} className="mr-2" />
                        <span className="text-sm">{file.name}</span>
                      </div>
                    )}
                  </div>
                  
                  {error && (
                    <div className="flex items-center text-red-500 mt-2 text-sm">
                      <AlertCircle size={16} className="mr-2" />
                      {error}
                    </div>
                  )}
                  
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      className={`flex items-center px-4 py-2 rounded-lg font-medium ${
                        isLoading 
                          ? darkMode ? 'bg-gray-600 cursor-not-allowed' : 'bg-gray-300 cursor-not-allowed'
                          : 'bg-indigo-600 hover:bg-indigo-700'
                      } text-white shadow-md transition-colors`}
                      disabled={isLoading || !file}
                    >
                      {isLoading ? (
                        <>
                          <Loader className="animate-spin mr-2" size={18} />
                          Processing...
                        </>
                      ) : (
                        <>
                          <Upload className="mr-2" size={18} />
                          Review SOP
                        </>
                      )}
                    </button>
                  </div>
                </form>
              ) : (
                <div className="space-y-6">
                  <div className={`p-6 rounded-lg ${
                    darkMode ? 'bg-gray-700 text-gray-100' : 'bg-gray-50 text-gray-800'
                  } transition-colors`}>
                    <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                      SOP Review Results
                    </h3>
                    
                    {review.message ? (
                      // Display message for invalid SOP
                      <div className="py-4">
                        <p className={`text-md font-medium ${darkMode ? 'text-yellow-400' : 'text-yellow-600'}`}>
                          {review.message}
                        </p>
                      </div>
                    ) : (
                      // Display detailed review for valid SOP
                      <div className="space-y-6">
                        <div>
                          <h4 className={`text-md font-medium mb-2 ${darkMode ? 'text-indigo-400' : 'text-indigo-600'}`}>
                            Grammar and Style
                          </h4>
                          <p className="text-sm whitespace-pre-line">{review.grammar_and_style}</p>
                        </div>
                        
                        <div>
                          <h4 className={`text-md font-medium mb-2 ${darkMode ? 'text-indigo-400' : 'text-indigo-600'}`}>
                            Structure
                          </h4>
                          <p className="text-sm whitespace-pre-line">{review.structure}</p>
                        </div>
                        
                        <div>
                          <h4 className={`text-md font-medium mb-2 ${darkMode ? 'text-indigo-400' : 'text-indigo-600'}`}>
                            Clarity and Coherence
                          </h4>
                          <p className="text-sm whitespace-pre-line">{review.clarity_and_coherence}</p>
                        </div>
                        
                        <div>
                          <h4 className={`text-md font-medium mb-2 ${darkMode ? 'text-indigo-400' : 'text-indigo-600'}`}>
                            Research Interests
                          </h4>
                          <p className="text-sm whitespace-pre-line">{review.research_interests_strength}</p>
                        </div>
                        
                        <div>
                          <h4 className={`text-md font-medium mb-2 ${darkMode ? 'text-indigo-400' : 'text-indigo-600'}`}>
                            Overall Rating
                          </h4>
                          <p className="text-sm font-medium">{review.overall_rating}</p>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex justify-end">
                    <button
                      onClick={resetForm}
                      className={`px-4 py-2 rounded-lg font-medium bg-indigo-600 hover:bg-indigo-700 text-white shadow-md transition-colors`}
                    >
                      Upload Another File
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SOP; 