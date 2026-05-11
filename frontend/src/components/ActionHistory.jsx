import { Ban, ShieldAlert, Bell, Zap, Clock } from 'lucide-react';

const ACTION_ICONS = {
  block_ip: Ban,
  alert_admin: Bell,
  rate_limit: ShieldAlert,
  sanitize_input: Zap,
  log_critical: ShieldAlert,
  log_warning: Bell,
  log_info: Bell,
};

const ACTION_COLORS = {
  block_ip: 'text-red-400 bg-red-500/10',
  alert_admin: 'text-orange-400 bg-orange-500/10',
  rate_limit: 'text-yellow-400 bg-yellow-500/10',
  sanitize_input: 'text-blue-400 bg-blue-500/10',
  log_critical: 'text-red-400 bg-red-500/10',
  log_warning: 'text-yellow-400 bg-yellow-500/10',
  log_info: 'text-green-400 bg-green-500/10',
};

function formatTime(ts) {
  if (!ts) return '';
  const d = new Date(ts);
  return d.toLocaleTimeString('en-US', { hour12: false });
}

export default function ActionHistory({ actions = [] }) {
  return (
    <div className="glass rounded-xl p-5">
      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">Action History</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-cyber-border">
              <th className="text-left py-2 px-2 text-slate-500 font-medium">Action</th>
              <th className="text-left py-2 px-2 text-slate-500 font-medium">Target</th>
              <th className="text-left py-2 px-2 text-slate-500 font-medium">Description</th>
              <th className="text-left py-2 px-2 text-slate-500 font-medium">Status</th>
              <th className="text-left py-2 px-2 text-slate-500 font-medium">Time</th>
            </tr>
          </thead>
          <tbody>
            {actions.length === 0 ? (
              <tr><td colSpan={5} className="text-center py-8 text-slate-600">No actions recorded yet</td></tr>
            ) : (
              actions.slice(0, 20).map((action, i) => {
                const Icon = ACTION_ICONS[action.action_type] || Zap;
                const color = ACTION_COLORS[action.action_type] || 'text-slate-400 bg-slate-500/10';
                return (
                  <tr key={i} className="border-b border-cyber-border/30 hover:bg-white/[0.02] transition-all">
                    <td className="py-2.5 px-2">
                      <div className="flex items-center gap-2">
                        <div className={`w-6 h-6 rounded flex items-center justify-center ${color}`}>
                          <Icon className="w-3 h-3" />
                        </div>
                        <span className="font-mono text-slate-300">{action.action_type}</span>
                      </div>
                    </td>
                    <td className="py-2.5 px-2 font-mono text-cyan-400">{action.target || '-'}</td>
                    <td className="py-2.5 px-2 text-slate-400 max-w-[200px] truncate">{action.description || '-'}</td>
                    <td className="py-2.5 px-2">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                        action.success ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                      }`}>
                        {action.success ? 'SUCCESS' : 'FAILED'}
                      </span>
                    </td>
                    <td className="py-2.5 px-2 text-slate-500 font-mono flex items-center gap-1">
                      <Clock className="w-3 h-3" />{formatTime(action.timestamp)}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
