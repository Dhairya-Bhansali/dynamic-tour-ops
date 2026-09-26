"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { Search, MapPin, Compass, Star, DollarSign, Filter } from "lucide-react";
import { fetchDestinations, fetchExperiences } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

export default function DiscoverPage() {
  const [search, setSearch] = useState("");
  const [styleFilter, setStyleFilter] = useState("All");
  const [destinations, setDestinations] = useState<any[]>([]);
  const [experiences, setExperiences] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const styles = ["All", "Adventure", "Luxury", "Culture", "Romantic", "Nature", "Spiritual"];

  useEffect(() => {
    loadData();
  }, [search, styleFilter]);

  async function loadData() {
    setLoading(true);
    try {
      const dests = await fetchDestinations(search, styleFilter);
      const exps = await fetchExperiences(search, styleFilter); // treating category/style similarly for simple filter
      setDestinations(dests);
      setExperiences(exps);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground pb-20">
      {/* Hero Section */}
      <section className="relative h-[60vh] flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-background z-10" />
        <div 
          className="absolute inset-0 bg-cover bg-center z-0 opacity-40 scale-105 transform transition-transform duration-10000"
          style={{ backgroundImage: "url('https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=2021&auto=format&fit=crop')" }}
        />
        <div className="relative z-20 text-center px-6 max-w-4xl mx-auto flex flex-col items-center">
          <Badge className="mb-6 bg-primary/20 text-primary hover:bg-primary/30 border-primary/30">
            Design Your Next Escape
          </Badge>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6">
            Where to <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-400">next?</span>
          </h1>
          
          <div className="w-full max-w-2xl bg-card/60 backdrop-blur-xl border border-white/10 rounded-full p-2 flex items-center shadow-2xl">
            <Search className="w-5 h-5 text-muted-foreground ml-4 mr-2" />
            <input 
              type="text" 
              placeholder="Search destinations, experiences..." 
              className="bg-transparent border-none outline-none flex-1 text-foreground placeholder:text-muted-foreground"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <Button className="rounded-full px-6 bg-primary text-white">Explore</Button>
          </div>
        </div>
      </section>

      {/* Filters */}
      <section className="px-6 py-8 max-w-7xl mx-auto border-b border-white/5 sticky top-16 z-30 bg-background/80 backdrop-blur-lg">
        <div className="flex items-center gap-4 overflow-x-auto pb-2 scrollbar-hide">
          <div className="flex items-center gap-2 text-muted-foreground mr-4">
            <Filter className="w-4 h-4" />
            <span className="text-sm font-medium uppercase tracking-wider">Style</span>
          </div>
          {styles.map(s => (
            <Badge 
              key={s} 
              variant={styleFilter === s ? "default" : "outline"}
              className="cursor-pointer px-4 py-1.5 text-sm rounded-full whitespace-nowrap transition-colors"
              onClick={() => setStyleFilter(s)}
            >
              {s}
            </Badge>
          ))}
        </div>
      </section>

      {/* Destinations Grid */}
      <section className="px-6 py-16 max-w-7xl mx-auto">
        <div className="flex items-end justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold mb-2">Featured Destinations</h2>
            <p className="text-muted-foreground">Handpicked locations for your next journey.</p>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => <Skeleton key={i} className="h-80 rounded-2xl" />)}
          </div>
        ) : destinations.length === 0 ? (
          <div className="h-40 flex items-center justify-center text-muted-foreground border border-white/5 rounded-2xl glass">
            No destinations found matching your criteria.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {destinations.map(dest => (
              <Link href={`/discover/destinations/${dest.id}`} key={dest.id}>
                <Card className="group overflow-hidden rounded-2xl border-white/10 bg-card hover:border-primary/50 transition-all duration-300 h-[400px] relative">
                  <div className="absolute inset-0 z-0">
                    <img src={dest.hero_image} alt={dest.name} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
                    <div className="absolute inset-0 bg-gradient-to-t from-background via-background/60 to-transparent" />
                  </div>
                  <CardContent className="relative z-10 h-full flex flex-col justify-end p-6">
                    <div className="flex items-center gap-2 mb-2">
                      <MapPin className="w-4 h-4 text-primary" />
                      <span className="text-sm font-medium text-white/80">{dest.country}</span>
                    </div>
                    <h3 className="text-3xl font-bold text-white mb-2">{dest.name}</h3>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {dest.travel_styles.map((s: string) => (
                        <span key={s} className="text-xs bg-white/10 backdrop-blur-md px-2 py-1 rounded-md text-white/90">
                          {s}
                        </span>
                      ))}
                    </div>
                    <p className="text-sm text-white/60 line-clamp-2">{dest.description}</p>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Map Abstraction (Demo) */}
      <section className="px-6 py-8 max-w-7xl mx-auto">
        <div className="w-full h-64 rounded-3xl border border-white/10 glass relative overflow-hidden flex flex-col items-center justify-center">
          <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1524661135-423995f22d0b?q=80&w=2074&auto=format&fit=crop')] bg-cover bg-center opacity-20 filter grayscale" />
          <MapPin className="w-12 h-12 text-primary mb-4 relative z-10 animate-bounce" />
          <h3 className="text-2xl font-bold relative z-10">Interactive Discovery Map</h3>
          <p className="text-muted-foreground mt-2 relative z-10">Map provider integration pending production deployment.</p>
          <Button variant="outline" className="mt-4 relative z-10 border-primary/50 text-primary">Enable Map View</Button>
        </div>
      </section>

      {/* Experiences Grid */}
      <section className="px-6 py-16 max-w-7xl mx-auto">
        <div className="flex items-end justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold mb-2">Curated Experiences</h2>
            <p className="text-muted-foreground">Add unforgettable moments to your trip.</p>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-64 rounded-2xl" />)}
          </div>
        ) : experiences.length === 0 ? (
          <div className="h-40 flex items-center justify-center text-muted-foreground border border-white/5 rounded-2xl glass">
            No experiences found matching your criteria.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {experiences.map(exp => (
              <Link href={`/discover/experiences/${exp.id}`} key={exp.id}>
                <Card className="group overflow-hidden rounded-2xl border-white/10 bg-card/50 hover:bg-card transition-all duration-300">
                  <div className="h-48 overflow-hidden relative">
                    <img src={exp.image} alt={exp.name} className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
                    <Badge className="absolute top-3 right-3 bg-background/80 backdrop-blur-md text-foreground border-none">
                      ${exp.price_estimate}
                    </Badge>
                  </div>
                  <CardContent className="p-5">
                    <div className="flex items-center gap-2 mb-2">
                      <Star className="w-3.5 h-3.5 text-primary" />
                      <span className="text-xs font-medium text-primary uppercase tracking-wider">{exp.category}</span>
                    </div>
                    <h3 className="font-semibold text-lg leading-tight mb-2 group-hover:text-primary transition-colors">{exp.name}</h3>
                    <div className="flex items-center text-muted-foreground text-sm gap-4">
                      <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5"/> {exp.location.split(',')[0]}</span>
                      <span className="flex items-center gap-1"><Compass className="w-3.5 h-3.5"/> {exp.duration}h</span>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
