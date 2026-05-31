import { useEffect, useState, useRef } from 'react';
import Globe from 'react-globe.gl';
import { api } from '../services/api';


export default function CyberGlobe({ attacks = [] }) {
  const globeEl = useRef();
  const [arcsData, setArcsData] = useState([]);
  const [pointsData, setPointsData] = useState([]);

  useEffect(() => {
    let mounted = true;

    // Simple hash to generate consistent lat/lng from IP string
    const ipToLocation = (ip) => {
      let hash = 0;
      for (let i = 0; i < ip.length; i++) {
        hash = ip.charCodeAt(i) + ((hash << 5) - hash);
      }
      const lat = (hash % 160) - 80; // -80 to 80
      const lng = ((hash >> 8) % 360) - 180; // -180 to 180
      return { lat, lng };
    };

    const fetchThreats = async () => {
      try {
        const data = await api.getThreats();
        if (!mounted) return;
        
        const recentAlerts = data.recent_alerts || [];
        const blockedIps = data.blocked_ips || [];
        
        const points = [];
        const arcs = [];
        
        // Define a central "server" location (e.g., Data Center)
        const serverLoc = { lat: 37.7749, lng: -122.4194 }; // San Francisco

        recentAlerts.forEach((alert, i) => {
          const ip = alert.source_ip || `unknown-${i}`;
          const loc = ipToLocation(ip);
          
          points.push({
            lat: loc.lat,
            lng: loc.lng,
            size: 0.15,
            color: alert.severity === 'high' ? '#ef4444' : '#f59e0b',
            label: `Threat: ${ip} (${alert.threat_type})`
          });
          
          arcs.push({
            startLat: loc.lat,
            startLng: loc.lng,
            endLat: serverLoc.lat,
            endLng: serverLoc.lng,
            color: alert.severity === 'high' ? ['#ef4444', '#ef444400'] : ['#f59e0b', '#f59e0b00']
          });
        });

        // Ensure we always have some activity to keep the globe interesting
        if (points.length === 0) {
          const defaultPoints = [
            { lat: 37.7749, lng: -122.4194, size: 0.14, color: '#ef4444', label: 'San Francisco Server' },
            { lat: 51.5074, lng: -0.1278, size: 0.12, color: '#3b82f6', label: 'London Node' },
            { lat: 35.6895, lng: 139.6917, size: 0.12, color: '#00f0ff', label: 'Tokyo Node' },
          ];
          setPointsData(defaultPoints);
          setArcsData([
            { startLat: 51.5074, startLng: -0.1278, endLat: 37.7749, endLng: -122.4194, color: ['#3b82f6', '#ef4444'] },
            { startLat: 35.6895, startLng: 139.6917, endLat: 37.7749, endLng: -122.4194, color: ['#00f0ff', '#ef4444'] }
          ]);
        } else {
          setPointsData([...points, { ...serverLoc, size: 0.2, color: '#3b82f6', label: 'Main Server' }]);
          setArcsData(arcs);
        }
      } catch (err) {
        console.error("Globe data fetch error:", err);
      }
    };

    fetchThreats();
    const interval = setInterval(fetchThreats, 5000);

    const timeout = setTimeout(() => {
      if (globeEl.current?.controls) {
        const controls = globeEl.current.controls();
        if (controls) {
          controls.autoRotate = true;
          controls.autoRotateSpeed = 1.2;
          controls.enableZoom = true;
          controls.minDistance = 250;
          controls.maxDistance = 900;
        }
      }
    }, 100);

    return () => {
      mounted = false;
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, []);

  return (
    <div className="w-full h-full flex items-center justify-center relative overflow-hidden rounded-xl border border-white/10 glass">
      <div className="absolute inset-0">
        <Globe
          ref={globeEl}
          globeImageUrl="https://unpkg.com/three-globe/example/img/earth-dark.jpg"
          bumpImageUrl="https://unpkg.com/three-globe/example/img/earth-topology.png"
          backgroundColor="rgba(0, 0, 0, 0)"
          showAtmosphere={true}
          atmosphereColor="rgba(56, 189, 248, 0.18)"
          atmosphereAltitude={0.16}
          globeAltitude={0.02}
          arcsData={arcsData}
          arcColor="color"
          arcDashLength={0.3}
          arcDashGap={0.25}
          arcDashAnimateTime={2000}
          arcAltitude={0.25}
          pointsData={pointsData}
          pointColor="color"
          pointAltitude={0.03}
          pointRadius={(d) => d.size}
          pointLabel={(d) => `${d.label || 'Threat'} · ${d.lat.toFixed(2)}, ${d.lng.toFixed(2)}`}
          width={null}
          height={null}
          style={{ width: '100%', height: '100%' }}
        />
      </div>

      <div className="absolute top-4 left-4 z-10">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse shadow-[0_0_10px_#ef4444]"></div>
          <h3 className="text-xs font-bold text-slate-200 tracking-wider">LIVE THREAT MAP</h3>
        </div>
        <p className="text-[10px] text-slate-400 font-mono">GLOBAL IP TRACKING ACTIVE</p>
      </div>
    </div>
  );
}
