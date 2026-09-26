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
