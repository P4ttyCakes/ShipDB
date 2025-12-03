import { Button } from "@/components/ui/button";
import WaveBackground from "@/components/WaveBackground";
import boatImage from "@/assets/boat.png";
import { Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Index = () => {
  const navigate = useNavigate();

  // Fixed star positions
  const stars = [
    { left: '10%', top: '20%', delay: '0s', duration: '2s', opacity: 0.4 },
    { left: '85%', top: '15%', delay: '0.5s', duration: '2.5s', opacity: 0.5 },
    { left: '15%', top: '35%', delay: '1s', duration: '3s', opacity: 0.3 },
    { left: '90%', top: '25%', delay: '1.5s', duration: '2s', opacity: 0.4 },
    { left: '25%', top: '12%', delay: '0.3s', duration: '2.8s', opacity: 0.5 },
    { left: '70%', top: '18%', delay: '0.8s', duration: '2.2s', opacity: 0.3 },
    { left: '5%', top: '30%', delay: '1.2s', duration: '2.7s', opacity: 0.4 },
    { left: '95%', top: '32%', delay: '0.6s', duration: '2.3s', opacity: 0.5 },
    { left: '45%', top: '10%', delay: '1.4s', duration: '2.6s', opacity: 0.3 },
    { left: '55%', top: '22%', delay: '0.9s', duration: '2.4s', opacity: 0.4 },
    { left: '35%', top: '28%', delay: '1.1s', duration: '2.9s', opacity: 0.5 },
    { left: '75%', top: '30%', delay: '0.4s', duration: '2.1s', opacity: 0.3 },
    { left: '20%', top: '40%', delay: '1.3s', duration: '2.5s', opacity: 0.4 },
    { left: '80%', top: '38%', delay: '0.7s', duration: '2.8s', opacity: 0.5 },
    { left: '50%', top: '16%', delay: '1.6s', duration: '2.2s', opacity: 0.3 },
  ];

  return (
    <div className="relative min-h-screen bg-background overflow-hidden">
      {/* Stars */}
      <div className="absolute inset-0 z-0">
        {stars.map((star, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-white rounded-full animate-pulse"
            style={{
              left: star.left,
              top: star.top,
              animationDelay: star.delay,
              animationDuration: star.duration,
              opacity: star.opacity,
            }}
          />
        ))}
      </div>

      {/* Hero Section */}
      <main className="relative z-10 flex items-center justify-center min-h-screen">
        <div className="container mx-auto px-4 py-20">
          <div className="flex flex-col items-center justify-center text-center max-w-4xl mx-auto">
            {/* Headline */}
            <h1 className="text-6xl md:text-8xl lg:text-9xl font-bold mb-6 text-foreground leading-tight tracking-tight">
              ShipDB
            </h1>
            
            {/* Tagline */}
            <p className="text-xl md:text-2xl text-muted-foreground mb-12 font-light tracking-wide">
              Build your database with AI
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Button 
                size="lg"
                onClick={() => navigate("/chat")}
                className="bg-primary hover:bg-primary/85 shadow-lg text-lg px-8 py-6 transition-all duration-200"
              >
                <Sparkles className="mr-2 h-5 w-5" />
                Get Started
              </Button>
            </div>
          </div>
        </div>
      </main>

      {/* Boat floating on waves */}
      <div className="absolute bottom-[15%] md:bottom-[20%] left-[10%] z-20 animate-float">
        <div 
          className="w-24 h-24 md:w-32 md:h-32 lg:w-40 lg:h-40 opacity-90 hover:opacity-100 transition-opacity duration-500"
          style={{
            backgroundColor: '#4285F4',
            maskImage: `url(${boatImage})`,
            maskSize: 'contain',
            maskRepeat: 'no-repeat',
            maskPosition: 'center',
            WebkitMaskImage: `url(${boatImage})`,
            WebkitMaskSize: 'contain',
            WebkitMaskRepeat: 'no-repeat',
            WebkitMaskPosition: 'center',
          }}
        />
      </div>

      {/* Wave Background - Fixed at bottom */}
      <WaveBackground />
    </div>
  );
};

export default Index;
