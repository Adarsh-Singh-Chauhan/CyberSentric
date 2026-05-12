import { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import RiskScore from './components/RiskScore';
import AgentPanel from './components/AgentPanel';
import ThreatFeed from './components/ThreatFeed';
import { ThreatLineChart, AttackPieChart } from './components/Charts';
import ActionHistory from './components/ActionHistory';
import InputAnalyzer from './components/InputAnalyzer';
import RedTeamPanel from './components/RedTeamPanel';
import LoginScreen from './components/LoginScreen';
import CyberGlobe from './components/CyberGlobe';
import CyberChatbot from './components/CyberChatbot';
import { useWebSocket } from './hooks/useWebSocket';
import { api } from './services/api';
import { Shield, Activity, AlertTriangle, Zap } from 'lucide-react';

export default function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboard, setDashboard] = useState(null);
  const [stats, setStats] = useState(null);
  const [latestSeverity, setLatestSeverity] = useState('none');
  const { messages, connected } = useWebSocket();

  // Check existing token on mount
  useEffect(() => {
    const token = localStorage.getItem('cs_token');
    if (token) {
      api.getMe().then(u => setUser(u)).catch(() => {
        localStorage.removeItem('cs_token');
      });
    }
  }, []);

  // Poll dashboard data
  const fetchData = useCallback(async () => {
    if (!user) return;
    try {
      const [dash, st] = await Promise.all([api.getDashboard(), api.getStats()]);
      setDashboard(dash);
      setStats(st);
    } catch (e) {
      console.error('Fetch error:', e);
    }
  }, [user]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // Track latest severity from WebSocket events
  useEffect(() => {
    if (messages.length > 0) {
      const latest = messages[0];
      if (latest?.data?.severity && latest.data.severity !== 'none') {
        setLatestSeverity(latest.data.severity);
        setTimeout(() => setLatestSeverity('none'), 10000);
      }
    }
  }, [messages]);

  const handleAnalysisResult = (result) => {
    if (result?.severity) {
      setLatestSeverity(result.severity);
      setTimeout(() => setLatestSeverity('none'), 10000);
    }
    fetchData();
  };

  const handleLogout = () => {
    localStorage.removeItem('cs_token');
    setUser(null);
  };

  if (!user) return <LoginScreen onLogin={setUser} />;

  const agents = dashboard?.agents || [];
  const actionHistory = dashboard?.action_history || [];
  const attackTypes = stats?.attack_types || [];

  return (
    <div className="min-h-screen bg-cyber-bg cyber-grid">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="ml-60 min-h-screen flex flex-col">
        <Topbar connected={connected} user={user} stats={stats} messages={messages} onLogout={handleLogout} />

        <div className="flex-1 p-6 space-y-6">
          {/* ─── DASHBOARD ─── */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6 animate-fade-in">
              {/* Stats row */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[
                  { label: 'Total Scans', value: stats?.total_processed || 0, icon: Shield, color: 'cyan', gradient: 'from-cyan-500/20 to-blue-500/20' },
                  { label: 'Threats Found', value: stats?.total_threats || 0, icon: AlertTriangle, color: 'red', gradient: 'from-red-500/20 to-orange-500/20' },
                  { label: 'IPs Blocked', value: stats?.blocked_ips_count || 0, icon: Zap, color: 'orange', gradient: 'from-orange-500/20 to-yellow-500/20' },
                  { label: 'Detection Rate', value: `${Math.round((stats?.detection_rate || 0) * 100)}%`, icon: Activity, color: 'green', gradient: 'from-green-500/20 to-emerald-500/20' },
                ].map((s, i) => (
                  <div key={i} className={`glass rounded-xl p-4 bg-gradient-to-br ${s.gradient} border border-white/5`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-[10px] text-slate-500 uppercase tracking-wider">{s.label}</p>
                        <p className={`text-2xl font-bold font-mono mt-1 text-${s.color}-400`}>{s.value}</p>
                      </div>
                      <s.icon className={`w-8 h-8 text-${s.color}-500/30`} />
                    </div>
                  </div>
                ))}
              </div>

              {/* 3D Globe - Live IP Tracking */}
              <div className="w-full h-[400px] mb-6">
                <CyberGlobe />
              </div>

              {/* Analyzer + Risk */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  <InputAnalyzer onResult={handleAnalysisResult} />
                </div>
                <RiskScore severity={latestSeverity} confidence={stats?.detection_rate || 0} threats={stats?.total_threats || 0} />
              </div>

              {/* Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ThreatLineChart />
                <AttackPieChart data={attackTypes} />
              </div>

              {/* Agent Panel + Feed */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <AgentPanel agents={agents} />
                <ThreatFeed events={messages} />
              </div>

              {/* Action History */}
              <ActionHistory actions={actionHistory} />
            </div>
          )}

          {/* ─── AGENTS ─── */}
          {activeTab === 'agents' && (
            <div className="space-y-6 animate-fade-in">
              <h2 className="text-lg font-bold text-slate-200">AI Agent Status</h2>
              <AgentPanel agents={agents} />
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {agents.map(agent => (
                  <div key={agent.name} className="glass rounded-xl p-5 hover:border-cyan-500/20 transition-all">
                    <h4 className="text-sm font-semibold text-slate-200 mb-3">{agent.name} Agent</h4>
                    <div className="space-y-2 text-xs font-mono">
                      <div className="flex justify-between"><span className="text-slate-500">Status</span><span className="text-slate-300">{agent.status}</span></div>
                      <div className="flex justify-between"><span className="text-slate-500">Processed</span><span className="text-cyan-400">{agent.processed_count}</span></div>
                      <div className="flex justify-between"><span className="text-slate-500">Threats</span><span className="text-red-400">{agent.threats_detected}</span></div>
                      <div className="flex justify-between"><span className="text-slate-500">Last Active</span><span className="text-slate-400">{new Date(agent.last_active).toLocaleTimeString()}</span></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ─── THREATS ─── */}
          {activeTab === 'threats' && (
            <div className="space-y-6 animate-fade-in">
              <h2 className="text-lg font-bold text-slate-200">Threat Analysis</h2>
              <InputAnalyzer onResult={handleAnalysisResult} />
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ThreatLineChart />
                <AttackPieChart data={attackTypes} />
              </div>
              <ActionHistory actions={actionHistory} />
            </div>
          )}

          {/* ─── RED TEAM ─── */}
          {activeTab === 'redteam' && (
            <div className="space-y-6 animate-fade-in">
              <h2 className="text-lg font-bold text-slate-200">Red Team Simulation</h2>
              <RedTeamPanel />
            </div>
          )}

          {/* ─── LOGS ─── */}
          {activeTab === 'logs' && (
            <div className="space-y-6 animate-fade-in">
              <h2 className="text-lg font-bold text-slate-200">Live Event Logs</h2>
              <ThreatFeed events={messages} />
            </div>
          )}

          {/* ─── SETTINGS ─── */}
          {activeTab === 'settings' && (
            <div className="space-y-6 animate-fade-in">
              <h2 className="text-lg font-bold text-slate-200">Settings</h2>
              <div className="glass rounded-xl p-6 max-w-lg">
                <h3 className="text-sm font-semibold text-slate-300 mb-4">Account</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between"><span className="text-slate-500">Username</span><span className="text-slate-200">{user.username}</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Role</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs ${user.role === 'admin' ? 'bg-purple-500/20 text-purple-400' : 'bg-blue-500/20 text-blue-400'}`}>{user.role}</span>
                  </div>
                  <div className="flex justify-between"><span className="text-slate-500">WebSocket</span>
                    <span className={`flex items-center gap-1 ${connected ? 'text-green-400' : 'text-red-400'}`}>
                      <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
                      {connected ? 'Connected' : 'Disconnected'}
                    </span>
                  </div>
                </div>
                <button onClick={handleLogout}
                  className="mt-6 w-full py-2 border border-red-500/30 text-red-400 rounded-lg text-sm hover:bg-red-500/10 transition-all">
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
      
      {/* Floating AI Chatbot */}
      <CyberChatbot />
    </div>
  );
}
