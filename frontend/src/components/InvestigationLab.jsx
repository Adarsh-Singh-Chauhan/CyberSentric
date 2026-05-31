import React, { useState } from 'react';
import { 
  Bitcoin, Mail, Hash, Image as ImageIcon, Smartphone, 
  Globe, Network, Mic, Terminal, Power
} from 'lucide-react';

const LAB_TOOLS = [
  { id: 'bitcoin', label: 'Bitcoin Finder', icon: Bitcoin },
  { id: 'email', label: 'Email Header Analysis', icon: Mail },
  { id: 'hash', label: 'Hash Value Calculator', icon: Hash },
  { id: 'exif', label: 'Image Exif Data', icon: ImageIcon },
  { id: 'imei', label: 'IMEI Check Digit', icon: Smartphone },
  { id: 'ip', label: 'IP Lookup', icon: Globe },
  { id: 'mac', label: 'MAC Lookup', icon: Network },
  { id: 'voice', label: 'Voice Analysis', icon: Mic },
];

export default function InvestigationLab() {
  const [activeTool, setActiveTool] = useState('email');
  const [headerInput, setHeaderInput] = useState('');

  return (
    <div className="h-[calc(100vh-8rem)] flex rounded-2xl overflow-hidden border border-[#00ffff]/20 bg-[#050b14] shadow-2xl shadow-[#00ffff]/10 animate-fade-in">
      
      {/* Secondary Sidebar (Investigation Lab Menu) */}
      <div className="w-64 bg-[#0a1526] border-r border-[#00ffff]/20 flex flex-col relative z-10">
        
        {/* Portal Header */}
        <div className="p-4 border-b border-[#00ffff]/20 flex items-center gap-3 bg-[#0a1526]/80 backdrop-blur-md">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00ffff] to-blue-600 flex items-center justify-center shadow-[0_0_15px_rgba(0,255,255,0.4)]">
            <Terminal className="w-5 h-5 text-[#050b14]" />
          </div>
          <div>
            <h2 className="text-xs font-black text-[#00ffff] tracking-widest uppercase">Academy Portal</h2>
            <p className="text-[10px] text-slate-400 uppercase tracking-widest mt-0.5">Investigation Lab</p>
          </div>
        </div>

        {/* Tools List */}
        <div className="flex-1 overflow-y-auto py-4 scrollbar-hide">
          <h3 className="px-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Tools</h3>
          <ul className="space-y-1 px-2">
            {LAB_TOOLS.map(tool => {
              const isActive = activeTool === tool.id;
              const Icon = tool.icon;
              return (
                <li key={tool.id}>
                  <button
                    onClick={() => setActiveTool(tool.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                      isActive 
                        ? 'bg-[#00ffff]/10 text-[#00ffff] shadow-[inset_2px_0_0_#00ffff]' 
                        : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? 'text-[#00ffff]' : 'text-slate-500'}`} />
                    {tool.label}
                  </button>
                </li>
              );
            })}
          </ul>
        </div>

        {/* Bottom Status Panel */}
        <div className="p-4 border-t border-[#00ffff]/20 bg-[#060e1a]">
          <div className="glass rounded-xl p-3 border border-[#00ffff]/10 mb-3 flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[#00ffff]/10 flex items-center justify-center">
              <Network className="w-4 h-4 text-[#00ffff]" />
            </div>
            <div>
              <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">System IP</p>
              <p className="text-xs font-mono text-[#00ffff] font-bold mt-0.5">49.43.42.197</p>
            </div>
          </div>
          <button className="w-full py-2.5 rounded-lg bg-red-500/10 text-red-500 border border-red-500/20 text-xs font-bold uppercase tracking-wider hover:bg-red-500 hover:text-white transition-all flex items-center justify-center gap-2">
            <Power className="w-4 h-4" />
            Terminate Session
          </button>
        </div>
      </div>

      {/* Main Tool Area */}
      <div className="flex-1 bg-[#050b14] relative overflow-y-auto">
        {/* Subtle Cyber Grid Background */}
        <div className="absolute inset-0 opacity-20 pointer-events-none bg-[linear-gradient(to_right,#00ffff_1px,transparent_1px),linear-gradient(to_bottom,#00ffff_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_50%,#000_70%,transparent_100%)]"></div>

        {activeTool === 'email' ? (
          <div className="relative z-10 p-8 max-w-4xl mx-auto animate-fade-in mt-8">
            <div className="mb-8">
              <h1 className="text-2xl font-bold text-white mb-2 flex items-center gap-3">
                <Mail className="w-6 h-6 text-[#00ffff]" />
                Email Header Analysis
              </h1>
              <p className="text-sm text-slate-400">Trace the origin and path of fraudulent or malicious emails.</p>
            </div>

            {/* Futuristic Input Area */}
            <div className="relative mb-6">
              <div className="absolute -inset-[1px] bg-gradient-to-r from-[#00ffff] to-transparent rounded-xl opacity-50 blur-[2px]"></div>
              <div className="relative bg-[#0a1526] rounded-xl border border-[#00ffff]/30 p-1">
                <div className="px-4 py-2 border-b border-[#00ffff]/20 flex justify-between items-center">
                  <span className="text-[10px] font-bold text-[#00ffff] uppercase tracking-widest">Paste Full Email Header</span>
                  <div className="flex gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-[#00ffff]/50"></div>
                    <div className="w-2 h-2 rounded-full bg-[#00ffff]/50"></div>
                  </div>
                </div>
                <textarea 
                  value={headerInput}
                  onChange={(e) => setHeaderInput(e.target.value)}
                  className="w-full h-64 bg-transparent border-none outline-none p-4 text-sm font-mono text-slate-300 placeholder-slate-600 resize-none"
                  placeholder="Paste the raw headers here (e.g. Delivered-To, Received, From, etc.)..."
                />
              </div>
            </div>

            {/* Analyze Button */}
            <button className="w-full py-4 bg-gradient-to-r from-[#00ffff]/80 to-[#00ffff] text-[#050b14] font-black uppercase tracking-widest text-sm rounded-xl shadow-[0_0_20px_rgba(0,255,255,0.3)] hover:shadow-[0_0_30px_rgba(0,255,255,0.5)] transition-all flex items-center justify-center gap-2 transform hover:-translate-y-0.5">
              <Terminal className="w-5 h-5" />
              Analyze Headers
            </button>

            {/* Instructions */}
            <div className="mt-12 p-6 rounded-xl border border-white/5 bg-white/[0.02]">
              <h3 className="text-sm font-bold text-white mb-4">How to get headers?</h3>
              <ul className="space-y-3 text-sm text-slate-400">
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#00ffff] mt-1.5 shadow-[0_0_5px_#00ffff]"></div>
                  <span><strong className="text-slate-200">Gmail:</strong> Open email → More (three dots) → "Show original"</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#00ffff] mt-1.5 shadow-[0_0_5px_#00ffff]"></div>
                  <span><strong className="text-slate-200">Outlook:</strong> Open email → More actions → View → "Message details"</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#00ffff] mt-1.5 shadow-[0_0_5px_#00ffff]"></div>
                  <span><strong className="text-slate-200">Yahoo:</strong> Open email → More (three dots) → "View raw message"</span>
                </li>
              </ul>
            </div>
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 animate-fade-in">
            <Terminal className="w-16 h-16 mb-4 opacity-20" />
            <p className="text-lg font-medium text-slate-400">Initialize {LAB_TOOLS.find(t => t.id === activeTool)?.label} Interface...</p>
            <p className="text-sm mt-2 text-[#00ffff]/60 font-mono">Module pending deployment.</p>
          </div>
        )}
      </div>
    </div>
  );
}
