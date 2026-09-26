"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useTripStore } from "@/store/useTripStore";
import { saveTravelDNA, saveTripPreferences } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowLeft, ArrowRight, Calendar, DollarSign, MapPin, Star, Settings2, Plane, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";

// For demo purposes, assuming traveler_id = 1 and trip_id = 1
const DEMO_TRAVELER_ID = 1;
const DEMO_TRIP_ID = 1;

export default function PersonalizePage() {
  const router = useRouter();
  const { selectedDestination, selectedExperiences } = useTripStore();
  const [step, setStep] = useState(1);
  const [saving, setSaving] = useState(false);
  
  // Form State
  const [dates, setDates] = useState({ start: "", end: "", duration: 7 });
  const [budget, setBudget] = useState(selectedDestination?.budget || 5000);
  const [accommodation, setAccommodation] = useState<string[]>([]);
  const [transportation, setTransportation] = useState<string[]>([]);
  const [travelStyle, setTravelStyle] = useState("");
  const [interests, setInterests] = useState<string[]>([]);
  
  // Travel DNA Calculation (derived)
  const calculateDNA = () => {
    return {
      Adventure: interests.includes("Adventure") ? 9 : 5,
      Culture: interests.includes("Culture") ? 9 : 6,
      Food: interests.includes("Food") ? 8 : 4,
      Nature: interests.includes("Nature") ? 9 : 5,
      Luxury: accommodation.includes("Luxury") ? 10 : (accommodation.includes("Budget") ? 2 : 5),
      Relaxation: travelStyle === "Relaxed" ? 10 : 4,
    };
  };

  useEffect(() => {
    if (!selectedDestination) {
      toast("No destination selected", { description: "Please select a destination first." });
      router.push("/discover");
    }
  }, [selectedDestination, router]);

  if (!selectedDestination) return null;

  const nextStep = () => {
    // Validation
    if (step === 1 && (!dates.start || !dates.end || dates.duration <= 0)) {
        toast.error("Please provide valid dates and duration.");
        return;
    }
    if (step === 2 && budget <= 0) {
        toast.error("Budget must be greater than zero.");
        return;
    }
    setStep(s => Math.min(s + 1, 6));
  };
  const prevStep = () => setStep(s => Math.max(s - 1, 1));

  const toggleArray = (setter: any, array: string[], val: string) => {
    setter(array.includes(val) ? array.filter(i => i !== val) : [...array, val]);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const dna = calculateDNA();
      const prefs = {
        destination_id: selectedDestination.id,
        start_date: dates.start,
        end_date: dates.end,
        duration: dates.duration,
        budget,
        currency: "USD",
        accommodation,
        transportation,
        interests,
        travel_style: travelStyle,
        selected_experiences: selectedExperiences.map(e => e.id)
      };

      await saveTravelDNA(DEMO_TRAVELER_ID, dna);
      await saveTripPreferences(DEMO_TRIP_ID, prefs);

      toast.success("Preferences Saved Successfully", {
        description: "Your Travel DNA and Trip Plan have been securely stored.",
      });
      setStep(6); 
    } catch (err) {
      console.error(err);
      toast.error("Failed to save preferences");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden flex flex-col">
      {/* Background Decor */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-primary/20 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[40%] h-[40%] bg-purple-600/10 blur-[100px] rounded-full pointer-events-none" />

      {/* Header */}
      <header className="px-6 py-6 border-b border-white/5 bg-background/50 backdrop-blur-md relative z-10">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => router.back()}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <h1 className="text-2xl font-bold tracking-tight text-white/90">Trip Personalization</h1>
          </div>
          <div className="text-sm font-medium text-primary">
            Step {step} of 5
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 px-6 py-12 relative z-10">
        <div className="max-w-3xl mx-auto">
          
          {/* Progress Bar */}
          <div className="w-full bg-white/5 h-2 rounded-full mb-12 overflow-hidden">
            <div 
              className="h-full bg-primary transition-all duration-500 ease-out" 
              style={{ width: `${(step / 6) * 100}%` }}
            />
          </div>

          <Card className="glass-card border-white/10 shadow-2xl bg-card/60 backdrop-blur-xl p-8 md:p-12 rounded-3xl min-h-[500px] flex flex-col">
            
            {/* STEP 1: Dates & Duration */}
            {step === 1 && (
              <div className="flex-1 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="flex items-center gap-3 mb-4 text-primary">
                  <Calendar className="w-6 h-6" />
                  <h2 className="text-3xl font-bold">When are you traveling?</h2>
                </div>
                <p className="text-muted-foreground mb-8">Set your dates for {selectedDestination.name}.</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <label className="block text-sm font-medium mb-2">Start Date</label>
                    <input 
                      type="date" 
                      className="w-full bg-background border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-primary/50"
                      value={dates.start}
                      onChange={e => setDates({...dates, start: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">End Date</label>
                    <input 
                      type="date" 
                      className="w-full bg-background border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-primary/50"
                      value={dates.end}
                      onChange={e => setDates({...dates, end: e.target.value})}
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Approximate Duration (Days)</label>
                  <input 
                    type="number" 
                    min="1"
                    className="w-full bg-background border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-primary/50 text-xl font-medium"
                    value={dates.duration}
                    onChange={e => setDates({...dates, duration: parseInt(e.target.value) || 0})}
                  />
                </div>
              </div>
            )}

            {/* STEP 2: Budget & Accommodation */}
            {step === 2 && (
              <div className="flex-1 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="flex items-center gap-3 mb-4 text-primary">
                  <DollarSign className="w-6 h-6" />
                  <h2 className="text-3xl font-bold">Budget & Stays</h2>
                </div>
                <p className="text-muted-foreground mb-8">How would you like to allocate your funds?</p>
                
                <div className="mb-10">
                  <label className="block text-sm font-medium mb-2 flex justify-between">
                    <span>Total Target Budget (USD)</span>
                    <span className="text-primary font-bold">${budget.toLocaleString()}</span>
                  </label>
                  <input 
                    type="range" 
                    min="500" max="25000" step="500"
                    className="w-full accent-primary"
                    value={budget}
                    onChange={e => setBudget(parseInt(e.target.value))}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-4">Accommodation Style (Select multiple)</label>
                  <div className="flex flex-wrap gap-3">
                    {["Budget", "Comfort", "Premium", "Luxury", "Boutique", "Resort", "Hostel"].map(opt => (
                      <div 
                        key={opt}
                        onClick={() => toggleArray(setAccommodation, accommodation, opt)}
                        className={`cursor-pointer px-5 py-3 rounded-xl border transition-all ${accommodation.includes(opt) ? 'bg-primary border-primary text-white' : 'bg-background/50 border-white/10 hover:border-primary/50'}`}
                      >
                        {opt}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* STEP 3: Travel Style & Interests */}
            {step === 3 && (
              <div className="flex-1 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="flex items-center gap-3 mb-4 text-primary">
                  <Star className="w-6 h-6" />
                  <h2 className="text-3xl font-bold">Style & Interests</h2>
                </div>
                
                <div className="mb-8">
                  <label className="block text-sm font-medium mb-4">What's your preferred pace?</label>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {["Relaxed", "Balanced", "Fast-paced"].map(opt => (
                      <div 
                        key={opt}
                        onClick={() => setTravelStyle(opt)}
                        className={`cursor-pointer p-4 text-center rounded-xl border transition-all ${travelStyle === opt ? 'bg-primary/20 border-primary text-primary font-medium' : 'bg-background/50 border-white/10 hover:border-white/30'}`}
                      >
                        {opt}
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-4">Core Interests (Select multiple)</label>
                  <div className="flex flex-wrap gap-3">
                    {["Adventure", "Culture", "Food", "Nature", "Luxury", "Spiritual", "Nightlife", "Shopping", "Photography"].map(opt => (
                      <div 
                        key={opt}
                        onClick={() => toggleArray(setInterests, interests, opt)}
                        className={`cursor-pointer px-5 py-3 rounded-xl border transition-all ${interests.includes(opt) ? 'bg-primary border-primary text-white' : 'bg-background/50 border-white/10 hover:border-primary/50'}`}
                      >
                        {opt}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* STEP 4: Transportation */}
            {step === 4 && (
              <div className="flex-1 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="flex items-center gap-3 mb-4 text-primary">
                  <Plane className="w-6 h-6" />
                  <h2 className="text-3xl font-bold">Getting Around</h2>
                </div>
                <p className="text-muted-foreground mb-8">How do you prefer to travel locally?</p>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {["Public Transport", "Rental Car", "Taxi/Private", "Train", "Internal Flights", "Walking"].map(opt => (
                     <div 
                     key={opt}
                     onClick={() => toggleArray(setTransportation, transportation, opt)}
                     className={`cursor-pointer p-5 rounded-xl border transition-all flex items-center justify-between ${transportation.includes(opt) ? 'bg-primary/10 border-primary' : 'bg-background/50 border-white/10 hover:border-white/30'}`}
                   >
                     <span className={transportation.includes(opt) ? 'text-primary font-medium' : ''}>{opt}</span>
                     {transportation.includes(opt) && <CheckCircle2 className="w-5 h-5 text-primary" />}
                   </div>
                  ))}
                </div>
              </div>
            )}

            {/* STEP 5: Review & Save */}
            {step === 5 && (
              <div className="flex-1 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="flex items-center gap-3 mb-6 text-primary">
                  <Settings2 className="w-6 h-6" />
                  <h2 className="text-3xl font-bold">Review Your Profile</h2>
                </div>
                
                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                      <p className="text-xs text-muted-foreground uppercase mb-1">Destination</p>
                      <p className="font-medium flex items-center gap-2"><MapPin className="w-4 h-4"/>{selectedDestination.name}</p>
                    </div>
                    <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                      <p className="text-xs text-muted-foreground uppercase mb-1">Duration & Budget</p>
                      <p className="font-medium">{dates.duration} Days • ${budget}</p>
                    </div>
                  </div>

                  <div className="p-5 bg-white/5 rounded-xl border border-white/5">
                    <h3 className="font-medium mb-3 text-primary">Generated Travel DNA</h3>
                    <div className="grid grid-cols-2 gap-y-3 gap-x-8">
                      {Object.entries(calculateDNA()).map(([key, val]) => (
                        <div key={key}>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-muted-foreground">{key}</span>
                            <span>{val}/10</span>
                          </div>
                          <div className="w-full bg-black/40 h-1.5 rounded-full overflow-hidden">
                            <div className="h-full bg-primary" style={{ width: `${val * 10}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {selectedExperiences.length > 0 && (
                    <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                      <p className="text-xs text-muted-foreground uppercase mb-2">Selected Experiences</p>
                      <div className="flex flex-wrap gap-2">
                         {selectedExperiences.map(e => (
                           <span key={e.id} className="text-xs px-2 py-1 bg-white/10 rounded-md">{e.name}</span>
                         ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* STEP 6: Success Terminal */}
            {step === 6 && (
              <div className="flex-1 flex flex-col items-center justify-center text-center animate-in zoom-in duration-500">
                <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mb-6">
                  <CheckCircle2 className="w-10 h-10 text-green-500" />
                </div>
                <h2 className="text-3xl font-bold mb-4">Travel DNA Saved</h2>
                <p className="text-muted-foreground max-w-md mb-8">
                  Your preferences and long-term travel profile have been securely stored in the backend. 
                  The AI Itinerary Engine is now ready to generate your perfect journey.
                </p>
                <div className="p-4 rounded-xl bg-primary/10 border border-primary/20 text-primary font-mono text-sm">
                  READY FOR PLANNING PHASE
                </div>
              </div>
            )}

            {/* Navigation */}
            {step === 6 && (
              <div className="mt-8 flex justify-center w-full">
                <Button onClick={() => router.push(`/trips/${DEMO_TRIP_ID}/plan`)} className="px-8 shadow-[0_0_20px_rgba(168,85,247,0.4)] rounded-full text-white h-14 text-lg w-full max-w-sm">
                  Generate My Itinerary <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </div>
            )}
            
            {step < 6 && (
              <div className="mt-12 flex items-center justify-between border-t border-white/10 pt-6">
                <Button variant="ghost" onClick={prevStep} disabled={step === 1 || saving}>
                  <ArrowLeft className="w-4 h-4 mr-2" /> Back
                </Button>
                
                {step < 5 ? (
                  <Button onClick={nextStep} className="px-8 shadow-lg shadow-primary/20 rounded-full">
                    Next <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                ) : (
                  <Button onClick={handleSave} disabled={saving} className="px-8 shadow-[0_0_20px_rgba(168,85,247,0.4)] rounded-full text-white">
                    {saving ? "Saving..." : "Confirm & Save DNA"} <CheckCircle2 className="w-4 h-4 ml-2" />
                  </Button>
                )}
              </div>
            )}

          </Card>
        </div>
      </main>
    </div>
  );
}
