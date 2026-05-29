import { useEffect, useState, useRef } from 'react';
import Globe from 'react-globe.gl';

export default function CyberGlobe({ attacks = [] }) {
  const globeEl = useRef();
  const [arcsData, setArcsData] = useState([]);
  const [pointsData, setPointsData] = useState([]);

  useEffect(() => {
    // Generate some cool default animation data if no live attacks
    const defaultPoints = [
      { lat: 37.7749, lng: -122.4194, size: 0.14, color: '#ef4444', label: 'San Francisco' },
      { lat: 51.5074, lng: -0.1278, size: 0.12, color: '#3b82f6', label: 'London' },
      { lat: 35.6895, lng: 139.6917, size: 0.12, color: '#00f0ff', label: 'Tokyo' },
      { lat: 55.7558, lng: 37.6173, size: 0.12, color: '#a855f7', label: 'Moscow' },
    ];

    const defaultArcs = [
      { startLat: 55.7558, startLng: 37.6173, endLat: 37.7749, endLng: -122.4194, color: '#ef4444' },
      { startLat: 35.6895, startLng: 139.6917, endLat: 51.5074, endLng: -0.1278, color: '#00f0ff' },
    ];

    setPointsData(defaultPoints);
    setArcsData(defaultArcs);
  }, []);

  useEffect(() => {
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

    return () => clearTimeout(timeout);
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
