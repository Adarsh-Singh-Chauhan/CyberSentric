import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';

const COLORS = ['#06b6d4', '#8b5cf6', '#ef4444', '#f97316', '#22c55e', '#ec4899', '#eab308'];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass rounded-lg px-3 py-2 text-xs border border-cyber-border">
      <p className="text-slate-400 mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }} className="font-mono">{p.name}: {p.value}</p>
      ))}
    </div>
  );
};

export function ThreatLineChart({ data = [] }) {
  const chartData = data.length > 0 ? data : [
    { time: '00:00', threats: 2 }, { time: '01:00', threats: 1 }, { time: '02:00', threats: 5 },
    { time: '03:00', threats: 3 }, { time: '04:00', threats: 8 }, { time: '05:00', threats: 4 },
    { time: '06:00', threats: 6 }, { time: '07:00', threats: 2 }, { time: '08:00', threats: 7 },
    { time: '09:00', threats: 12 }, { time: '10:00', threats: 9 }, { time: '11:00', threats: 5 },
  ];

  return (
    <div className="glass rounded-xl p-5">
      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">Threat Frequency</h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(30,41,59,0.5)" />
          <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#64748b' }} stroke="transparent" />
          <YAxis tick={{ fontSize: 10, fill: '#64748b' }} stroke="transparent" />
          <Tooltip content={<CustomTooltip />} />
          <Line type="monotone" dataKey="threats" stroke="#06b6d4" strokeWidth={2}
            dot={{ r: 3, fill: '#06b6d4' }} activeDot={{ r: 5, stroke: '#06b6d4', strokeWidth: 2, fill: '#0a0e1a' }}
            filter="url(#glow)" />
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
          </defs>
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function AttackPieChart({ data = [] }) {
  const chartData = data.length > 0 ? data : [
    { name: 'Prompt Injection', value: 35 }, { name: 'XSS', value: 25 },
    { name: 'SQL Injection', value: 20 }, { name: 'Brute Force', value: 12 },
    { name: 'Command Injection', value: 8 },
  ];

  return (
    <div className="glass rounded-xl p-5">
      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">Attack Distribution</h3>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie data={chartData} cx="50%" cy="50%" innerRadius={50} outerRadius={80}
            paddingAngle={3} dataKey="value" stroke="transparent">
            {chartData.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: '10px', color: '#94a3b8' }}
            formatter={(value) => <span className="text-slate-400">{value}</span>} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
