"use client";
import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { generateItinerary, fetchActiveItinerary, fetchTripPreferences } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Sparkles, Calendar, Clock, MapPin, DollarSign, Activity, AlertCircle, RefreshCw, CheckCircle2, ArrowRight } from "lucide-react";
import { toast } from "sonner";
import { useTripStore } from "@/store/useTripStore";
import dayjs from "dayjs";

export default function PlanPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const router = useRouter();
  const tripId = parseInt(unwrappedParams.id);
  const { selectedDestination } = useTripStore();
  
  const [itinerary, setItinerary] = useState<any>(null);
  const [prefs, setPrefs] = useState<any>(null);
  const [validation, setValidation] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [genStep, setGenStep] = useState(0);

  const genSteps = [
    "Understanding your preferences...",
    "Finding candidate experiences...",
    "Building itinerary...",
    "Validating schedule constraints...",
    "Checking budget bounds...",
    "Finalizing version..."
  ];

  useEffect(() => {
    loadData();
  }, [tripId]);

  async function loadData() {
    try {
      setLoading(true);
      const tripPrefs = await fetchTripPreferences(tripId);
      setPrefs(tripPrefs.preferences);
      
      const activeItin = await fetchActiveItinerary(tripId);
      if (activeItin) {
        setItinerary(activeItin);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleGenerate = async () => {
    setGenerating(true);
    setItinerary(null);
    setValidation(null);
    
    // Fake the AI stages for UI immersion
    for (let i = 0; i < genSteps.length; i++) {
      setGenStep(i);
      await new Promise(r => setTimeout(r, 1000));
    }
    
    try {
      const result = await generateItinerary(tripId);
      setItinerary(result.itinerary);
      setValidation(result.validation);
      toast.success("Itinerary generated successfully!");
    } catch (err) {
      console.error(err);
      toast.error("Failed to generate itinerary");
    } finally {
      setGenerating(false);
    }
  };

  if (loading) return <div className="p-12 max-w-4xl mx-auto"><Skeleton className="h-64 w-full rounded-3xl" /></div>;

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <header className="relative border-b border-white/10 bg-background/50 backdrop-blur-md z-10 pt-24 pb-8 px-6">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/10 to-transparent pointer-events-none" />
        <div className="max-w-5xl mx-auto relative z-10">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <Badge variant="outline" className={`mb-4 border-primary/20 ${itinerary?.generation_method === "AI GENERATED" ? "bg-green-500/10 text-green-500 border-green-500/20" : "bg-primary/10 text-primary"}`}>
                {itinerary?.generation_method || "AI Planner Engine"}
              </Badge>
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4 text-white">Your Itinerary</h1>
              <div className="flex flex-wrap items-center gap-4 text-muted-foreground">
                <span className="flex items-center gap-1.5"><MapPin className="w-4 h-4"/> {selectedDestination?.name || "Destination"}</span>
                <span className="flex items-center gap-1.5"><Calendar className="w-4 h-4"/> {prefs?.duration || "?"} Days</span>
                <span className="flex items-center gap-1.5"><DollarSign className="w-4 h-4"/> {prefs?.budget || "?"} Budget</span>
              </div>
            </div>
            
            <div className="flex flex-col gap-3">
              {itinerary && (
                <Button variant="outline" onClick={handleGenerate} disabled={generating} className="glass-card">
                  <RefreshCw className={`w-4 h-4 mr-2 ${generating ? 'animate-spin' : ''}`} />
                  Regenerate Version
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 py-12">
        {!itinerary && !generating && (
          <div className="text-center py-20 border border-white/10 rounded-3xl bg-card/30 backdrop-blur-md">
            <div className="w-24 h-24 mx-auto bg-primary/20 rounded-full flex items-center justify-center mb-6">
              <Sparkles className="w-10 h-10 text-primary" />
            </div>
            <h2 className="text-3xl font-bold mb-4">Ready to build your journey?</h2>
            <p className="text-muted-foreground max-w-lg mx-auto mb-8">
              Our AI engine will now synthesize your Travel DNA, selected experiences, and deterministic constraints into an optimized daily plan.
            </p>
            <Button size="lg" onClick={handleGenerate} className="rounded-full shadow-[0_0_30px_rgba(168,85,247,0.3)] h-14 px-8 text-lg">
              <Sparkles className="w-5 h-5 mr-2" /> Generate Itinerary
            </Button>
          </div>
        )}

        {generating && (
          <div className="text-center py-32 border border-white/5 rounded-3xl bg-black/20">
            <div className="relative w-24 h-24 mx-auto mb-8">
              <div className="absolute inset-0 bg-primary/30 rounded-full animate-ping" />
              <div className="relative w-full h-full bg-primary/20 rounded-full border border-primary/50 flex items-center justify-center backdrop-blur-sm">
                <Sparkles className="w-10 h-10 text-primary animate-pulse" />
              </div>
            </div>
            <h3 className="text-2xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-white to-white/50">
              {genSteps[genStep]}
            </h3>
            <div className="w-64 h-2 bg-white/10 rounded-full mx-auto overflow-hidden">
              <div className="h-full bg-primary transition-all duration-1000 ease-in-out" style={{ width: `${((genStep + 1) / genSteps.length) * 100}%` }} />
            </div>
          </div>
        )}

        {itinerary && !generating && (
          <div className="animate-in fade-in slide-in-from-bottom-10 duration-700">
            {/* Validation Banner */}
            {validation && (
              <div className={`mb-10 p-5 rounded-2xl border ${validation.valid ? 'bg-green-500/10 border-green-500/20' : 'bg-destructive/10 border-destructive/20'} flex items-start gap-4`}>
                {validation.valid ? <CheckCircle2 className="w-6 h-6 text-green-500 shrink-0 mt-0.5" /> : <AlertCircle className="w-6 h-6 text-destructive shrink-0 mt-0.5" />}
                <div>
                  <h3 className={`text-lg font-bold ${validation.valid ? 'text-green-500' : 'text-destructive'}`}>
                    {validation.valid ? 'Itinerary Validated' : 'Validation Issues Detected'}
                  </h3>
                  {validation.warnings.length > 0 && (
                    <ul className="mt-2 space-y-1 text-sm text-yellow-500/90 list-disc list-inside">
                      {validation.warnings.map((w: string, i: number) => <li key={i}>{w}</li>)}
                    </ul>
                  )}
                  {validation.errors.length > 0 && (
                    <ul className="mt-2 space-y-1 text-sm text-destructive list-disc list-inside">
                      {validation.errors.map((e: string, i: number) => <li key={i}>{e}</li>)}
                    </ul>
                  )}
                </div>
              </div>
            )}

            {/* Timeline */}
            <div className="space-y-12">
              {/* Group items by day */}
              {Array.from({ length: prefs?.duration || 1 }).map((_, i) => {
                const dayNum = i + 1;
                const dayItems = itinerary.items.filter((item: any) => item.day_number === dayNum).sort((a: any, b: any) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());
                
                if (dayItems.length === 0) return null;
                
                const dayDate = dayjs(dayItems[0].day_date).format("dddd, MMM D");

                return (
                  <div key={dayNum} className="relative">
                    {/* Day Header */}
                    <div className="sticky top-20 z-20 bg-background/90 backdrop-blur-xl py-4 border-b border-white/5 mb-8 flex items-end gap-4">
                      <h2 className="text-3xl font-bold">Day {dayNum}</h2>
                      <span className="text-muted-foreground font-medium pb-1">{dayDate}</span>
                    </div>

                    {/* Timeline Line */}
                    <div className="absolute left-6 top-24 bottom-0 w-px bg-white/10" />

                    <div className="space-y-8 pl-14">
                      {dayItems.map((item: any) => (
                        <div key={item.id} className="relative group">
                          {/* Timeline Node */}
                          <div className="absolute -left-[39px] top-5 w-4 h-4 rounded-full border-2 border-primary bg-background group-hover:bg-primary transition-colors z-10" />
                          
                          <Card className="glass-card border-white/5 bg-card/40 hover:bg-card/60 transition-colors overflow-hidden">
                            <CardContent className="p-0">
                              <div className="flex flex-col sm:flex-row">
                                {/* Time Block */}
                                <div className="p-5 sm:w-48 shrink-0 border-b sm:border-b-0 sm:border-r border-white/5 bg-white/[0.02]">
                                  <div className="font-mono text-xl text-primary font-medium">
                                    {dayjs(item.start_time).format("HH:mm")}
                                  </div>
                                  <div className="text-sm text-muted-foreground mb-3">
                                    to {dayjs(item.end_time).format("HH:mm")}
                                  </div>
                                  <div className="inline-flex items-center gap-1.5 text-xs font-medium px-2 py-1 bg-white/5 rounded-md">
                                    <Activity className="w-3.5 h-3.5" />
                                    {item.activity_type}
                                  </div>
                                </div>
                                
                                {/* Content Block */}
                                <div className="p-5 sm:p-6 flex-1 flex flex-col justify-center">
                                  <h3 className="text-xl font-bold text-white mb-2">{item.description}</h3>
                                  
                                  <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mb-4">
                                    <span className="flex items-center gap-1.5"><MapPin className="w-4 h-4 text-primary/70"/> {item.location}</span>
                                    <span className="flex items-center gap-1.5"><DollarSign className="w-4 h-4 text-primary/70"/> ${item.estimated_cost}</span>
                                    {item.confidence_score && (
                                      <span className="flex items-center gap-1.5 text-green-400/80">
                                        <CheckCircle2 className="w-4 h-4" /> {(item.confidence_score * 100).toFixed(0)}% Match
                                      </span>
                                    )}
                                  </div>
                                  
                                  {item.ai_reasoning && (
                                    <div className="p-3 rounded-lg bg-primary/5 border border-primary/10 text-sm text-primary/90 flex items-start gap-2">
                                      <Sparkles className="w-4 h-4 shrink-0 mt-0.5" />
                                      <p>{item.ai_reasoning}</p>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* End of Itinerary Action */}
            <div className="mt-20 text-center border-t border-white/10 pt-12 pb-6">
              <h3 className="text-2xl font-bold mb-6">Itinerary finalized. What's next?</h3>
              <Button size="lg" className="rounded-full h-14 px-8 text-lg font-medium shadow-[0_0_30px_rgba(168,85,247,0.3)]">
                Proceed to Bookings <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
