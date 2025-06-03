import { useState } from 'react';
import { useNavigate, Link, Navigate } from 'react-router-dom';
import { Eye, EyeOff, Search, FileText, MessageSquare } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import toast from 'react-hot-toast';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({
    password: ''
  });

  const navigate = useNavigate();
  const register = useAuthStore((state) => state.register);
  
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (isAuthenticated) {
    return <Navigate to="/chat" replace />;
  } 

  const validateForm = () => {
    let isValid = true;
    const newErrors = { password: ''};

    // Validate password length
    if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    try {
      await register(formData);
      toast.success('Registration successful! Please login.');
      navigate('/login');
    } catch (error) {
      toast.error('Registration failed. Please try again.');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'faculty_id' ? parseInt(value) : value,
    }));
    
    // Clear errors when user types
    if (name === 'password' || name === 'confirm_password') {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const features = [
    {
      icon: <MessageSquare className="w-6 h-6 text-indigo-600" />,
      title: "Chat Interface",
      description: "Search and query universities, courses, and scholarship schemes through our intuitive chat interface."
    },
    {
      icon: <Search className="w-6 h-6 text-indigo-600" />,
      title: "Professor Search",
      description: "Find the perfect professor match with our intelligent agent-based search feature."
    },
    {
      icon: <FileText className="w-6 h-6 text-indigo-600" />,
      title: "SOP Review",
      description: "Get expert assistance with document preparation and Statement of Purpose reviews."
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-5xl flex overflow-hidden">
        {/* Feature Showcase */}
        <div className="hidden lg:block w-1/2 bg-indigo-600 p-12 text-white">
          <div className="h-full flex flex-col">
            <div className="flex items-center space-x-3 mb-12">
              <img src="/logo.png" alt="UniBro Logo" className="w-12 h-12" />
              <h1 className="text-3xl font-bold">UniBro</h1>
            </div>
            
            <h2 className="text-2xl font-semibold mb-8">Your Academic Journey Begins Here</h2>
            
            <div className="space-y-8 flex-grow">
              {features.map((feature, index) => (
                <div key={index} className="flex items-start space-x-4">
                  <div className="bg-white/20 p-3 rounded-lg">
                    {feature.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold text-xl">{feature.title}</h3>
                    <p className="text-indigo-100 mt-1">{feature.description}</p>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-auto pt-8 text-sm text-indigo-100">
              Empowering your educational decisions with intelligent assistance.
            </div>
          </div>
        </div>
        
        {/* Registration Form */}
        <div className="w-full lg:w-1/2 p-8 lg:p-12">
          <div className="flex flex-col items-center mb-8">
            <div className="bg-indigo-100 p-3 rounded-full mb-4">
              <img src="/logo.png" alt="UniBro Logo" className="w-10 h-10" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Create Account</h1>
            <p className="text-gray-600 mt-2">Join UniBro and start your academic journey</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                value={formData.username}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                required
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  value={formData.password}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  required
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 hover:text-gray-700 mt-1"
                  onClick={togglePasswordVisibility}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password}</p>}
            </div>

            <button
              type="submit"
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
            >
              Register
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-indigo-600 hover:text-indigo-500">
              Sign in
            </Link>
          </p>
          
          {/* Mobile version of features */}
          <div className="mt-8 lg:hidden">
            <h3 className="text-center text-lg font-semibold text-gray-800 mb-4">Our Features</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {features.map((feature, index) => (
                <div key={index} className="bg-indigo-50 p-4 rounded-lg text-center">
                  <div className="flex justify-center mb-2">
                    {feature.icon}
                  </div>
                  <h4 className="font-semibold text-sm">{feature.title}</h4>
                  <p className="text-xs text-gray-600 mt-1">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;