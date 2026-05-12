import { useEffect, useState, useRef } from 'react';
import Globe from 'react-globe.gl';

export default function CyberGlobe({ attacks = [] }) {
  const globeEl = useRef();
  const [arcsData, setArcsData] = useState([]);
  const [pointsData, setPointsData] = useState([]);

  useEffect(() => {
    // Generate some cool default animation data if no live attacks
    const defaultPoints = [
      { lat: 37.7749, lng: -122.4194, size: 0.1, color: '#ef4444' }, // SF
      { lat: 51.5074, lng: -0.1278, size: 0.1, color: '#3b82f6' }, // London
      { lat: 35.6895, lng: 139.6917, size: 0.1, color: '#00f0ff' }, // Tokyo
      { lat: 55.7558, lng: 37.6173, size: 0.1, color: '#a855f7' }, // Moscow
    ];

    const defaultArcs = [
      { startLat: 55.7558, startLng: 37.6173, endLat: 37.7749, endLng: -122.4194, color: '#ef4444' },
      { startLat: 35.6895, startLng: 139.6917, endLat: 51.5074, endLng: -0.1278, color: '#00f0ff' }
    ];

    setPointsData(defaultPoints);
    setArcsData(defaultArcs);

    // Auto-rotate the globe slowly
    if (globeEl.current) {
      globeEl.current.controls().autoRotate = true;
      globeEl.current.controls().autoRotateSpeed = 1.5;
    }
  }, []);

  return (
    <div className="w-full h-full flex items-center justify-center relative overflow-hidden rounded-xl border border-white/10 glass">
      {/* Absolute positioning to fill the container properly */}
      <div className="absolute inset-0">
        <Globe
          ref={globeEl}
          globeImageUrl="//unpkg.com/three-globe/example/img/earth-dark.jpg"
          backgroundColor="rgba(0,0,0,0)"
          
          arcsData={arcsData}
          arcColor="color"
          arcDashLength={0.4}
          arcDashGap={0.2}
          arcDashAnimateTime={1500}
          arcAltitude={0.2}
          
          pointsData={pointsData}
          pointColor="color"
          pointAltitude={0.05}
          pointRadius="size"
          
          width={800} // Will need dynamic sizing in a real app, but 800 works for a dashboard widget
          height={500}
        />
      </div>
      
      {/* Overlay UI */}
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
