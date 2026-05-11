import { AlertTriangle, ShieldAlert, ShieldCheck, Info, Clock } from 'lucide-react';

const SEV_ICON = {
  critical: ShieldAlert,
  high: AlertTriangle,
  medium: AlertTriangle,
  low: Info,
  none: ShieldCheck,
};

const SEV_COLOR = {
  critical: 'text-red-400 bg-red-500/10',
  high: 'text-orange-400 bg-orange-500/10',
  medium: 'text-yellow-400 bg-yellow-500/10',
  low: 'text-blue-400 bg-blue-500/10',
  none: 'text-green-400 bg-green-500/10',
};

function formatTime(ts) {
  if (!ts) return '';
  const d = new Date(ts);
  return d.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

export default function ThreatFeed({ events = [] }) {
  const threatEvents = events
    .filter(e => e.type === 'threat_event' || e.type === 'threat_response' || e.type === 'system_metric')
    .slice(0, 30);

  return (
    <div className="glass rounded-xl p-5 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Live Threat Feed</h3>
        <div className="flex items-center gap-1.5">
          <div className="pulse-dot bg-emerald-400" />
          <span className="text-[10px] font-mono text-slate-500">STREAMING</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        {threatEvents.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-slate-500">
            <ShieldCheck className="w-8 h-8 mb-2 text-green-500/50" />
            <p className="text-sm">No events yet. System is monitoring...</p>
            <p className="text-xs mt-1">Submit an input to analyze, or run a Red Team simulation.</p>
          </div>
        ) : (
          threatEvents.map((event, i) => {
            const data = event.data || {};
            const severity = data.severity || 'none';
            const Icon = SEV_ICON[severity] || Info;
            const colorClass = SEV_COLOR[severity] || SEV_COLOR.none;

            return (
              <div key={i} className="flex items-start gap-3 p-2.5 rounded-lg bg-white/[0.02] hover:bg-white/[0.04] transition-all animate-slide-up border border-transparent hover:border-white/5">
                <div className={`w-7 h-7 rounded-md flex items-center justify-center flex-shrink-0 ${colorClass}`}>
                  <Icon className="w-3.5 h-3.5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium text-slate-300 truncate">
                      {data.threat_type || data.event_type || event.type || 'Event'}
                    </span>
                    <span className={`text-[9px] font-mono uppercase px-1.5 py-0.5 rounded-full ${colorClass}`}>
                      {severity}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-0.5 truncate">
                    {data.description || data.message || JSON.stringify(data).slice(0, 100)}
                  </p>
                </div>
                <div className="flex items-center gap-1 text-[10px] text-slate-600 flex-shrink-0">
                  <Clock className="w-3 h-3" />
                  {formatTime(event.timestamp)}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
