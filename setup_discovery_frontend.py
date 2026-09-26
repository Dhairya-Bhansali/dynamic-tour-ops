import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# 1. API Client
create_file("frontend/src/lib/api.ts", """
const API_BASE = "http://localhost:8000/api/v1";

export async function fetchDestinations(search?: string, style?: string) {
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (style && style !== 'All') params.append("style", style);
  
  const res = await fetch(`${API_BASE}/destinations?${params.toString()}`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch destinations");
  return res.json();
}

export async function fetchDestination(id: string) {
  const res = await fetch(`${API_BASE}/destinations/${id}`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch destination");
  return res.json();
}

export async function fetchExperiences(search?: string, category?: string, destId?: string) {
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (category && category !== 'All') params.append("category", category);
  if (destId) params.append("dest_id", destId);

  const res = await fetch(`${API_BASE}/experiences?${params.toString()}`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch experiences");
  return res.json();
}

export async function fetchExperience(id: string) {
  const res = await fetch(`${API_BASE}/experiences/${id}`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch experience");
  return res.json();
}
""")

# 2. Zustand Store
create_file("frontend/src/store/useTripStore.ts", """
import { create } from 'zustand';

interface TripState {
  selectedDestination: any | null;
  selectedExperiences: any[];
  setDestination: (dest: any) => void;
  addExperience: (exp: any) => void;
  removeExperience: (expId: number) => void;
  clearSelection: () => void;
}

export const useTripStore = create<TripState>((set) => ({
  selectedDestination: null,
  selectedExperiences: [],
  setDestination: (dest) => set({ selectedDestination: dest }),
  addExperience: (exp) => set((state) => ({ 
    selectedExperiences: state.selectedExperiences.some(e => e.id === exp.id) 
      ? state.selectedExperiences 
      : [...state.selectedExperiences, exp] 
  })),
  removeExperience: (expId) => set((state) => ({
    selectedExperiences: state.selectedExperiences.filter(e => e.id !== expId)
  })),
  clearSelection: () => set({ selectedDestination: null, selectedExperiences: [] })
}));
""")

# 3. Main Discover Page (Client Component)
create_file("frontend/src/app/(traveler)/discover/page.tsx", """
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
""")

# 4. Destination Detail Page
create_file("frontend/src/app/(traveler)/discover/destinations/[id]/page.tsx", """
"use client";
import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { fetchDestination, fetchExperiences } from "@/lib/api";
import { useTripStore } from "@/store/useTripStore";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowLeft, MapPin, Calendar, DollarSign, Check, Plus } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

export default function DestinationDetail({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const router = useRouter();
  const [dest, setDest] = useState<any>(null);
  const [exps, setExps] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const { setDestination, addExperience, removeExperience, selectedExperiences, selectedDestination } = useTripStore();

  useEffect(() => {
    async function load() {
      try {
        const d = await fetchDestination(unwrappedParams.id);
        const e = await fetchExperiences(undefined, undefined, unwrappedParams.id);
        setDest(d);
        setExps(e);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [unwrappedParams.id]);

  if (loading) return <div className="p-10"><Skeleton className="w-full h-96 rounded-3xl" /></div>;
  if (!dest) return <div className="p-10 text-center">Destination not found.</div>;

  const isSelected = selectedDestination?.id === dest.id;

  const handleSelectDest = () => {
    setDestination(dest);
    toast.success(`${dest.name} selected for your trip!`);
  };

  const handlePersonalizeHandoff = () => {
    if (!selectedDestination) {
      setDestination(dest);
    }
    // Handoff to personalize module
    toast("Handoff to PERSONALIZE stage...", { description: "Data has been prepared in the global store." });
    // router.push("/personalize"); // Commeneted out until personalize is built
  };

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Hero */}
      <div className="relative h-[50vh] md:h-[70vh] w-full">
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/40 to-black/20 z-10" />
        <img src={dest.hero_image} alt={dest.name} className="w-full h-full object-cover" />
        
        <div className="absolute top-6 left-6 z-20">
          <Button variant="outline" size="icon" className="rounded-full bg-background/20 backdrop-blur-md border-white/10 hover:bg-background/40" onClick={() => router.back()}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
        </div>

        <div className="absolute bottom-0 left-0 w-full z-20 p-6 md:p-12 max-w-7xl mx-auto flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <MapPin className="w-5 h-5 text-primary" />
              <span className="text-lg font-medium text-white/90">{dest.country}</span>
            </div>
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-4">{dest.name}</h1>
            <div className="flex flex-wrap gap-2">
              {dest.travel_styles.map((s: string) => (
                <Badge key={s} variant="outline" className="bg-white/10 border-white/20 backdrop-blur-md px-3 py-1 text-sm">{s}</Badge>
              ))}
            </div>
          </div>
          
          <div className="flex flex-col gap-3 min-w-[200px]">
            {isSelected ? (
              <Button size="lg" className="rounded-full bg-green-600 hover:bg-green-700 text-white shadow-lg shadow-green-900/20" onClick={handlePersonalizeHandoff}>
                <Check className="mr-2 w-5 h-5" /> Destination Selected
              </Button>
            ) : (
              <Button size="lg" className="rounded-full bg-primary hover:bg-primary/90 text-white shadow-lg shadow-primary/20" onClick={handleSelectDest}>
                Build My Trip Here
              </Button>
            )}
            {isSelected && (
               <Button size="lg" variant="outline" className="rounded-full glass" onClick={handlePersonalizeHandoff}>
                 Continue to Personalize 
               </Button>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-12 grid grid-cols-1 lg:grid-cols-3 gap-12">
        <div className="lg:col-span-2 space-y-12">
          {/* Overview */}
          <section>
            <h2 className="text-2xl font-bold mb-4">Overview</h2>
            <p className="text-lg text-muted-foreground leading-relaxed">
              {dest.description}
            </p>
          </section>

          {/* Quick Stats */}
          <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="glass-card bg-card/40 border-white/5">
              <CardContent className="p-6 flex flex-col items-center justify-center text-center">
                <Calendar className="w-6 h-6 text-primary mb-2" />
                <p className="text-sm text-muted-foreground">Duration</p>
                <p className="font-semibold">{dest.recommended_duration} Days</p>
              </CardContent>
            </Card>
            <Card className="glass-card bg-card/40 border-white/5">
              <CardContent className="p-6 flex flex-col items-center justify-center text-center">
                <DollarSign className="w-6 h-6 text-primary mb-2" />
                <p className="text-sm text-muted-foreground">Est. Budget</p>
                <p className="font-semibold">${dest.budget}</p>
              </CardContent>
            </Card>
          </section>

          {/* Experiences */}
          <section>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">Top Experiences in {dest.name}</h2>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {exps.map(exp => {
                const isExpSelected = selectedExperiences.some(e => e.id === exp.id);
                return (
                  <Card key={exp.id} className={`group overflow-hidden rounded-2xl border-white/10 transition-all duration-300 ${isExpSelected ? 'ring-2 ring-primary bg-primary/5' : 'bg-card/50 hover:bg-card'}`}>
                    <div className="h-40 overflow-hidden relative">
                      <img src={exp.image} alt={exp.name} className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
                    </div>
                    <CardContent className="p-5">
                      <h3 className="font-semibold text-lg leading-tight mb-2"><Link href={`/discover/experiences/${exp.id}`} className="hover:text-primary hover:underline">{exp.name}</Link></h3>
                      <div className="flex items-center justify-between mt-4">
                        <span className="font-bold text-primary">${exp.price_estimate}</span>
                        {isExpSelected ? (
                          <Button size="sm" variant="outline" className="border-destructive/50 text-destructive hover:bg-destructive/10" onClick={() => removeExperience(exp.id)}>Remove</Button>
                        ) : (
                          <Button size="sm" onClick={() => {
                            addExperience(exp);
                            toast.success(`Added ${exp.name} to your trip plan!`);
                          }}>
                            <Plus className="w-4 h-4 mr-1" /> Add
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </section>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="sticky top-24">
            <Card className="glass-card border-white/10 shadow-2xl shadow-primary/5">
              <CardContent className="p-6">
                <h3 className="text-xl font-bold mb-4">Your Trip Plan</h3>
                {selectedDestination ? (
                  <div className="mb-6 p-4 rounded-xl bg-background/50 border border-white/5">
                    <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Destination</p>
                    <p className="font-medium flex items-center gap-2"><MapPin className="w-4 h-4 text-primary"/> {selectedDestination.name}</p>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground mb-6">No destination selected yet.</p>
                )}

                <h4 className="font-semibold mb-3">Selected Experiences ({selectedExperiences.length})</h4>
                {selectedExperiences.length > 0 ? (
                  <ul className="space-y-3 mb-6">
                    {selectedExperiences.map(e => (
                      <li key={e.id} className="text-sm flex justify-between items-center bg-white/5 p-2 rounded-md">
                        <span className="truncate pr-2">{e.name}</span>
                        <span className="font-mono text-primary">${e.price_estimate}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-muted-foreground mb-6">Explore experiences and add them to your trip.</p>
                )}

                <div className="border-t border-white/10 pt-4 mb-6">
                  <div className="flex justify-between items-center">
                    <span className="font-medium">Total Estimate</span>
                    <span className="text-xl font-bold">
                      ${(selectedDestination?.budget || 0) + selectedExperiences.reduce((acc, curr) => acc + curr.price_estimate, 0)}
                    </span>
                  </div>
                </div>

                <Button className="w-full h-12 text-base rounded-full shadow-[0_0_20px_rgba(168,85,247,0.3)]" disabled={!selectedDestination} onClick={handlePersonalizeHandoff}>
                  Personalize Trip
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
""")

# 5. Experience Detail Page
create_file("frontend/src/app/(traveler)/discover/experiences/[id]/page.tsx", """
"use client";
import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { fetchExperience } from "@/lib/api";
import { useTripStore } from "@/store/useTripStore";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeft, MapPin, Clock, DollarSign, Plus, Check } from "lucide-react";
import { toast } from "sonner";

export default function ExperienceDetail({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const router = useRouter();
  const [exp, setExp] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  const { addExperience, removeExperience, selectedExperiences } = useTripStore();

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchExperience(unwrappedParams.id);
        setExp(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [unwrappedParams.id]);

  if (loading) return <div className="p-10"><Skeleton className="w-full h-96 rounded-3xl" /></div>;
  if (!exp) return <div className="p-10 text-center">Experience not found.</div>;

  const isSelected = selectedExperiences.some(e => e.id === exp.id);

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-5xl mx-auto px-6 py-12">
        <Button variant="ghost" className="mb-6 -ml-4 text-muted-foreground hover:text-foreground" onClick={() => router.back()}>
          <ArrowLeft className="w-4 h-4 mr-2" /> Back
        </Button>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          {/* Image */}
          <div className="rounded-3xl overflow-hidden border border-white/10 h-[500px]">
            <img src={exp.image} alt={exp.name} className="w-full h-full object-cover" />
          </div>

          {/* Content */}
          <div className="flex flex-col justify-center">
            <div className="inline-block px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4 w-fit border border-primary/20">
              {exp.category}
            </div>
            
            <h1 className="text-4xl font-bold mb-4 leading-tight">{exp.name}</h1>
            
            <div className="flex flex-col gap-3 mb-8 text-muted-foreground">
              <div className="flex items-center gap-3">
                <MapPin className="w-5 h-5 text-primary/70" />
                <span>{exp.location}</span>
              </div>
              <div className="flex items-center gap-3">
                <Clock className="w-5 h-5 text-primary/70" />
                <span>{exp.duration} hours</span>
              </div>
              <div className="flex items-center gap-3">
                <DollarSign className="w-5 h-5 text-primary/70" />
                <span className="font-semibold text-foreground text-xl">${exp.price_estimate}</span>
              </div>
            </div>

            <p className="text-lg leading-relaxed text-foreground/80 mb-10">
              {exp.description}
            </p>

            {isSelected ? (
              <Button size="lg" variant="outline" className="w-full md:w-auto h-14 rounded-xl border-destructive/50 text-destructive hover:bg-destructive/10" onClick={() => {
                removeExperience(exp.id);
                toast("Removed from your trip plan.");
              }}>
                Remove from Trip
              </Button>
            ) : (
              <Button size="lg" className="w-full md:w-auto h-14 rounded-xl shadow-[0_0_20px_rgba(168,85,247,0.25)]" onClick={() => {
                addExperience(exp);
                toast.success("Added to your trip plan!");
              }}>
                <Plus className="w-5 h-5 mr-2" /> Add to My Trip
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
""")
