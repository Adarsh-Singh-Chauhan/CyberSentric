import React, { useState, useEffect } from 'react';
import CyberGlobe from './CyberGlobe';
import { api } from '../services/api';
import { Shield, Activity, MapPin, Zap } from 'lucide-react';

export default function GlobalMonitor() {
  const [threats, setThreats] = useState([]);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    let mounted = true;
    const fetchData = async () => {
      try {
        const [threatData, statData] = await Promise.all([
          api.getThreats(),
          api.getStats()
        ]);
        if (mounted) {
          setThreats(threatData.recent_alerts || []);
          setStats(statData);
        }
      } catch (e) {
        console.error("Monitor fetch error:", e);
      }
    };
    
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col lg:flex-row gap-6 animate-fade-in">
      {/* Globe Container */}
      <div className="flex-1 glass rounded-2xl border border-white/10 relative overflow-hidden flex flex-col shadow-2xl shadow-cyan-900/20">
        <div className="absolute top-0 left-0 w-full p-6 z-10 pointer-events-none flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-black tracking-tight text-white mb-1 drop-shadow-md">GLOBAL THREAT MAP</h2>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_10px_#22d3ee]"></div>
              <p className="text-xs font-mono text-cyan-400">LIVE SATELLITE LINK ACTIVE</p>
            </div>
          </div>
          
          <div className="glass px-4 py-3 rounded-xl border border-white/10 flex items-center gap-6">
            <div className="text-center">
              <p className="text-[10px] text-slate-400 uppercase font-bold tracking-wider mb-1">Total Blocked</p>
              <p className="text-xl font-mono text-orange-400 font-bold">{stats?.blocked_ips_count || 0}</p>
            </div>
            <div className="w-px h-8 bg-white/10"></div>
            <div className="text-center">
              <p className="text-[10px] text-slate-400 uppercase font-bold tracking-wider mb-1">Detection Rate</p>
              <p className="text-xl font-mono text-emerald-400 font-bold">{Math.round((stats?.detection_rate || 0) * 100)}%</p>
            </div>
          </div>
        </div>

        <div className="flex-1 w-full h-full min-h-[400px]">
          <CyberGlobe />
        </div>
      </div>

      {/* Activity Panel */}
      <div className="w-full lg:w-96 glass rounded-2xl border border-white/10 flex flex-col shadow-xl">
        <div className="p-5 border-b border-white/10 bg-black/20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            <h3 className="font-bold text-slate-200">Global Activity</h3>
          </div>
          <span className="text-[10px] bg-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded-full font-mono uppercase tracking-wider">
            Real-Time
          </span>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-hide">
          {threats.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 opacity-50">
              <Shield className="w-12 h-12 mb-3" />
              <p className="text-sm font-medium">No recent global activity</p>
            </div>
          ) : (
            threats.slice(0, 15).map((threat, idx) => (
              <div key={idx} className="glass p-3 rounded-xl border border-white/5 hover:border-cyan-500/30 transition-all group">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${threat.severity === 'high' ? 'bg-red-500 shadow-[0_0_8px_#ef4444]' : 'bg-orange-500 shadow-[0_0_8px_#f97316]'}`} />
                    <span className="text-xs font-bold text-slate-200 uppercase tracking-wide">{threat.threat_type || 'Unknown'}</span>
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">
                    {new Date(threat.timestamp || Date.now()).toLocaleTimeString()}
                  </span>
                </div>
                
                <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
                  <MapPin className="w-3 h-3 text-slate-500" />
                  <span className="font-mono text-cyan-400/80 group-hover:text-cyan-400 transition-colors">
                    {threat.source_ip || '192.168.x.x'}
                  </span>
                </div>
                
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <Zap className="w-3 h-3 text-slate-500" />
                  <span className="truncate">{threat.details || 'Suspicious global pattern detected'}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
