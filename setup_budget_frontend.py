import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

def append_to_file(path, content):
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n" + content.strip() + "\n")

def replace_in_file(path, old, new):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if old not in content:
        print(f"Warning: '{old}' not found in {path}")
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# 1. Update api.ts
api_methods = """
export async function optimizeBudget(tripId: number, payload: any) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/budget/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Failed to optimize budget");
  return res.json();
}

export async function applyOptimizedScenario(tripId: number, items: any[]) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/itinerary/apply-scenario`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario_items: items })
  });
  if (!res.ok) throw new Error("Failed to apply scenario");
  return res.json();
}
"""
append_to_file("frontend/src/lib/api.ts", api_methods)

# 2. Update PlanPage
replace_in_file("frontend/src/app/(traveler)/trips/[id]/plan/page.tsx", 
                """import { generateItinerary, fetchActiveItinerary, fetchTripPreferences, fetchItineraryExplanation } from "@/lib/api";""", 
                """import { generateItinerary, fetchActiveItinerary, fetchTripPreferences, fetchItineraryExplanation, optimizeBudget, applyOptimizedScenario } from "@/lib/api";""")

replace_in_file("frontend/src/app/(traveler)/trips/[id]/plan/page.tsx", 
                """import { Sparkles, Calendar, Clock, MapPin, DollarSign, Activity, AlertCircle, RefreshCw, CheckCircle2, ArrowRight, Info, Target, ShieldCheck } from "lucide-react";""", 
                """import { Sparkles, Calendar, Clock, MapPin, DollarSign, Activity, AlertCircle, RefreshCw, CheckCircle2, ArrowRight, Info, Target, ShieldCheck, Zap } from "lucide-react";""")

replace_in_file("frontend/src/app/(traveler)/trips/[id]/plan/page.tsx",
                "const [selectedItemExplanation, setSelectedItemExplanation] = useState<any>(null);",
                """const [selectedItemExplanation, setSelectedItemExplanation] = useState<any>(null);
  
  // Optimizer state
  const [optimizerOpen, setOptimizerOpen] = useState(false);
  const [targetBudget, setTargetBudget] = useState(5000);
  const [optPriority, setOptPriority] = useState("balanced");
  const [optimizing, setOptimizing] = useState(false);
  const [optScenarios, setOptScenarios] = useState<any>(null);
  const [applyingScenario, setApplyingScenario] = useState(false);""")

replace_in_file("frontend/src/app/(traveler)/trips/[id]/plan/page.tsx",
                """const expl = await fetchItineraryExplanation(tripId);
        setExplanation(expl);
      }
    } catch (err) {""",
                """const expl = await fetchItineraryExplanation(tripId);
        setExplanation(expl);
        setTargetBudget(tripPrefs.preferences?.budget || 5000);
      }
    } catch (err) {""")

optimizer_modal = """
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
"""

replace_in_file("frontend/src/app/(traveler)/trips/[id]/plan/page.tsx",
                "</DialogContent>\n      </Dialog>\n    </div>",
                "</DialogContent>\n      </Dialog>\n" + optimizer_modal + "\n    </div>")

replace_in_file("frontend/src/app/(traveler)/trips/[id]/plan/page.tsx",
                """<div className="flex flex-col gap-3">
              {itinerary && (
                <Button variant="outline" onClick={handleGenerate} disabled={generating} className="glass-card">
                  <RefreshCw className={`w-4 h-4 mr-2 ${generating ? 'animate-spin' : ''}`} />
                  Regenerate Version
                </Button>
              )}
            </div>""",
                """<div className="flex flex-col gap-3">
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
            </div>""")

print("Budget frontend added.")
