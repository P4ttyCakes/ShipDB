import { Button } from "@/components/ui/button";
import WaveBackground from "@/components/WaveBackground";
import { Database, Sparkles } from "lucide-react";
import sailboat from "@/assets/sailboat.png";
import { useNavigate } from "react-router-dom";

const Index = () => {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen bg-gradient-to-b from-background to-muted overflow-hidden">
      {/* Hero Section */}
      <main className="relative z-10">
        <div className="container mx-auto px-4 pt-32 pb-64 md:pt-48 md:pb-96">
          <div className="flex flex-col items-center text-center max-w-3xl mx-auto animate-fade-in">
            {/* Logo/Icon */}
            <div className="mb-16 relative">
              <div className="absolute inset-0 bg-primary/30 blur-3xl rounded-full animate-pulse"></div>
              <div className="relative bg-gradient-to-br from-primary to-accent p-6 rounded-3xl shadow-2xl shadow-primary/20">
                <Database className="w-16 h-16 md:w-20 md:h-20 text-background" />
              </div>
            </div>

            {/* Headline */}
            <h1 className="text-7xl md:text-9xl font-bold mb-4 bg-gradient-to-r from-foreground via-primary to-accent bg-clip-text text-transparent leading-tight tracking-tight">
              ShipDB
            </h1>
            
            {/* Tagline */}
            <p className="text-lg md:text-xl text-muted-foreground mb-16 font-light tracking-wide">
              build your database
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-6">
              <Button 
                size="lg"
                onClick={() => navigate("/chat")}
                className="bg-gradient-to-r from-primary to-accent hover:opacity-90 transition-all text-xl px-12 py-8 shadow-2xl shadow-primary/30 hover:shadow-primary/40 hover:scale-105 duration-300"
              >
                <Sparkles className="mr-3 h-6 w-6" />
                Get Started
              </Button>
            </div>
          </div>
        </div>
      </main>

      {/* Sailboat floating on waves */}
      <div className="absolute bottom-[15%] md:bottom-[20%] left-[10%] z-20 animate-float">
        <img 
          src={sailboat} 
          alt="Sailboat" 
          className="w-24 h-24 md:w-32 md:h-32 lg:w-40 lg:h-40 opacity-60 hover:opacity-80 transition-opacity duration-500"
        />
      </div>

      {/* Wave Background - Fixed at bottom */}
      <WaveBackground />
    </div>
  );
};

export default Index;
