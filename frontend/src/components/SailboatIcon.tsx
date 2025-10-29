const SailboatIcon = ({ className = "w-32 h-32" }: { className?: string }) => {
  return (
    <svg 
      className={className}
      xmlns="http://www.w3.org/2000/svg" 
      viewBox="0 0 100 100"
      fill="none"
    >
      
      
      {/* Water/Waves */}
      <path
        d="M 20 65 Q 30 60, 50 62 Q 70 60, 80 65"
        stroke="currentColor"
        strokeWidth="1.5"
        fill="none"
        className="text-primary/30"
      />
      <path
        d="M 18 68 Q 28 63, 48 65 Q 68 63, 82 68"
        stroke="currentColor"
        strokeWidth="1.5"
        fill="none"
        className="text-primary/30"
      />
      
      {/* Hull */}
      <path
        d="M 25 65 Q 35 68, 50 69 Q 65 68, 75 65 L 75 70 Q 65 72, 50 73 Q 35 72, 25 70 Z"
        fill="currentColor"
        className="text-primary"
      />
      
      {/* Mast */}
      <line
        x1="50"
        y1="65"
        x2="50"
        y2="35"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        className="text-primary"
      />
      
      {/* Foresail (Jib) */}
      <path
        d="M 50 35 L 50 60 L 30 60 Z"
        fill="currentColor"
        className="text-primary"
      />
      
      {/* Mainsail */}
      <path
        d="M 50 35 Q 52 40, 48 40 Q 50 45, 50 60 L 65 60 L 50 35 Z"
        fill="currentColor"
        className="text-primary"
      />
    </svg>
  );
};

export default SailboatIcon;

