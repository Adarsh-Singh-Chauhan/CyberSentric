import { useState, useEffect } from 'react';
import { Lock, User, Eye, EyeOff, Shield, ArrowRight, Loader2 } from 'lucide-react';
import { api } from '../services/api';

export default function LoginScreen({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) return setError('All fields required');
    setLoading(true);
    setError('');
    try {
      const res = isLogin ? await api.login(username, password) : await api.register(username, password);
      localStorage.setItem('cs_token', res.access_token);
      onLogin({ username: res.username, role: res.role });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-cyber-bg cyber-grid flex items-center justify-center p-4">
      {/* Ambient glow */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/5 rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-[120px]" />
      </div>

      <div className="glass rounded-2xl p-8 w-full max-w-md relative animate-fade-in">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center mb-4 animate-glow">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            CyberSentric
          </h1>
          <p className="text-xs text-slate-500 mt-1">AI-Driven Cybersecurity Defense Platform</p>
        </div>

        {/* Toggle */}
        <div className="flex bg-white/5 rounded-lg p-1 mb-6">
          <button onClick={() => setIsLogin(true)}
            className={`flex-1 py-2 rounded-md text-sm font-medium transition-all ${isLogin ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-500'}`}>
            Sign In
          </button>
          <button onClick={() => setIsLogin(false)}
            className={`flex-1 py-2 rounded-md text-sm font-medium transition-all ${!isLogin ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-500'}`}>
            Register
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input type="text" value={username} onChange={e => setUsername(e.target.value)}
              placeholder="Username" autoComplete="username"
              className="w-full bg-white/5 border border-cyber-border rounded-lg pl-10 pr-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500/50 transition-all" />
          </div>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input type={showPass ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)}
              placeholder="Password" autoComplete={isLogin ? 'current-password' : 'new-password'}
              className="w-full bg-white/5 border border-cyber-border rounded-lg pl-10 pr-10 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500/50 transition-all" />
            <button type="button" onClick={() => setShowPass(!showPass)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300">
              {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>

          {error && <p className="text-xs text-red-400 text-center">{error}</p>}

          <button type="submit" disabled={loading}
            className="w-full py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg text-sm font-semibold text-white hover:opacity-90 transition-all disabled:opacity-40 flex items-center justify-center gap-2">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
            {isLogin ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <div className="mt-6 p-3 rounded-lg bg-white/[0.02] border border-cyber-border/50">
          <p className="text-[10px] text-slate-500 text-center">
            Demo credentials: <span className="text-cyan-400 font-mono">admin / admin123</span> (admin) or <span className="text-cyan-400 font-mono">user / user123</span> (user)
          </p>
        </div>
      </div>
    </div>
  );
}
