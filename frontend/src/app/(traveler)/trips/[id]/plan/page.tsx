"use client";
import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { generateItinerary, fetchActiveItinerary, fetchTripPreferences, fetchItineraryExplanation, optimizeBudget, applyOptimizedScenario } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Sparkles, Calendar, Clock, MapPin, DollarSign, Activity, AlertCircle, RefreshCw, CheckCircle2, ArrowRight, Info, Target, ShieldCheck, Zap } from "lucide-react";
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
  const [optScenarios, setOptScenarios] = useState<any>(null);
  const [applyingScenario, setApplyingScenario] = useState(false);

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
                                    <span className="flex items-center gap-1.5"><DollarSign className="w-4 h-4 text-primary/70"/> ${item.estimated_cost}</span>
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
        <DialogContent className="sm:max-w-[700px] bg-background/95 backdrop-blur-xl border-white/10 p-0 overflow-hidden">
          <div className="bg-primary/10 p-6 border-b border-white/10">
             <DialogTitle className="text-2xl font-bold flex items-center gap-3">
               <Zap className="w-6 h-6 text-primary" />
               Optimize Your Trip
             </DialogTitle>
             <p className="text-sm text-muted-foreground mt-2">Adjust your constraints to find an optimized version of your itinerary.</p>
          </div>
          
          <div className="p-6 max-h-[70vh] overflow-y-auto">
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
                <div>
                  <label className="block text-sm font-medium mb-4">Optimization Priority</label>
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { id: "experience_max", label: "Maximize Experiences" },
                      { id: "preserve_favorites", label: "Preserve Favorites" },
                      { id: "minimal_travel", label: "Minimize Travel" },
                      { id: "balanced", label: "Balanced" }
                    ].map(opt => (
                      <div 
                        key={opt.id}
                        onClick={() => setOptPriority(opt.id)}
                        className={`cursor-pointer p-4 text-center rounded-xl border transition-all text-sm ${optPriority === opt.id ? 'bg-primary/20 border-primary text-primary font-medium' : 'bg-background/50 border-white/10 hover:border-white/30'}`}
                      >
                        {opt.label}
                      </div>
                    ))}
                  </div>
                </div>
                <Button 
                  size="lg" 
                  className="w-full h-12 text-lg rounded-full" 
                  onClick={async () => {
                     setOptimizing(true);
                     try {
                       const res = await optimizeBudget(tripId, { target_budget: targetBudget, optimization_priority: optPriority });
                       setOptScenarios(res);
                     } catch(err) {
                       toast.error("Failed to generate scenarios");
                     } finally {
                       setOptimizing(false);
                     }
                  }}
                  disabled={optimizing}
                >
                  {optimizing ? "Generating Scenarios..." : "Find Optimized Plans"} <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            )}
            
            {optScenarios && (
              <div className="space-y-8 animate-in fade-in duration-500">
                <div className="flex justify-between items-center px-4 py-3 bg-white/5 rounded-xl border border-white/10">
                   <div>
                     <div className="text-xs text-muted-foreground uppercase">Current Estimate</div>
                     <div className="font-bold text-lg">${optScenarios.current_cost}</div>
                   </div>
                   <ArrowRight className="w-5 h-5 text-muted-foreground" />
                   <div className="text-right">
                     <div className="text-xs text-primary uppercase font-bold">Target Budget</div>
                     <div className="font-bold text-lg text-primary">${optScenarios.target_budget}</div>
                   </div>
                </div>
                
                <div className="space-y-6">
                  {optScenarios.scenarios.map((scen: any) => (
                    <Card key={scen.scenario_id} className="glass-card border-white/10 bg-card/60 overflow-hidden">
                      <CardContent className="p-6">
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h3 className="font-bold text-primary mb-1">{scen.name}</h3>
                            <div className="text-2xl font-bold">${scen.total_cost}</div>
                            {optScenarios.current_cost > scen.total_cost && (
                               <div className="text-xs text-green-400 font-medium">Estimated savings: ${optScenarios.current_cost - scen.total_cost}</div>
                            )}
                          </div>
                          <Button 
                            variant="secondary"
                            disabled={applyingScenario}
                            onClick={async () => {
                               setApplyingScenario(true);
                               try {
                                 await applyOptimizedScenario(tripId, scen.items);
                                 toast.success("Scenario applied successfully!");
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
                            {applyingScenario ? "Applying..." : "Apply this plan"}
                          </Button>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                           <div><div className="text-[10px] uppercase text-muted-foreground">Preference Fit</div><div className="font-bold">{scen.preference_match}%</div></div>
                           <div><div className="text-[10px] uppercase text-muted-foreground">Exp Coverage</div><div className="font-bold">{scen.experience_coverage}%</div></div>
                           <div><div className="text-[10px] uppercase text-muted-foreground">Time Eff</div><div className="font-bold">{scen.time_efficiency}%</div></div>
                           <div><div className="text-[10px] uppercase text-muted-foreground">Budget Fit</div><div className="font-bold">{scen.budget_fit}%</div></div>
                        </div>
                        
                        <div className="bg-black/40 p-4 rounded-xl border border-white/5 space-y-3">
                           <div className="text-sm font-semibold mb-2">Why this change?</div>
                           
                           {scen.changes.removed_items.length > 0 && (
                             <div>
                               <div className="text-xs text-destructive uppercase font-bold mb-1">Removed</div>
                               <div className="text-sm text-white/80">{scen.changes.removed_items.map((r:any) => r.description).join(", ")}</div>
                             </div>
                           )}
                           
                           {scen.changes.added_items.length > 0 && (
                             <div>
                               <div className="text-xs text-green-400 uppercase font-bold mb-1">Added</div>
                               <div className="text-sm text-white/80">{scen.changes.added_items.map((a:any) => a.description).join(", ")}</div>
                             </div>
                           )}
                           
                           <div className="mt-2 text-xs italic text-muted-foreground pt-2 border-t border-white/10">
                             Reason: {scen.changes.explanation}
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

    </div>
  );
}
