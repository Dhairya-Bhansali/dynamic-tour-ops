"use client";
import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { getBookableItems, checkAvailability, createBooking, getBookings, getPreparation } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { CheckCircle2, AlertCircle, RefreshCw, CreditCard, Clock, CalendarCheck, CheckSquare, Hotel, Info } from "lucide-react";
import dayjs from "dayjs";

export default function BookPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const router = useRouter();
  const tripId = parseInt(unwrappedParams.id);
  
  const [items, setItems] = useState<any[]>([]);
  const [bookings, setBookings] = useState<any[]>([]);
  const [readiness, setReadiness] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  const [checking, setChecking] = useState<number | null>(null);
  const [bookingIds, setBookingIds] = useState<number[]>([]);
  
  // Local state to track availability checks
  const [availabilities, setAvailabilities] = useState<Record<number, any>>({});

  useEffect(() => {
    loadData();
  }, [tripId]);

  async function loadData() {
    try {
      setLoading(true);
      const [bItems, bBookings, bPrep] = await Promise.all([
        getBookableItems(tripId),
        getBookings(tripId),
        getPreparation(tripId)
      ]);
      setItems(bItems);
      setBookings(bBookings);
      setReadiness(bPrep);
    } catch (err) {
      console.error(err);
      toast.error("Failed to load booking data.");
    } finally {
      setLoading(false);
    }
  }

  const handleCheckAvailability = async (itemId: number, cost: number) => {
    setChecking(itemId);
    try {
      const res = await checkAvailability(tripId, itemId, cost);
      setAvailabilities(prev => ({ ...prev, [itemId]: res }));
      if (!res.available) {
         toast.error(res.reason || "Item not available.");
      } else {
         toast.success("Available! Ready to book.");
      }
    } catch(err) {
       toast.error("Error checking availability.");
    } finally {
       setChecking(null);
    }
  };

  const handleBook = async (itemId: number, cost: number) => {
    setBookingIds(prev => [...prev, itemId]);
    try {
      await createBooking(tripId, itemId, cost);
      toast.success("Booking confirmed!");
      await loadData();
    } catch(err) {
      toast.error("Failed to confirm booking.");
    } finally {
      setBookingIds(prev => prev.filter(id => id !== itemId));
    }
  };

  if (loading) return <div className="p-12 max-w-4xl mx-auto"><Skeleton className="h-64 w-full rounded-3xl" /></div>;

  const totalCost = items.reduce((acc, curr) => acc + (curr.estimated_cost || 0), 0);

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <header className="relative border-b border-white/10 bg-background/50 backdrop-blur-md z-10 pt-24 pb-8 px-6">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/10 to-transparent pointer-events-none" />
        <div className="max-w-5xl mx-auto relative z-10">
          <div className="flex justify-between items-end">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4 text-white">Review & Book</h1>
              <p className="text-muted-foreground">Secure your itinerary items. We separate live bookings from demo providers.</p>
            </div>
            <Button variant="outline" onClick={() => router.push(`/trips/${tripId}/plan`)}>Back to Plan</Button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          <div className="lg:col-span-2 space-y-6">
            <h2 className="text-2xl font-bold mb-4">Bookable Components</h2>
            
            {items.map(item => {
              const bMatch = bookings.find(b => b.itinerary_item_id === item.itinerary_item_id);
              const avail = availabilities[item.itinerary_item_id];
              const isChecking = checking === item.itinerary_item_id;
              const isBooking = bookingIds.includes(item.itinerary_item_id);
              
              return (
                <Card key={item.itinerary_item_id} className="glass-card border-white/10 overflow-hidden">
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start mb-4">
                       <div>
                         <Badge variant="outline" className="mb-2 bg-white/5">{item.activity_type}</Badge>
                         <h3 className="text-xl font-bold text-white mb-1">{item.description}</h3>
                         <div className="text-sm text-muted-foreground flex items-center gap-2">
                           <Clock className="w-3.5 h-3.5"/> 
                           {item.start_time ? dayjs(item.start_time).format("MMM D, HH:mm") : "Anytime"}
                         </div>
                       </div>
                       <div className="text-right">
                         <div className="text-2xl font-bold text-primary">${item.estimated_cost}</div>
                       </div>
                    </div>
                    
                    {bMatch ? (
                      <div className="bg-green-500/10 border border-green-500/20 p-4 rounded-xl flex items-center justify-between">
                         <div>
                            <div className="flex items-center gap-2 mb-1">
                               <CheckCircle2 className="w-4 h-4 text-green-500" />
                               <span className="font-bold text-green-500">{bMatch.status}</span>
                            </div>
                            <div className="text-xs text-green-500/80">Code: {bMatch.confirmation_code}</div>
                         </div>
                         <Badge variant="outline" className="text-[10px] h-5">{bMatch.source_type} BOOKING</Badge>
                      </div>
                    ) : (
                      <div className="border-t border-white/10 pt-4 mt-4 flex items-center justify-between">
                         <div>
                           {avail?.available === false && (
                              <div className="text-sm text-destructive flex items-center gap-1.5 mb-2"><AlertCircle className="w-4 h-4"/> {avail.reason}</div>
                           )}
                           {avail?.available === true && (
                              <div className="text-sm text-green-400 flex items-center gap-1.5 mb-2"><CheckCircle2 className="w-4 h-4"/> Available with {avail.provider_id}</div>
                           )}
                         </div>
                         <div className="flex gap-3">
                           {!avail?.available && (
                             <Button variant="secondary" size="sm" onClick={() => handleCheckAvailability(item.itinerary_item_id, item.estimated_cost)} disabled={isChecking}>
                               {isChecking ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : null}
                               Check Availability
                             </Button>
                           )}
                           {avail?.available && (
                             <Button variant="default" size="sm" onClick={() => handleBook(item.itinerary_item_id, item.estimated_cost)} disabled={isBooking}>
                               {isBooking ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : "Confirm Booking"}
                             </Button>
                           )}
                         </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <div className="space-y-6">
            <Card className="glass-card border-primary/20 sticky top-24">
              <CardHeader className="pb-4 border-b border-white/10 bg-primary/5">
                <CardTitle className="text-lg flex items-center gap-2"><CreditCard className="w-5 h-5"/> Trip Total</CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="space-y-3 text-sm text-muted-foreground mb-6">
                   <div className="flex justify-between"><span>All Items</span><span>${totalCost}</span></div>
                   <div className="flex justify-between text-green-400 font-medium"><span>Confirmed</span><span>${bookings.reduce((a,c)=>a+c.estimated_cost,0)}</span></div>
                </div>
                <div className="flex justify-between items-center text-xl font-bold border-t border-white/10 pt-4">
                  <span>Estimated Total</span>
                  <span className="text-primary">${totalCost}</span>
                </div>
              </CardContent>
            </Card>

            {readiness && (
              <Card className="glass-card border-white/10 overflow-hidden">
                <CardHeader className="bg-black/40 border-b border-white/5 pb-4">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-lg">Trip Readiness</CardTitle>
                    <Badge variant={readiness.status === "READY" ? "default" : "destructive"}>{readiness.status}</Badge>
                  </div>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="space-y-6">
                    <div>
                      <div className="flex justify-between text-sm mb-2 font-medium">
                        <span>Booking Completion</span>
                        <span className={readiness.booking_completion === 100 ? "text-green-400" : ""}>{readiness.booking_completion}%</span>
                      </div>
                      <div className="w-full bg-black/40 h-2 rounded-full overflow-hidden">
                        <div className="h-full bg-primary" style={{ width: `${readiness.booking_completion}%` }} />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="bg-white/5 p-3 rounded-lg border border-white/5">
                        <div className="text-[10px] text-muted-foreground uppercase mb-1">Confirmations</div>
                        <div className="font-bold">{readiness.required_confirmations}</div>
                      </div>
                      <div className="bg-white/5 p-3 rounded-lg border border-white/5">
                        <div className="text-[10px] text-muted-foreground uppercase mb-1">Preparation</div>
                        <div className="font-bold">{readiness.preparation}</div>
                      </div>
                    </div>

                    <div className="space-y-2 border-t border-white/10 pt-6">
                      <h4 className="text-sm font-semibold mb-3">Preparation Checklist</h4>
                      {readiness.tasks.map((t: any) => (
                        <div key={t.id} className="flex items-start gap-3 text-sm">
                           {t.status === 'DONE' ? <CheckCircle2 className="w-4 h-4 text-green-500 shrink-0 mt-0.5" /> : <div className="w-4 h-4 rounded-full border border-white/30 shrink-0 mt-0.5" />}
                           <span className={t.status === 'DONE' ? 'text-muted-foreground line-through' : 'text-white/90'}>{t.title}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

        </div>
      </main>
    </div>
  );
}
