import { useState } from "react"
import { Navigate, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { Search, FileText, MessageSquare, Eye, EyeOff } from "lucide-react";
import { Link } from "react-router-dom";
import { toast } from "react-hot-toast";

const Login = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);

    const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

    if (isAuthenticated) {
        return <Navigate to="/chat" replace />;
    }
    const navigate = useNavigate();
    const login = useAuthStore((state) => state.login);

    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await login(email, password);
            navigate('/chat');
            toast.success('Login successful!');
        } catch (error) {
            toast.error('Invalid credentials');
        }
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
                        
                        <h2 className="text-2xl font-semibold mb-8">Your Academic Journey Made Easier</h2>
                        
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
                
                {/* Login Form */}
                <div className="w-full lg:w-1/2 p-8 lg:p-12">
                    <div className="flex flex-col items-center mb-8">
                        <div className="bg-indigo-100 p-3 rounded-full mb-4">
                            <img src="/logo.png" alt="UniBro Logo" className="w-10 h-10" />
                        </div>
                        <h1 className="text-2xl font-bold text-gray-900">Welcome Back</h1>
                        <p className="text-gray-600 mt-2">Sign in to continue your academic journey</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                                Email
                            </label>
                            <input
                                id="email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
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
                                    type={showPassword ? "text" : "password"}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
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
                        </div>

                        {/* <div className="flex items-center justify-between">
                            <div className="flex items-center">
                                <input
                                    id="remember-me"
                                    name="remember-me"
                                    type="checkbox"
                                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                                />
                                <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700">
                                    Remember me
                                </label>
                            </div>

                            <div className="text-sm">
                                <a href="#" className="font-medium text-indigo-600 hover:text-indigo-500">
                                    Forgot your password?
                                </a>
                            </div>
                        </div> */}

                        <button
                            type="submit"
                            className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                        >
                            Sign In
                        </button>
                    </form>

                    <p className="mt-6 text-center text-sm text-gray-600">
                        Don't have an account?{' '}
                        <Link to="/register" className="font-medium text-indigo-600 hover:text-indigo-500">
                            Register here
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

export default Login;