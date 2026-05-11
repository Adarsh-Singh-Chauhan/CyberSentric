import { useState } from 'react';
import { Swords, Play, Loader2, CheckCircle, XCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { api } from '../services/api';

const SIM_TYPES = [
  { id: 'full', label: 'Full Suite', desc: 'Run all attack simulations' },
  { id: 'prompt_injection', label: 'Prompt Injection', desc: 'Test LLM prompt injection defense' },
  { id: 'xss', label: 'XSS', desc: 'Test cross-site scripting defense' },
  { id: 'sqli', label: 'SQL Injection', desc: 'Test SQL injection defense' },
  { id: 'command_injection', label: 'Command Injection', desc: 'Test command injection defense' },
  { id: 'brute_force', label: 'Brute Force', desc: 'Test brute force detection' },
];

export default function RedTeamPanel() {
  const [loading, setLoading] = useState(false);
  const [selectedType, setSelectedType] = useState('full');
  const [result, setResult] = useState(null);
  const [expanded, setExpanded] = useState({});

  const runSim = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await api.runSimulation(selectedType);
      setResult(res);
    } catch (err) {
      setResult({ error: err.message });
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (rate) => {
    if (rate >= 0.9) return 'text-green-400';
    if (rate >= 0.7) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="space-y-4">
      <div className="glass rounded-xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <Swords className="w-5 h-5 text-red-400" />
          <h3 className="text-sm font-semibold text-slate-200">Red Team Simulation</h3>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-green-500/20 text-green-400 font-mono">SAFE</span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mb-4">
          {SIM_TYPES.map(t => (
            <button key={t.id} onClick={() => setSelectedType(t.id)}
              className={`p-2.5 rounded-lg text-left transition-all border ${
                selectedType === t.id
                  ? 'border-red-500/30 bg-red-500/10 text-red-400'
                  : 'border-cyber-border bg-white/[0.02] text-slate-400 hover:border-white/10'
              }`}>
              <p className="text-xs font-medium">{t.label}</p>
              <p className="text-[10px] text-slate-500 mt-0.5">{t.desc}</p>
            </button>
          ))}
        </div>

        <button onClick={runSim} disabled={loading}
          className="w-full py-2.5 bg-gradient-to-r from-red-500 to-rose-600 rounded-lg text-sm font-medium text-white hover:opacity-90 transition-all disabled:opacity-40 flex items-center justify-center gap-2">
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          {loading ? 'Running Simulation...' : 'Launch Simulation'}
        </button>
      </div>

      {result && !result.error && (
        <div className="glass rounded-xl p-5 animate-slide-up">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-200">Results</h3>
            <span className={`text-lg font-bold font-mono ${getScoreColor(result.overall_detection_rate || result.detection_rate || 0)}`}>
              {Math.round((result.overall_detection_rate || result.detection_rate || 0) * 100)}%
            </span>
          </div>

          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="p-3 rounded-lg bg-white/[0.03] text-center">
              <p className="text-lg font-bold text-cyan-400 font-mono">{result.tests_run || 0}</p>
              <p className="text-[10px] text-slate-500">Tests Run</p>
            </div>
            <div className="p-3 rounded-lg bg-white/[0.03] text-center">
              <p className="text-lg font-bold text-green-400 font-mono">{result.detected || 0}</p>
              <p className="text-[10px] text-slate-500">Detected</p>
            </div>
            <div className="p-3 rounded-lg bg-white/[0.03] text-center">
              <p className="text-lg font-bold text-red-400 font-mono">{result.missed || (result.tests_run - result.detected) || 0}</p>
              <p className="text-[10px] text-slate-500">Missed</p>
            </div>
          </div>

          {result.suites && Object.entries(result.suites).map(([name, suite]) => (
            <div key={name} className="mb-2 border border-cyber-border/50 rounded-lg overflow-hidden">
              <button onClick={() => setExpanded(p => ({ ...p, [name]: !p[name] }))}
                className="w-full flex items-center justify-between p-3 hover:bg-white/[0.02] transition-all">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-slate-300 capitalize">{name.replace('_', ' ')}</span>
                  <span className={`text-[10px] font-mono ${getScoreColor(suite.detection_rate)}`}>
                    {Math.round(suite.detection_rate * 100)}%
                  </span>
                </div>
                {expanded[name] ? <ChevronUp className="w-3.5 h-3.5 text-slate-500" /> : <ChevronDown className="w-3.5 h-3.5 text-slate-500" />}
              </button>
              {expanded[name] && suite.details && (
                <div className="px-3 pb-3 space-y-1">
                  {suite.details.map((d, i) => (
                    <div key={i} className="flex items-center gap-2 text-[11px]">
                      {d.detected ? <CheckCircle className="w-3 h-3 text-green-400" /> : <XCircle className="w-3 h-3 text-red-400" />}
                      <span className="font-mono text-slate-400 truncate">{d.input}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {result?.error && (
        <div className="glass rounded-xl p-4 border border-red-500/30 text-red-400 text-xs">
          {result.error}. Make sure you're logged in as admin (admin/admin123).
        </div>
      )}
    </div>
  );
}
