import { useState } from 'react';
import { Shield, Loader2, Mail, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

export default function LoginScreen({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  
  // Form fields
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [organization, setOrganization] = useState('');
  
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!identifier || !password) return setError('Please enter a valid credential and password.');
    if (!isLogin && (!fullName || !organization)) return setError('Please fill out all signup fields.');
    
    setLoading(true);
    setError('');
    try {
      // Using identifier as username for the backend
      const res = isLogin 
        ? await api.login(identifier, password) 
        : await api.register(identifier, password);
      
      localStorage.setItem('cs_token', res.access_token);
      onLogin({ username: res.username, role: res.role });
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setGoogleLoading(true);
    setError('');
    try {
      // Create a seamless Google OAuth mock that fetches a real JWT token from the backend
      const googleUser = 'google_oauth_user';
      const googlePass = 'google_oauth_secret_pass';
      
      let res;
      try {
        res = await api.login(googleUser, googlePass);
      } catch (e) {
        res = await api.register(googleUser, googlePass);
      }
      
      localStorage.setItem('cs_token', res.access_token);
      onLogin({ username: 'Google User', role: 'user' });
    } catch (err) {
      setError('Google Sign-In failed');
    } finally {
      setGoogleLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col relative overflow-hidden">
      {/* Modern Webapp Background Elements */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-400/20 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-orange-400/20 blur-[120px]" />
        {/* Subtle grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
      </div>

      {/* Navbar */}
      <div className="h-16 bg-white/80 backdrop-blur-md border-b border-gray-200 flex items-center px-8 z-10">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-[#FFA116] flex items-center justify-center shadow-lg shadow-orange-500/30">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-xl tracking-tight text-slate-900">CyberSentric</span>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center p-4 z-10">
        <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white w-full max-w-[440px] overflow-hidden">
          
          {/* Tabs */}
          <div className="flex border-b border-gray-100">
            <button 
              onClick={() => { setIsLogin(true); setError(''); }}
              className={`flex-1 py-4 text-sm font-semibold transition-colors relative ${isLogin ? 'text-[#FFA116]' : 'text-gray-400 hover:text-gray-600'}`}
            >
              Sign In
              {isLogin && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-[#FFA116] shadow-[0_-2px_10px_rgba(255,161,22,0.5)]"></div>}
            </button>
            <button 
              onClick={() => { setIsLogin(false); setError(''); }}
              className={`flex-1 py-4 text-sm font-semibold transition-colors relative ${!isLogin ? 'text-[#FFA116]' : 'text-gray-400 hover:text-gray-600'}`}
            >
              Create Account
              {!isLogin && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-[#FFA116] shadow-[0_-2px_10px_rgba(255,161,22,0.5)]"></div>}
            </button>
          </div>

          <div className="p-8">
            <div className="text-center mb-6">
              <h1 className="text-2xl font-bold text-slate-800 mb-2">
                {isLogin ? 'Welcome back' : 'Start your journey'}
              </h1>
              <p className="text-sm text-gray-500">
                {isLogin ? 'Enter your details to access the dashboard.' : 'Sign up to secure your enterprise infrastructure.'}
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {!isLogin && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-gray-600 mb-1">Full Name</label>
                    <input 
                      type="text" 
                      value={fullName} 
                      onChange={e => setFullName(e.target.value)}
                      placeholder="John Doe" 
                      className="w-full border border-gray-200 bg-gray-50/50 rounded-lg px-4 py-3 text-[15px] text-slate-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-[#FFA116] focus:ring-2 focus:ring-[#FFA116]/20 transition-all" 
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-600 mb-1">Organization</label>
                    <input 
                      type="text" 
                      value={organization} 
                      onChange={e => setOrganization(e.target.value)}
                      placeholder="Company Inc." 
                      className="w-full border border-gray-200 bg-gray-50/50 rounded-lg px-4 py-3 text-[15px] text-slate-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-[#FFA116] focus:ring-2 focus:ring-[#FFA116]/20 transition-all" 
                    />
                  </div>
                </>
              )}

              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Email, Number or Username</label>
                <input 
                  type="text" 
                  value={identifier} 
                  onChange={e => setIdentifier(e.target.value)}
                  placeholder="name@company.com / 98765... / username" 
                  className="w-full border border-gray-200 bg-gray-50/50 rounded-lg px-4 py-3 text-[15px] text-slate-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-[#FFA116] focus:ring-2 focus:ring-[#FFA116]/20 transition-all" 
                />
              </div>
              
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="block text-xs font-semibold text-gray-600">Password</label>
                  {isLogin && <a href="#" className="text-xs text-[#FFA116] hover:underline font-medium">Forgot?</a>}
                </div>
                <input 
                  type="password" 
                  value={password} 
                  onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••" 
                  className="w-full border border-gray-200 bg-gray-50/50 rounded-lg px-4 py-3 text-[15px] text-slate-800 placeholder-gray-400 focus:bg-white focus:outline-none focus:border-[#FFA116] focus:ring-2 focus:ring-[#FFA116]/20 transition-all" 
                />
              </div>

              {error && <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100 flex items-start gap-2">
                <div className="mt-0.5">⚠️</div>
                {error}
              </div>}

              <button 
                type="submit" 
                disabled={loading}
                className="w-full bg-[#1e293b] hover:bg-black text-white rounded-lg py-3.5 font-semibold transition-all shadow-[0_4px_14px_0_rgb(0,0,0,0.1)] hover:shadow-[0_6px_20px_rgba(0,0,0,0.2)] flex items-center justify-center gap-2 mt-2"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (isLogin ? 'Sign In to Dashboard' : 'Create Account')}
              </button>
            </form>

            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200"></div>
                </div>
                <div className="relative flex justify-center text-xs uppercase tracking-wider font-semibold">
                  <span className="px-3 bg-white text-gray-400">Or continue with</span>
                </div>
              </div>

              <div className="mt-6">
                <button 
                  onClick={handleGoogleLogin}
                  disabled={googleLoading}
                  className="w-full flex items-center justify-center gap-3 px-4 py-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors font-medium text-slate-700 disabled:opacity-50"
                >
                  {googleLoading ? <Loader2 className="w-5 h-5 animate-spin text-slate-400" /> : (
                    <>
                      <svg className="w-5 h-5" viewBox="0 0 24 24">
                        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                      </svg>
                      Sign in with Google
                    </>
                  )}
                </button>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
