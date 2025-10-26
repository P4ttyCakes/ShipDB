const WaveBackground = () => {
  return (
    <div className="absolute bottom-0 left-0 w-full overflow-hidden leading-none">
      <svg
        className="relative block w-[200%] h-[200px] md:h-[320px] lg:h-[400px] animate-wave"
        xmlns="http://www.w3.org/2000/svg"
        xmlnsXlink="http://www.w3.org/1999/xlink"
        viewBox="0 0 1440 400"
        preserveAspectRatio="none"
      >
        <defs>
          <linearGradient id="wave-gradient-1" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="hsl(215 25% 22%)" stopOpacity="0.5" />
            <stop offset="100%" stopColor="hsl(215 30% 28%)" stopOpacity="0.5" />
          </linearGradient>
          <linearGradient id="wave-gradient-2" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="hsl(215 20% 18%)" stopOpacity="0.7" />
            <stop offset="100%" stopColor="hsl(215 25% 24%)" stopOpacity="0.7" />
          </linearGradient>
          <linearGradient id="wave-gradient-3" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="hsl(220 18% 16%)" stopOpacity="0.8" />
            <stop offset="100%" stopColor="hsl(215 22% 20%)" stopOpacity="0.9" />
          </linearGradient>
        </defs>
        
        {/* Wave 1 - Slowest */}
        <path
          fill="url(#wave-gradient-1)"
          d="M0,180 C240,100 480,100 720,180 C960,260 1200,260 1440,180 L1440,400 L0,400 Z"
          opacity="0.7"
        >
          <animate
            attributeName="d"
            dur="20s"
            repeatCount="indefinite"
            values="
              M0,180 C240,100 480,100 720,180 C960,260 1200,260 1440,180 L1440,400 L0,400 Z;
              M0,150 C240,230 480,230 720,150 C960,70 1200,70 1440,150 L1440,400 L0,400 Z;
              M0,180 C240,100 480,100 720,180 C960,260 1200,260 1440,180 L1440,400 L0,400 Z
            "
          />
        </path>
        
        {/* Wave 2 - Medium */}
        <path
          fill="url(#wave-gradient-2)"
          d="M0,220 C240,140 480,140 720,220 C960,300 1200,300 1440,220 L1440,400 L0,400 Z"
          opacity="0.8"
        >
          <animate
            attributeName="d"
            dur="15s"
            repeatCount="indefinite"
            values="
              M0,220 C240,140 480,140 720,220 C960,300 1200,300 1440,220 L1440,400 L0,400 Z;
              M0,250 C240,330 480,330 720,250 C960,170 1200,170 1440,250 L1440,400 L0,400 Z;
              M0,220 C240,140 480,140 720,220 C960,300 1200,300 1440,220 L1440,400 L0,400 Z
            "
          />
        </path>
        
        {/* Wave 3 - Fastest */}
        <path
          fill="url(#wave-gradient-3)"
          d="M0,280 C240,220 480,220 720,280 C960,340 1200,340 1440,280 L1440,400 L0,400 Z"
          opacity="0.9"
        >
          <animate
            attributeName="d"
            dur="10s"
            repeatCount="indefinite"
            values="
              M0,280 C240,220 480,220 720,280 C960,340 1200,340 1440,280 L1440,400 L0,400 Z;
              M0,310 C240,370 480,370 720,310 C960,250 1200,250 1440,310 L1440,400 L0,400 Z;
              M0,280 C240,220 480,220 720,280 C960,340 1200,340 1440,280 L1440,400 L0,400 Z
            "
          />
        </path>
      </svg>
    </div>
  );
};

export default WaveBackground;
