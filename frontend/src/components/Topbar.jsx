import { Shield, Wifi, WifiOff, User, Bell, LogOut, Settings, ChevronDown, CheckCircle2 } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

export default function Topbar({ connected, user, stats, messages = [], onLogout }) {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const notificationRef = useRef(null);
  const profileRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (notificationRef.current && !notificationRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setShowProfile(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const unreadCount = messages.length;

  return (
    <header className="h-14 glass border-b border-cyber-border flex items-center justify-between px-6 sticky top-0 z-30">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className={`pulse-dot ${connected ? 'bg-emerald-400' : 'bg-red-400'}`} />
          <span className="text-xs font-mono text-slate-400">
            {connected ? 'LIVE' : 'OFFLINE'}
          </span>
        </div>
        <div className="h-4 w-px bg-cyber-border" />
        <div className="flex items-center gap-4 text-xs font-mono">
          <span className="text-slate-500">Pipeline: <span className="text-cyan-400">{stats?.pipeline_runs || 0}</span></span>
          <span className="text-slate-500">Threats: <span className="text-red-400">{stats?.total_threats || 0}</span></span>
          <span className="text-slate-500">Blocked: <span className="text-orange-400">{stats?.blocked_ips_count || 0}</span></span>
        </div>
      </div>

      <div className="flex items-center gap-4 relative">
        {/* Notifications */}
        <div className="relative" ref={notificationRef}>
          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            className={`relative p-2 rounded-lg transition-all ${showNotifications ? 'bg-white/10 text-white' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'}`}
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 bg-red-500 rounded-full text-[8px] font-bold flex items-center justify-center text-white border border-slate-900">
                {Math.min(unreadCount, 99)}
              </span>
            )}
          </button>
          
          {showNotifications && (
            <div className="absolute right-0 mt-3 w-80 rounded-xl glass border border-white/10 shadow-2xl overflow-hidden animate-fade-in z-50">
              <div className="px-4 py-3 border-b border-white/10 flex justify-between items-center bg-white/5">
                <h3 className="text-sm font-bold text-slate-200">Notifications</h3>
                {unreadCount > 0 && <span className="text-[10px] bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full">{unreadCount} New</span>}
              </div>
              <div className="max-h-[300px] overflow-y-auto scrollbar-hide">
                {messages.length === 0 ? (
                  <div className="px-4 py-8 flex flex-col items-center justify-center text-slate-500">
                    <CheckCircle2 className="w-8 h-8 mb-2 text-emerald-500/30" />
                    <p className="text-sm">You're all caught up!</p>
                  </div>
                ) : (
                  messages.slice(0, 10).map((msg, i) => (
                    <div key={i} className="px-4 py-3 border-b border-white/5 hover:bg-white/5 transition-colors flex gap-3 cursor-pointer group">
                      <div className={`w-2 h-2 mt-1.5 rounded-full flex-shrink-0 ${msg.data?.severity === 'high' ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]' : msg.data?.severity === 'medium' ? 'bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.5)]' : 'bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]'}`} />
                      <div className="flex-1 overflow-hidden">
                        <div className="flex justify-between items-start">
                          <p className="text-sm text-slate-200 font-medium group-hover:text-cyan-400 transition-colors">{msg.type === 'THREAT_DETECTED' ? 'Threat Detected' : msg.data?.event_type || 'System Event'}</p>
                          <p className="text-[10px] text-slate-500 flex-shrink-0 ml-2">{new Date(msg.timestamp || Date.now()).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</p>
                        </div>
                        <p className="text-xs text-slate-400 mt-1 truncate">{msg.data?.details || msg.data?.description || JSON.stringify(msg.data)}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
              <div className="p-2 bg-black/20 border-t border-white/10">
                <button className="w-full py-1.5 text-xs font-medium text-cyan-400 hover:text-cyan-300 hover:bg-cyan-500/10 rounded-lg transition-colors">
                  View All Activity
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="h-4 w-px bg-cyber-border" />
        
        {/* User Profile */}
        <div className="relative" ref={profileRef}>
          <button 
            onClick={() => setShowProfile(!showProfile)}
            className={`flex items-center gap-2 pl-2 pr-1 py-1 rounded-full transition-all border ${showProfile ? 'bg-white/10 border-white/20' : 'hover:bg-white/5 border-transparent'}`}
          >
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg">
                <User className="w-3.5 h-3.5 text-white" />
              </div>
              <div className="text-left hidden md:block">
                <p className="text-xs text-slate-200 font-medium leading-tight">{user?.username || 'Admin'}</p>
                <p className="text-[10px] text-slate-500 leading-tight capitalize">{user?.role || 'admin'}</p>
              </div>
            </div>
            <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${showProfile ? 'rotate-180' : ''}`} />
          </button>
          
          {showProfile && (
            <div className="absolute right-0 mt-3 w-56 rounded-xl glass border border-white/10 shadow-2xl overflow-hidden py-1 animate-fade-in z-50">
              <div className="px-4 py-3 border-b border-white/10 bg-black/20">
                <p className="text-sm text-slate-200 font-bold">{user?.username || 'Admin User'}</p>
                <p className="text-xs text-slate-500 mt-0.5">{user?.username?.toLowerCase()}@cybersentric.ai</p>
              </div>
              <div className="py-1">
                <button className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-slate-300 hover:bg-white/10 hover:text-white transition-colors group">
                  <Settings className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 transition-colors" /> 
                  Account Settings
                </button>
                <button className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-slate-300 hover:bg-white/10 hover:text-white transition-colors group">
                  <Shield className="w-4 h-4 text-slate-500 group-hover:text-purple-400 transition-colors" /> 
                  Security Preferences
                </button>
              </div>
              <div className="border-t border-white/10 pt-1 mt-1">
                <button 
                  onClick={onLogout} 
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-400 hover:bg-red-500/10 transition-colors"
                >
                  <LogOut className="w-4 h-4" /> 
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
