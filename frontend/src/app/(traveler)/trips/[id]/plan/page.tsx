"use client";
import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { generateItinerary, fetchActiveItinerary, fetchTripPreferences, fetchItineraryExplanation, optimizeBudget, applyOptimizedScenario, fetchDisruptions, simulateDisruption, analyzeDisruption, fetchDisruptionAlternatives, approveAlternative, rejectDisruption, getCostExplanation } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Sparkles, Calendar, Clock, MapPin, DollarSign, Activity, AlertCircle, RefreshCw, CheckCircle2, ArrowRight, Info, Target, ShieldCheck, Zap, AlertTriangle, TrendingDown, Database } from "lucide-react";
import { toast } from "sonner";
import { useTripStore } from "@/store/useTripStore";
import dayjs from "dayjs";

export default function PlanPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const router = useRouter();
  const tripId = parseInt(unwrappedParams.id);
  const { selectedDestination } = useTripStore();
  
  const [itinerary, setItinerary] = useState<any>(null);
  const [explanation, setExplanation] = useState<any>(null);
  const [costExpl, setCostExpl] = useState<any>(null);
  const [prefs, setPrefs] = useState<any>(null);
  const [validation, setValidation] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [genStep, setGenStep] = useState(0);
  
  const [selectedItemExplanation, setSelectedItemExplanation] = useState<any>(null);
  
  // Optimizer state
  const [optimizerOpen, setOptimizerOpen] = useState(false);
  const [targetBudget, setTargetBudget] = useState(5000);
  const [optPriority, setOptPriority] = useState("balanced");
  const [optimizing, setOptimizing] = useState(false);

  const formatCurrency = (val: number, currency = "INR") => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
      maximumFractionDigits: 0
    }).format(val);
  };

  const [optScenarios, setOptScenarios] = useState<any>(null);
  const [applyingScenario, setApplyingScenario] = useState(false);
  
  // Disruption state
  const [disruptions, setDisruptions] = useState<any[]>([]);
  const [activeDisruption, setActiveDisruption] = useState<any>(null);
  const [disruptionAlts, setDisruptionAlts] = useState<any[]>([]);
  const [analyzingDisruption, setAnalyzingDisruption] = useState(false);

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
        const expl = await fetchItineraryExplanation(tripId);
        setExplanation(expl);
        setTargetBudget(tripPrefs.preferences?.budget || 5000);
        
        try {
          const ce = await getCostExplanation(tripId);
          setCostExpl(ce);
        } catch(e) {}
      }
      
      const drs = await fetchDisruptions(tripId);
      setDisruptions(drs.filter((d: any) => d.status === "DETECTED" || d.status === "ALTERNATIVES_READY"));
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
    setExplanation(null);
    
    for (let i = 0; i < genSteps.length; i++) {
      setGenStep(i);
      await new Promise(r => setTimeout(r, 1000));
    }
    
    try {
      const result = await generateItinerary(tripId);
      setItinerary(result.itinerary);
      setValidation(result.validation);
      
      const expl = await fetchItineraryExplanation(tripId);
      setExplanation(expl);
      
      toast.success("Itinerary generated successfully!");
    } catch (err) {
      console.error(err);
      toast.error("Failed to generate itinerary");
    } finally {
      setGenerating(false);
    }
  };

  const getBadgeColor = (method: string) => {
     if (method === "AI GENERATED") return "bg-green-500/10 text-green-500 border-green-500/20";
     if (method === "DEMO FALLBACK") return "bg-primary/10 text-primary border-primary/20";
     return "bg-secondary/10 text-secondary border-secondary/20";
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
              <Badge variant="outline" className={`mb-4 ${getBadgeColor(itinerary?.generation_method)}`}>
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
                <>
                  <Button variant="default" onClick={() => setOptimizerOpen(true)} className="rounded-full shadow-lg shadow-primary/20">
                    <Zap className="w-4 h-4 mr-2" />
                    Optimize Budget
                  </Button>
                  <Button variant="outline" onClick={handleGenerate} disabled={generating} className="glass-card">
                    <RefreshCw className={`w-4 h-4 mr-2 ${generating ? 'animate-spin' : ''}`} />
                    Regenerate Version
                  </Button>
                  <Button variant="outline" onClick={async () => {
                     try {
                        await simulateDisruption(tripId, "PRICE_CHANGE");
                        toast.error("Simulated Disruption Triggered");
                        loadData();
                     } catch(e) {}
                  }} className="glass-card border-destructive/50 text-destructive hover:bg-destructive hover:text-white">
                    <AlertTriangle className="w-4 h-4 mr-2" />
                    Simulate Disruption
                  </Button>
                </>
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

        {itinerary && !generating && disruptions.length > 0 && (
          <div className="mb-8">
             {disruptions.map((d: any) => (
                <Card key={d.id} className="border-destructive/50 bg-destructive/5 overflow-hidden">
                   <div className="bg-destructive/10 px-6 py-3 flex items-center justify-between border-b border-destructive/20">
                      <div className="flex items-center gap-2 text-destructive font-bold">
                         <AlertTriangle className="w-5 h-5" />
                         TRIP UPDATE
                      </div>
                      <Badge variant="destructive">{d.severity} IMPACT</Badge>
                   </div>
                   <CardContent className="p-6">
                      <div className="flex justify-between items-start">
                         <div>
                            <h3 className="text-xl font-bold mb-2">{d.title}</h3>
                            <p className="text-muted-foreground mb-4">{d.description}</p>
                            
                            <div className="grid grid-cols-2 gap-4 mb-4 text-sm bg-black/40 p-4 rounded-xl border border-white/5">
                               <div><div className="text-muted-foreground uppercase text-xs mb-1">Previous</div><div className="font-bold line-through">{d.previous_value}</div></div>
                               <div><div className="text-muted-foreground uppercase text-xs mb-1">Current</div><div className="font-bold text-destructive">{d.current_value}</div></div>
                            </div>
                         </div>
                         
                         <div className="flex flex-col gap-2 w-48 shrink-0">
                            <Button 
                               onClick={async () => {
                                  setActiveDisruption(d);
                                  if (d.status === "DETECTED") {
                                     setAnalyzingDisruption(true);
                                     await analyzeDisruption(d.id);
                                     const alts = await fetchDisruptionAlternatives(d.id);
                                     setDisruptionAlts(alts);
                                     setAnalyzingDisruption(false);
                                  } else {
                                     const alts = await fetchDisruptionAlternatives(d.id);
                                     setDisruptionAlts(alts);
                                  }
                               }}
                               className="w-full bg-destructive text-destructive-foreground hover:bg-destructive/90"
                            >
                               View Alternatives
                            </Button>
                            <Button variant="outline" className="w-full" onClick={async () => {
                               await rejectDisruption(d.id);
                               toast.success("Disruption dismissed");
                               loadData();
                            }}>
                               Dismiss
                            </Button>
                         </div>
                      </div>
                      
                      <div className="flex justify-between items-center mt-4 text-xs text-muted-foreground uppercase tracking-wider">
                         <span>Source: {d.source}</span>
                         <span>Confidence: {d.confidence}</span>
                      </div>
                   </CardContent>
                </Card>
             ))}
          </div>
        )}

        {itinerary && !generating && (
          <div className="animate-in fade-in slide-in-from-bottom-10 duration-700">
            
            {/* WHY THIS TRIP Section */}
            {explanation && (
              <Card className="glass-card mb-12 border-primary/20 overflow-hidden">
                <CardHeader className="bg-primary/5 border-b border-white/5">
                  <div className="flex items-center gap-3">
                    <Target className="w-6 h-6 text-primary" />
                    <h2 className="text-2xl font-bold">Why this trip?</h2>
                  </div>
                  <p className="text-muted-foreground">This itinerary prioritizes your strongest stated preferences while keeping the schedule within your selected duration and target budget.</p>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                       <div className="text-4xl font-bold text-primary mb-2">{explanation.overall_match}% <span className="text-lg text-muted-foreground font-normal">Overall Preference Match</span></div>
                       <p className="text-sm text-muted-foreground mb-6">An optimized match based on your Travel DNA and selected interests.</p>
                    </div>
                    <div className="space-y-4 border-l border-white/10 pl-8">
                       {Object.entries(explanation.dna_alignment || {}).map(([key, val]: any) => (
                         <div key={key}>
                           <div className="flex justify-between text-sm mb-1.5 font-medium">
                             <span>{key}</span>
                             <span className="text-primary">{val}%</span>
                           </div>
                           <div className="w-full bg-black/40 h-2 rounded-full overflow-hidden">
                             <div className="h-full bg-primary" style={{ width: `${val}%` }} />
                           </div>
                         </div>
                       ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* COST EXPLANATION SECTION */}
            {costExpl && (
              <Card className="glass-card mb-12 border-primary/20 overflow-hidden">
                <CardHeader className="bg-primary/5 border-b border-white/5">
                  <div className="flex items-center gap-3">
                    <DollarSign className="w-6 h-6 text-primary" />
                    <h2 className="text-2xl font-bold">Cost Intelligence</h2>
                  </div>
                  <p className="text-muted-foreground">Transparent deterministic breakdown of your trip costs and optimization history.</p>
                </CardHeader>
                <CardContent className="p-6">
                  
                  {/* Budget Position */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    <div className="bg-black/30 p-4 rounded-xl border border-white/5">
                      <div className="text-xs text-muted-foreground uppercase mb-1">Target Budget</div>
                      <div className="text-2xl font-bold">{formatCurrency(costExpl.target_budget, costExpl.currency || "INR")}</div>
                    </div>
                    <div className="bg-black/30 p-4 rounded-xl border border-white/5">
                      <div className="text-xs text-muted-foreground uppercase mb-1">Current Cost</div>
                      <div className="text-2xl font-bold">{formatCurrency(costExpl.current_total, costExpl.currency || "INR")}</div>
                    </div>
                    <div className="bg-black/30 p-4 rounded-xl border border-white/5">
                      <div className="text-xs text-muted-foreground uppercase mb-1">Optimized Cost</div>
                      <div className="text-2xl font-bold text-green-400">{formatCurrency(costExpl.optimized_total, costExpl.currency || "INR")}</div>
                    </div>
                    <div className="bg-black/30 p-4 rounded-xl border border-white/5">
                      <div className="text-xs text-muted-foreground uppercase mb-1">Savings Achieved</div>
                      <div className="text-2xl font-bold text-primary">{formatCurrency(costExpl.savings, costExpl.currency || "INR")}</div>
                    </div>
                  </div>

                  {/* Cost of Inaction / Optimization Path */}
                  {costExpl.optimization_strategy !== "NONE" && (
                    <div className="mb-8 p-6 bg-black/40 rounded-xl border border-white/5">
                      <h3 className="font-bold text-lg mb-4 flex items-center gap-2"><TrendingDown className="w-5 h-5 text-primary"/> Cost Waterfall</h3>
                      <div className="flex items-center justify-between text-center relative">
                        <div className="absolute top-1/2 left-0 w-full h-px bg-white/10 -z-10" />
                        <div className="bg-background px-4">
                          <div className="text-sm text-muted-foreground mb-1">Original Trip</div>
                          <div className="font-bold text-xl">{formatCurrency(costExpl.original_total, costExpl.currency || "INR")}</div>
                        </div>
                        <div className="bg-background px-4">
                          <div className="text-sm text-destructive mb-1">Unmanaged Risk</div>
                          <div className="font-bold text-xl text-destructive">{formatCurrency(costExpl.projected_unmanaged_cost, costExpl.currency || "INR")}</div>
                        </div>
                        <div className="bg-background px-4">
                          <div className="text-sm text-green-400 mb-1">Optimized Alternative</div>
                          <div className="font-bold text-xl text-green-400">{formatCurrency(costExpl.optimized_total, costExpl.currency || "INR")}</div>
                        </div>
                        <div className="bg-background px-4">
                          <div className="text-sm text-primary mb-1">Potential Avoided Cost</div>
                          <div className="font-bold text-xl text-primary">{formatCurrency(costExpl.avoided_cost, costExpl.currency || "INR")}</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Component Breakdown */}
                  {costExpl.components && costExpl.components.length > 0 && (
                    <div>
                      <h3 className="font-bold text-lg mb-4">What changed?</h3>
                      <div className="space-y-3">
                        {costExpl.components.map((c: any, i: number) => (
                          <div key={i} className="flex flex-col md:flex-row md:items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                            <div className="mb-2 md:mb-0">
                              <Badge variant="outline" className="mb-2 bg-white/5">{c.component_type}</Badge>
                              <p className="text-sm">{c.reason}</p>
                              <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                                <span className="flex items-center gap-1"><Database className="w-3 h-3" /> {c.source}</span>
                                <span>{c.freshness}</span>
                              </div>
                            </div>
                            <div className="flex items-center gap-4 text-right">
                              <div>
                                <div className="text-xs text-muted-foreground uppercase">Original</div>
                                <div className="font-semibold line-through opacity-70">{formatCurrency(c.original_cost, costExpl.currency || "INR")}</div>
                              </div>
                              <ArrowRight className="w-4 h-4 text-muted-foreground" />
                              <div>
                                <div className="text-xs text-muted-foreground uppercase">New</div>
                                <div className="font-bold text-green-400">{formatCurrency(c.optimized_cost, costExpl.currency || "INR")}</div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                </CardContent>
              </Card>
            )}

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
              {Array.from({ length: prefs?.duration || 1 }).map((_, i) => {
                const dayNum = i + 1;
                const dayItems = itinerary.items.filter((item: any) => item.day_number === dayNum).sort((a: any, b: any) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());
                
                if (dayItems.length === 0) return null;
                
                const dayDate = dayjs(dayItems[0].day_date).format("dddd, MMM D");
                const dayExpl = explanation?.daily_explanations?.find((d: any) => d.day_number === dayNum);

                return (
                  <div key={dayNum} className="relative">
                    {/* Day Header */}
                    <div className="sticky top-20 z-20 bg-background/90 backdrop-blur-xl pt-6 pb-4 border-b border-white/5 mb-8">
                      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                        <div className="flex items-end gap-4">
                          <h2 className="text-3xl font-bold">Day {dayNum}</h2>
                          <span className="text-muted-foreground font-medium pb-1">{dayDate}</span>
                        </div>
                        
                        {/* Daily Explanation Summary */}
                        {dayExpl && (
                          <div className="flex items-center gap-4 text-sm font-medium bg-white/5 px-4 py-2 rounded-xl border border-white/5">
                            <div className="flex flex-col"><span className="text-[10px] text-muted-foreground uppercase tracking-wider">Theme</span><span>{dayExpl.theme}</span></div>
                            <div className="w-px h-8 bg-white/10" />
                            <div className="flex flex-col"><span className="text-[10px] text-muted-foreground uppercase tracking-wider">Time Eff</span><span className="text-green-400">{dayExpl.time_efficiency}%</span></div>
                            <div className="w-px h-8 bg-white/10" />
                            <div className="flex flex-col"><span className="text-[10px] text-muted-foreground uppercase tracking-wider">Budget Fit</span><span className="text-green-400">{dayExpl.budget_fit}%</span></div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Timeline Line */}
                    <div className="absolute left-6 top-24 bottom-0 w-px bg-white/10" />

                    <div className="space-y-8 pl-14">
                      {dayItems.map((item: any) => {
                        const itemExpl = explanation?.item_explanations?.find((e: any) => e.item_id === item.id);
                        
                        return (
                        <div key={item.id} className="relative group">
                          {/* Timeline Node */}
                          <div className="absolute -left-[39px] top-5 w-4 h-4 rounded-full border-2 border-primary bg-background group-hover:bg-primary transition-colors z-10" />
                          
                          <Card className="glass-card border-white/5 bg-card/40 hover:bg-card/60 transition-colors overflow-hidden relative">
                            {/* Trust Badges */}
                            <div className="absolute top-4 right-4 flex gap-2">
                               {itemExpl?.is_user_selected && (
                                 <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20 text-[10px] h-5 px-1.5"><CheckCircle2 className="w-3 h-3 mr-1"/> SELECTED BY YOU</Badge>
                               )}
                               <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20 text-[10px] h-5 px-1.5"><ShieldCheck className="w-3 h-3 mr-1"/> VERIFIED SCHEDULE</Badge>
                            </div>

                            <CardContent className="p-0">
                              <div className="flex flex-col md:flex-row">
                                {/* Time Block */}
                                <div className="p-5 md:w-48 shrink-0 border-b md:border-b-0 md:border-r border-white/5 bg-white/[0.02]">
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
                                <div className="p-5 md:p-6 flex-1 flex flex-col justify-center">
                                  <h3 className="text-xl font-bold text-white mb-2 pr-20">{item.description}</h3>
                                  
                                  <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mb-4">
                                    <span className="flex items-center gap-1.5"><MapPin className="w-4 h-4 text-primary/70"/> {item.location}</span>
                                    <span className="flex items-center gap-1.5"><DollarSign className="w-4 h-4 text-primary/70"/> {formatCurrency(item.estimated_cost, "INR")}</span>
                                  </div>
                                  
                                  {/* Explanation Trigger */}
                                  <Button 
                                    variant="outline" 
                                    size="sm" 
                                    className="w-fit text-primary border-primary/20 hover:bg-primary/10 rounded-full"
                                    onClick={() => setSelectedItemExplanation({ item, expl: itemExpl })}
                                  >
                                    <Info className="w-4 h-4 mr-2" /> Why this?
                                  </Button>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        </div>
                      )})}
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* End of Itinerary Action */}
            <div className="mt-20 text-center border-t border-white/10 pt-12 pb-6">
              <h3 className="text-2xl font-bold mb-6">Itinerary finalized. What's next?</h3>
              <Button size="lg" onClick={() => router.push(`/trips/${tripId}/book`)} className="rounded-full h-14 px-8 text-lg font-medium shadow-[0_0_30px_rgba(168,85,247,0.3)]">
                Review & Book <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </div>
          </div>
        )}
      </main>

      {/* Explanation Modal */}
      <Dialog open={!!selectedItemExplanation} onOpenChange={(open) => !open && setSelectedItemExplanation(null)}>
        <DialogContent className="sm:max-w-[500px] bg-background/95 backdrop-blur-xl border-white/10 p-0 overflow-hidden">
           {selectedItemExplanation && (
             <>
               <div className="bg-primary/10 p-6 border-b border-white/10 flex items-center justify-between">
                 <DialogTitle className="text-2xl font-bold flex items-center gap-3">
                   <Info className="w-6 h-6 text-primary" />
                   Why this?
                 </DialogTitle>
                 <div className="text-right">
                   <div className="text-3xl font-bold text-primary">{selectedItemExplanation.expl?.overall_match_score || 80}%</div>
                   <div className="text-[10px] text-muted-foreground uppercase tracking-widest font-medium">Preference Match</div>
                 </div>
               </div>
               
               <div className="p-6 space-y-8 max-h-[70vh] overflow-y-auto">
                 <div>
                   <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">Preference Evidence</h4>
                   <div className="space-y-4">
                     {selectedItemExplanation.expl?.reasons?.map((r: any, idx: number) => (
                       <div key={idx} className="flex gap-4">
                          <div className="w-12 text-right font-bold text-primary shrink-0">{r.score * 100}%</div>
                          <div>
                            <div className="font-medium">{r.label}</div>
                            <div className="text-sm text-muted-foreground">{r.explanation}</div>
                          </div>
                       </div>
                     ))}
                   </div>
                 </div>

                 <div className="grid grid-cols-2 gap-4 border-t border-white/10 pt-6">
                   <div>
                     <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2"><Sparkles className="w-4 h-4 text-primary"/> AI Reasoning</h4>
                     <p className="text-sm italic text-white/90">"{selectedItemExplanation.item.ai_reasoning}"</p>
                   </div>
                   <div className="border-l border-white/10 pl-4">
                     <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-green-500"/> Verified Facts</h4>
                     <ul className="space-y-1">
                       {selectedItemExplanation.expl?.verified_facts?.map((f: string, i: number) => (
                         <li key={i} className="text-xs flex items-start gap-2">
                           <CheckCircle2 className="w-3 h-3 text-green-500 shrink-0 mt-0.5" />
                           <span className="text-white/80">{f}</span>
                         </li>
                       ))}
                     </ul>
                   </div>
                 </div>

                 <div className="border-t border-white/10 pt-6">
                   <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">What would change this?</h4>
                   <p className="text-sm text-muted-foreground">
                     This activity may be dynamically replaced if:
                   </p>
                   <ul className="list-disc list-inside text-sm text-muted-foreground mt-2 opacity-80">
                     <li>your budget decreases</li>
                     <li>the activity becomes unavailable</li>
                     <li>a schedule conflict is introduced</li>
                   </ul>
                 </div>
               </div>
             </>
           )}
        </DialogContent>
      </Dialog>

      {/* Budget Optimizer Modal */}
      <Dialog open={optimizerOpen} onOpenChange={(open) => { setOptimizerOpen(open); if(!open) setOptScenarios(null); }}>
        <DialogContent className="sm:max-w-[800px] bg-background/95 backdrop-blur-xl border-white/10 p-0 overflow-hidden">
          <div className="bg-primary/10 p-6 border-b border-white/10">
             <DialogTitle className="text-2xl font-bold flex items-center gap-3">
               <Zap className="w-6 h-6 text-primary" />
               Cost Optimization Engine
             </DialogTitle>
             <p className="text-sm text-muted-foreground mt-2">Adjust your budget to automatically generate feasible configurations based on live backend data.</p>
          </div>
          
          <div className="p-6 max-h-[75vh] overflow-y-auto">
            {!optScenarios && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2">Target Budget (USD)</label>
                  <input 
                    type="number" 
                    className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-primary/50 text-lg font-medium"
                    value={targetBudget}
                    onChange={e => setTargetBudget(parseInt(e.target.value) || 0)}
                  />
                </div>
                
                <Button 
                  size="lg" 
                  className="w-full h-12 text-lg rounded-full" 
                  onClick={async () => {
                     setOptimizing(true);
                     try {
                       const res = await optimizeBudget(tripId, { target_budget: targetBudget });
                       setOptScenarios(res);
                     } catch(err) {
                       toast.error("Failed to generate scenarios");
                     } finally {
                       setOptimizing(false);
                     }
                  }}
                  disabled={optimizing}
                >
                  {optimizing ? "Running Deterministic Optimizer..." : "Find Optimized Plans"} <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            )}
            
            {optScenarios && (
              <div className="space-y-8 animate-in fade-in duration-500">
                <div className="flex flex-col gap-4 px-4 py-4 bg-white/5 rounded-xl border border-white/10">
                  <div className="flex justify-between items-center">
                     <div>
                       <div className="text-xs text-muted-foreground uppercase">Current Trip Cost</div>
                       <div className="font-bold text-xl">${optScenarios.current_cost}</div>
                     </div>
                     <ArrowRight className="w-5 h-5 text-muted-foreground" />
                     <div className="text-right">
                       <div className="text-xs text-primary uppercase font-bold">Target Budget</div>
                       <div className="font-bold text-xl text-primary">${optScenarios.target_budget}</div>
                     </div>
                  </div>
                  
                  {/* Cost Breakdown */}
                  <div className="border-t border-white/10 pt-4 mt-2">
                    <div className="text-xs text-muted-foreground uppercase mb-2">Current Cost Breakdown</div>
                    <div className="flex flex-wrap gap-3">
                      {Object.entries(optScenarios.breakdown || {}).map(([cat, val]: any) => (
                         val > 0 && <Badge key={cat} variant="secondary">{cat}: ${val}</Badge>
                      ))}
                    </div>
                  </div>
                </div>
                
                <div className="space-y-6">
                  {optScenarios.scenarios.map((scen: any) => (
                    <Card key={scen.scenario_id} className="glass-card border-white/10 bg-card/60 overflow-hidden">
                      <CardContent className="p-0">
                        <div className="p-6 border-b border-white/5 flex justify-between items-start">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <h3 className="font-bold text-primary text-lg">{scen.name}</h3>
                              <Badge variant={scen.feasibility === "UNDER BUDGET" ? "default" : "destructive"}>
                                {scen.feasibility}
                              </Badge>
                            </div>
                            <div className="text-3xl font-bold">${scen.optimized_cost}</div>
                            {scen.savings > 0 && (
                               <div className="text-sm text-green-400 font-medium">Save ${scen.savings} ({scen.savings_percentage.toFixed(1)}%)</div>
                            )}
                          </div>
                          <Button 
                            variant="secondary"
                            disabled={applyingScenario}
                            onClick={async () => {
                               setApplyingScenario(true);
                               try {
                                 await applyOptimizedScenario(tripId, { scenario_items: scen.items, scenario_id: scen.scenario_id });
                                 toast.success("Scenario applied! New itinerary version created.");
                                 setOptimizerOpen(false);
                                 setOptScenarios(null);
                                 loadData();
                               } catch (err) {
                                 toast.error("Failed to apply scenario");
                               } finally {
                                 setApplyingScenario(false);
                               }
                            }}
                          >
                            {applyingScenario ? "Applying..." : "Apply Version"}
                          </Button>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 p-6 border-b border-white/5 bg-black/20">
                           <div><div className="text-xs uppercase text-muted-foreground">Preference Match</div><div className="font-bold text-lg">{scen.preference_score}%</div></div>
                           <div><div className="text-xs uppercase text-muted-foreground">Budget Fit</div><div className="font-bold text-lg">{scen.budget_fit}%</div></div>
                        </div>
                        
                        <div className="p-6 space-y-4">
                           <div className="text-sm font-semibold mb-2">Why did the price change?</div>
                           
                           {scen.changed_components?.length === 0 ? (
                             <p className="text-sm text-muted-foreground">No components were changed in this scenario.</p>
                           ) : (
                             scen.changed_components?.map((diff: any, idx: number) => (
                               <div key={idx} className="bg-black/40 p-4 rounded-xl border border-white/5">
                                 <div className="flex justify-between items-start mb-2">
                                   <div className="font-medium flex items-center gap-2">
                                     <Badge variant="outline">{diff.component_type}</Badge>
                                     <span className="text-sm">Cost Reduced by ${diff.savings}</span>
                                   </div>
                                 </div>
                                 <div className="grid grid-cols-2 gap-2 text-sm mb-3">
                                   <div><span className="text-muted-foreground">Old:</span> <span className="line-through">${diff.original_cost}</span></div>
                                   <div><span className="text-muted-foreground">New:</span> <span className="text-green-400 font-bold">${diff.optimized_cost}</span></div>
                                 </div>
                                 <div className="text-xs text-muted-foreground italic border-l-2 border-primary/50 pl-3 py-1 mb-3">
                                   {diff.reason}
                                 </div>
                                 <div className="flex items-center justify-between text-[10px] uppercase tracking-wider text-muted-foreground">
                                   <span>Source: {diff.source}</span>
                                   <span>Freshness: {diff.freshness}</span>
                                 </div>
                               </div>
                             ))
                           )}
                           
                           <div className="text-xs text-muted-foreground pt-2 flex items-center justify-between">
                             <span>Data Sources: {scen.data_sources.join(", ")}</span>
                           </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
      
      {/* Disruption Alternatives Modal */}
      <Dialog open={!!activeDisruption} onOpenChange={(open) => { if(!open) { setActiveDisruption(null); setDisruptionAlts([]); } }}>
        <DialogContent className="sm:max-w-[800px] bg-background/95 backdrop-blur-xl border-white/10 p-0 overflow-hidden">
           <div className="bg-destructive/10 p-6 border-b border-destructive/20">
              <DialogTitle className="text-2xl font-bold flex items-center gap-3 text-destructive">
                <AlertTriangle className="w-6 h-6" />
                Review Alternatives
              </DialogTitle>
              <p className="text-sm text-muted-foreground mt-2">Your trip requires attention. Please select an optimized alternative to resolve the disruption.</p>
           </div>
           
           <div className="p-6 max-h-[75vh] overflow-y-auto">
              {analyzingDisruption ? (
                 <div className="py-20 text-center">
                    <RefreshCw className="w-10 h-10 text-destructive animate-spin mx-auto mb-4" />
                    <p className="font-medium text-lg">Analyzing impact and calculating alternatives...</p>
                 </div>
              ) : (
                 <div className="space-y-6">
                    <div className="bg-white/5 p-4 rounded-xl border border-white/10">
                       <h4 className="text-sm font-bold uppercase text-muted-foreground mb-4">Cost of Inaction</h4>
                       <div className="flex justify-between items-center">
                          <div>
                             <div className="text-xs text-muted-foreground">Original Trip Cost</div>
                             <div className="font-bold">${activeDisruption?.impact?.projected_cost - activeDisruption?.impact?.cost_impact}</div>
                          </div>
                          <ArrowRight className="w-4 h-4 text-muted-foreground" />
                          <div>
                             <div className="text-xs text-muted-foreground">Projected Cost (If unchanged)</div>
                             <div className="font-bold text-destructive">${activeDisruption?.impact?.projected_cost}</div>
                          </div>
                          <div className="bg-destructive/20 text-destructive px-3 py-1 rounded-full text-sm font-bold">
                             +${activeDisruption?.impact?.cost_impact}
                          </div>
                       </div>
                    </div>
                    
                    <h3 className="font-bold text-lg">Recommended Alternatives</h3>
                    {disruptionAlts.map((alt: any) => (
                       <Card key={alt.id} className="glass-card border-white/10 overflow-hidden">
                          <CardContent className="p-0">
                             <div className="p-6 border-b border-white/5 flex justify-between items-start">
                                <div>
                                   <Badge variant="outline" className="mb-2 bg-primary/20 text-primary border-primary">Recommended</Badge>
                                   <div className="text-3xl font-bold">
                                      ${activeDisruption?.impact?.projected_cost - alt.cost_difference}
                                   </div>
                                   <div className="text-sm text-green-400 font-medium">
                                      Avoided cost: ${alt.cost_difference}
                                   </div>
                                </div>
                                <Button 
                                   onClick={async () => {
                                      try {
                                         await approveAlternative(activeDisruption.id, alt.id);
                                         toast.success("Alternative approved! Itinerary updated.");
                                         setActiveDisruption(null);
                                         loadData();
                                      } catch(e) {
                                         toast.error("Failed to approve alternative.");
                                      }
                                   }}
                                >
                                   Approve Change
                                </Button>
                             </div>
                             
                             <div className="p-6 space-y-4">
                                <div className="text-sm font-semibold">Changes Applied</div>
                                {alt.changes.map((c: any, idx: number) => (
                                   <div key={idx} className="bg-black/40 p-4 rounded-xl border border-white/5 text-sm">
                                      <div className="flex justify-between items-center mb-2">
                                         <Badge variant="outline">{c.component_type}</Badge>
                                         <span className="text-green-400">Save ${c.savings}</span>
                                      </div>
                                      <div className="text-muted-foreground italic mb-2 border-l-2 border-primary/50 pl-3 py-1">{c.reason}</div>
                                      <div className="flex justify-between text-xs text-muted-foreground uppercase">
                                         <span>Old: <span className="line-through text-white/50">${c.original_cost}</span></span>
                                         <span>New: <span className="text-white">${c.optimized_cost}</span></span>
                                      </div>
                                   </div>
                                ))}
                             </div>
                          </CardContent>
                       </Card>
                    ))}
                 </div>
              )}
           </div>
        </DialogContent>
      </Dialog>
      
    </div>
  );
}
