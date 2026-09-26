import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, Globe, Plane, Shield, Map } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      {/* Navbar */}
      <header className="px-6 h-20 flex items-center justify-between border-b border-white/5 glass sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-purple-700 flex items-center justify-center">
            <Globe className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-semibold tracking-tight">NexTour</span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/discover">
            <Button variant="ghost" className="hidden sm:flex text-muted-foreground hover:text-foreground">
              For Travelers
            </Button>
          </Link>
          <Link href="/operator">
            <Button variant="ghost" className="hidden sm:flex text-muted-foreground hover:text-foreground">
              For Operators
            </Button>
          </Link>
          <Link href="/discover">
            <Button className="rounded-full px-6 bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/20">
              Start Planning
            </Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1">
        <section className="relative px-6 py-24 md:py-32 overflow-hidden flex flex-col items-center text-center">
          {/* Background Glow */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/20 blur-[120px] rounded-full pointer-events-none" />
          
          <Badge variant="outline" className="mb-6 py-1.5 px-4 rounded-full border-primary/30 bg-primary/10 text-primary-foreground shadow-[0_0_15px_rgba(168,85,247,0.15)]">
            <span className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
              </span>
              Introducing Dynamic Tour Operations
            </span>
          </Badge>
          
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight max-w-4xl mb-8 leading-tight">
            The Future of <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-400">Personalized Travel</span> is Here.
          </h1>
          
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mb-12">
            Experience end-to-end trip planning with AI-powered itinerary generation, real-time disruption handling, and a seamless operator control tower.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
            <Link href="/discover">
              <Button size="lg" className="rounded-full w-full sm:w-auto px-8 h-14 text-base bg-primary hover:bg-primary/90 shadow-[0_0_30px_rgba(168,85,247,0.3)]">
                I am a Traveler <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
            <Link href="/operator">
              <Button size="lg" variant="outline" className="rounded-full w-full sm:w-auto px-8 h-14 text-base border-white/10 hover:bg-white/5 glass">
                I am an Operator
              </Button>
            </Link>
          </div>
        </section>

        {/* Feature Highlights */}
        <section className="px-6 py-24 bg-card/30 border-t border-white/5 relative">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold mb-4">Complete Tour Lifecycle</h2>
              <p className="text-muted-foreground">From initial discovery to post-trip review, handled in one platform.</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="glass-card border-white/5 bg-background/40">
                <CardContent className="p-8 flex flex-col gap-4">
                  <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                    <Map className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold">AI Trip Personalization</h3>
                  <p className="text-muted-foreground">Tailor-made itineraries based on your unique Travel DNA and preferences.</p>
                </CardContent>
              </Card>
              
              <Card className="glass-card border-white/5 bg-background/40 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-10">
                  <Shield className="w-24 h-24" />
                </div>
                <CardContent className="p-8 flex flex-col gap-4 relative z-10">
                  <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                    <Shield className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold">Dynamic Disruption</h3>
                  <p className="text-muted-foreground">Automated impact analysis and confidence-scored alternatives when things go wrong.</p>
                </CardContent>
              </Card>
              
              <Card className="glass-card border-white/5 bg-background/40">
                <CardContent className="p-8 flex flex-col gap-4">
                  <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                    <Plane className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold">Operator Control Tower</h3>
                  <p className="text-muted-foreground">A mission-control center for managing bookings, vendors, and dynamic itineraries.</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
