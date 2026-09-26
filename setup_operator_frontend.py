import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

def append_to_file(path, content):
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n" + content.strip() + "\n")

# 1. Update api.ts
api_methods = """
export async function getOperatorDashboard() {
  const res = await fetch(`${API_BASE}/operator/dashboard`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}
export async function getOperatorTours(statusFilter: string = "ALL") {
  const res = await fetch(`${API_BASE}/operator/tours?status_filter=${statusFilter}`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}
export async function getOperatorAlerts() {
  const res = await fetch(`${API_BASE}/operator/alerts`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}
export async function getOperatorTourDetail(tripId: number) {
  const res = await fetch(`${API_BASE}/operator/tours/${tripId}`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}
"""
append_to_file("frontend/src/lib/api.ts", api_methods)

# 2. Update operator page
operator_page = """
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getOperatorDashboard, getOperatorTours, getOperatorAlerts } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { toast } from "sonner";
import { AlertCircle, ArrowRight, Briefcase, CalendarCheck, CheckCircle2, ChevronRight, Compass, Users } from "lucide-react";
import dayjs from "dayjs";

export default function OperatorDashboard() {
  const router = useRouter();
  const [metrics, setMetrics] = useState<any>(null);
  const [tours, setTours] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [filter, setFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [filter]);

  async function loadData() {
    setLoading(true);
    try {
      const [m, t, a] = await Promise.all([
        getOperatorDashboard(),
        getOperatorTours(filter),
        getOperatorAlerts()
      ]);
      setMetrics(m);
      setTours(t);
      setAlerts(a);
    } catch(err) {
      toast.error("Failed to load operator data");
    } finally {
      setLoading(false);
    }
  }

  if (loading && !metrics) return <div className="p-12"><Skeleton className="h-96 w-full rounded-3xl" /></div>;

  return (
    <div className="min-h-screen bg-black/95 text-white pb-24">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/50 backdrop-blur-md pt-20 pb-8 px-8">
        <div className="max-w-7xl mx-auto flex justify-between items-end">
          <div>
            <h1 className="text-4xl font-bold tracking-tight mb-2">Control Tower</h1>
            <p className="text-muted-foreground">Mission control for tour operations.</p>
          </div>
          <Button variant="outline" className="border-white/20">Operator Settings</Button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-8 py-8 space-y-10">
        
        {/* Top KPIs */}
        {metrics && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
             <Card className="glass-card border-white/10 bg-white/5">
                <CardContent className="p-6">
                  <div className="text-sm text-muted-foreground mb-1 uppercase tracking-wider font-semibold">Active Tours</div>
                  <div className="text-4xl font-bold">{metrics.active_tours}</div>
                </CardContent>
             </Card>
             <Card className="glass-card border-white/10 bg-white/5">
                <CardContent className="p-6">
                  <div className="text-sm text-muted-foreground mb-1 uppercase tracking-wider font-semibold">Upcoming</div>
                  <div className="text-4xl font-bold text-white/80">{metrics.upcoming_tours}</div>
                </CardContent>
             </Card>
             <Card className="glass-card border-white/10 bg-white/5">
                <CardContent className="p-6">
                  <div className="text-sm text-muted-foreground mb-1 uppercase tracking-wider font-semibold">Travelers</div>
                  <div className="text-4xl font-bold text-white/80">{metrics.total_travelers}</div>
                </CardContent>
             </Card>
             <Card className="glass-card border-white/10 bg-white/5">
                <CardContent className="p-6">
                  <div className="text-sm text-muted-foreground mb-1 uppercase tracking-wider font-semibold">Confirmations</div>
                  <div className="text-4xl font-bold text-white/80">{metrics.confirmed_bookings}</div>
                </CardContent>
             </Card>
             <Card className={`glass-card border-white/10 ${metrics.attention_required > 0 ? "bg-red-500/10 border-red-500/30" : "bg-white/5"}`}>
                <CardContent className="p-6">
                  <div className={`text-sm mb-1 uppercase tracking-wider font-semibold ${metrics.attention_required > 0 ? "text-red-400" : "text-muted-foreground"}`}>Attention Required</div>
                  <div className={`text-4xl font-bold ${metrics.attention_required > 0 ? "text-red-500" : "text-white/80"}`}>{metrics.attention_required}</div>
                </CardContent>
             </Card>
          </div>
        )}

        <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
          
          <div className="xl:col-span-3 space-y-6">
            
            <div className="flex justify-between items-end">
              <h2 className="text-2xl font-bold tracking-tight">Active Tours</h2>
              <div className="flex gap-2">
                 {['ALL', 'ACTIVE', 'UPCOMING', 'ATTENTION_REQUIRED', 'COMPLETED'].map(f => (
                   <Button key={f} variant={filter === f ? 'default' : 'outline'} size="sm" onClick={() => setFilter(f)} className={filter !== f ? "border-white/10" : ""}>
                     {f.replace('_', ' ')}
                   </Button>
                 ))}
              </div>
            </div>

            <Card className="glass-card border-white/10 overflow-hidden">
               <Table>
                 <TableHeader className="bg-white/5 border-b border-white/10">
                   <TableRow className="border-none hover:bg-transparent">
                     <TableHead className="text-white">Trip</TableHead>
                     <TableHead className="text-white">Traveler</TableHead>
                     <TableHead className="text-white">Destination</TableHead>
                     <TableHead className="text-white">Dates</TableHead>
                     <TableHead className="text-white">Status</TableHead>
                     <TableHead className="text-white">Bookings</TableHead>
                     <TableHead className="text-white">Next Activity</TableHead>
                     <TableHead className="text-white text-right">Action</TableHead>
                   </TableRow>
                 </TableHeader>
                 <TableBody>
                    {loading ? (
                      <TableRow><TableCell colSpan={8} className="text-center py-12"><RefreshCw className="w-6 h-6 animate-spin mx-auto text-muted-foreground"/></TableCell></TableRow>
                    ) : tours.length === 0 ? (
                      <TableRow><TableCell colSpan={8} className="text-center py-12 text-muted-foreground">No tours matching filter.</TableCell></TableRow>
                    ) : tours.map(tour => (
                      <TableRow key={tour.trip_id} className="border-b border-white/5 hover:bg-white/5 cursor-pointer transition-colors" onClick={() => router.push(`/operator/tours/${tour.trip_id}`)}>
                         <TableCell className="font-mono text-xs">TRIP-{tour.trip_id}</TableCell>
                         <TableCell className="font-medium">{tour.traveler_name}</TableCell>
                         <TableCell>{tour.destination}</TableCell>
                         <TableCell className="text-sm whitespace-nowrap">
                            {tour.start_date ? dayjs(tour.start_date).format("MMM D") : "TBD"}
                            {tour.end_date && ` → ${dayjs(tour.end_date).format("MMM D")}`}
                         </TableCell>
                         <TableCell>
                            <Badge variant={tour.attention_state ? "destructive" : tour.status === 'ACTIVE' ? "default" : "secondary"}>
                              {tour.status.replace('_', ' ')}
                            </Badge>
                         </TableCell>
                         <TableCell>
                            <div className="flex items-center gap-2">
                               <CheckCircle2 className={`w-4 h-4 ${tour.booking_completion.split('/')[0] === tour.booking_completion.split('/')[1] ? 'text-green-500' : 'text-muted-foreground'}`}/>
                               <span className="text-sm">{tour.booking_completion}</span>
                            </div>
                         </TableCell>
                         <TableCell className="text-sm text-muted-foreground max-w-[200px] truncate">{tour.next_scheduled_activity || "None scheduled"}</TableCell>
                         <TableCell className="text-right">
                           <Button variant="ghost" size="icon" className="hover:bg-white/10"><ChevronRight className="w-4 h-4"/></Button>
                         </TableCell>
                      </TableRow>
                    ))}
                 </TableBody>
               </Table>
            </Card>
          </div>

          <div className="space-y-6">
            <h2 className="text-xl font-bold tracking-tight text-red-400 flex items-center gap-2"><AlertCircle className="w-5 h-5"/> Attention Center</h2>
            
            <div className="space-y-4">
               {alerts.length === 0 ? (
                 <div className="text-sm text-muted-foreground bg-white/5 p-6 rounded-xl text-center border border-white/5">
                    No critical alerts.
                 </div>
               ) : alerts.map(alert => (
                 <Card key={alert.id} className="glass-card border-red-500/20 bg-red-500/5 cursor-pointer hover:bg-red-500/10 transition-colors" onClick={() => router.push(`/operator/tours/${alert.trip_id}`)}>
                    <CardContent className="p-5">
                       <div className="flex justify-between items-start mb-3">
                          <Badge variant="destructive" className="text-[10px]">{alert.severity}</Badge>
                          <span className="text-xs text-muted-foreground font-mono">TRIP-{alert.trip_id}</span>
                       </div>
                       <h4 className="font-bold text-sm mb-1">{alert.affected_item}</h4>
                       <p className="text-xs text-white/70 mb-3">{alert.reason}</p>
                       <div className="text-xs font-semibold text-primary">{alert.recommended_action}</div>
                    </CardContent>
                 </Card>
               ))}
            </div>

            <Card className="glass-card border-white/10">
               <CardHeader className="pb-3 border-b border-white/10">
                 <CardTitle className="text-sm flex items-center gap-2 text-muted-foreground"><Compass className="w-4 h-4"/> Live Operations Map</CardTitle>
               </CardHeader>
               <CardContent className="p-0">
                  <div className="h-64 bg-black relative flex items-center justify-center overflow-hidden">
                     {/* Polished Mock Map */}
                     <div className="absolute inset-0 opacity-30 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary/20 via-black to-black"></div>
                     <div className="absolute top-1/4 left-1/4 w-3 h-3 bg-green-500 rounded-full animate-ping"></div>
                     <div className="absolute top-1/2 left-2/3 w-3 h-3 bg-red-500 rounded-full animate-ping"></div>
                     <div className="absolute bottom-1/4 right-1/4 w-3 h-3 bg-primary rounded-full animate-ping"></div>
                     
                     <div className="text-center z-10 p-4">
                        <Badge variant="outline" className="bg-black/50 backdrop-blur border-white/20 mb-2">DEMO MAP DATA</Badge>
                        <p className="text-xs text-muted-foreground">Map provider disconnected</p>
                     </div>
                  </div>
               </CardContent>
            </Card>

          </div>
        </div>
      </main>
    </div>
  );
}

// Ensure the page doesn't try to use a hook that doesn't exist.
import { RefreshCw } from "lucide-react";
"""
create_file("frontend/src/app/(operator)/operator/page.tsx", operator_page)

# 3. Create operator tour detail page
tour_detail_page = """
"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { getOperatorTourDetail } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { AlertCircle, ArrowLeft, Calendar, CheckCircle2, Clock, MapPin, Store, CreditCard, ChevronRight } from "lucide-react";
import dayjs from "dayjs";

export default function OperatorTourDetail({ params }: { params: Promise<{ tripId: string }> }) {
  const unwrappedParams = use(params);
  const router = useRouter();
  const tripId = parseInt(unwrappedParams.tripId);
  
  const [tour, setTour] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [tripId]);

  async function loadData() {
    setLoading(true);
    try {
      const data = await getOperatorTourDetail(tripId);
      setTour(data);
    } catch(err) {
      toast.error("Failed to load tour details.");
    } finally {
      setLoading(false);
    }
  }

  if (loading || !tour) return <div className="p-12"><Skeleton className="h-[600px] w-full rounded-3xl" /></div>;

  return (
    <div className="min-h-screen bg-black/95 text-white pb-24">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/50 backdrop-blur-md pt-20 pb-8 px-8 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-6">
            <Button variant="ghost" size="icon" onClick={() => router.push('/operator')} className="hover:bg-white/10 rounded-full h-10 w-10">
               <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <div className="flex items-center gap-3 mb-1">
                 <h1 className="text-3xl font-bold tracking-tight">TRIP-{tour.trip_id}</h1>
                 <Badge variant={tour.readiness === 'READY' ? 'default' : 'destructive'}>{tour.readiness}</Badge>
              </div>
              <p className="text-muted-foreground">{tour.traveler_name} • {tour.destination}</p>
            </div>
          </div>
          <div className="flex gap-3">
             <Button variant="outline" className="border-white/20">Contact Traveler</Button>
             <Button variant="outline" className="border-white/20">Mark Attention Resolved</Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-8 py-8">
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          <div className="space-y-6">
             <Card className="glass-card border-white/10">
               <CardHeader className="pb-4 border-b border-white/10">
                 <CardTitle className="text-lg">Trip Overview</CardTitle>
               </CardHeader>
               <CardContent className="pt-6 space-y-4">
                 <div className="flex justify-between border-b border-white/5 pb-2">
                    <span className="text-muted-foreground">Traveler</span>
                    <span className="font-medium">{tour.traveler_name}</span>
                 </div>
                 <div className="flex justify-between border-b border-white/5 pb-2">
                    <span className="text-muted-foreground">Dates</span>
                    <span className="font-medium">{tour.start_date ? dayjs(tour.start_date).format('MMM D, YYYY') : 'TBD'}</span>
                 </div>
                 <div className="flex justify-between border-b border-white/5 pb-2">
                    <span className="text-muted-foreground">Budget</span>
                    <span className="font-medium">${tour.budget}</span>
                 </div>
                 <div className="flex justify-between border-b border-white/5 pb-2">
                    <span className="text-muted-foreground">Coordinator</span>
                    <span className="font-medium">{tour.coordinator}</span>
                 </div>
                 <div className="flex justify-between border-b border-white/5 pb-2">
                    <span className="text-muted-foreground">Itinerary Version</span>
                    <span className="font-medium font-mono">v{tour.current_itinerary_version}</span>
                 </div>
               </CardContent>
             </Card>
             
             <Card className="glass-card border-white/10">
               <CardHeader className="pb-4 border-b border-white/10">
                 <CardTitle className="text-lg">Readiness Check</CardTitle>
               </CardHeader>
               <CardContent className="pt-6 space-y-6">
                 <div>
                    <div className="flex justify-between text-sm mb-2 font-medium">
                      <span>Bookings Confirmed</span>
                      <span className={tour.booking_completion.split('/')[0] === tour.booking_completion.split('/')[1] ? "text-green-400" : "text-yellow-400"}>{tour.booking_completion}</span>
                    </div>
                    <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden">
                      <div className="h-full bg-primary" style={{ width: `${(parseInt(tour.booking_completion.split('/')[0]) / Math.max(1, parseInt(tour.booking_completion.split('/')[1]))) * 100}%` }} />
                    </div>
                 </div>
               </CardContent>
             </Card>
             
             <Card className="glass-card border-white/10">
               <CardHeader className="pb-4 border-b border-white/10">
                 <CardTitle className="text-lg flex items-center gap-2"><Store className="w-5 h-5"/> Involved Vendors</CardTitle>
               </CardHeader>
               <CardContent className="pt-6 space-y-4">
                 {tour.vendors.map((v: any) => (
                    <div key={v.id} className="flex justify-between items-center p-3 rounded-xl bg-white/5 border border-white/5">
                       <div>
                          <Badge variant="outline" className="text-[10px] mb-1">{v.service_type}</Badge>
                          <div className="font-bold text-sm">{v.name}</div>
                          <div className="text-xs text-muted-foreground">{v.location}</div>
                       </div>
                       <div className="text-right">
                          <div className="text-xs text-green-400 font-bold mb-1">{v.status}</div>
                          <div className="text-sm">${v.cost}</div>
                       </div>
                    </div>
                 ))}
                 {tour.vendors.length === 0 && <div className="text-sm text-muted-foreground text-center">No vendors yet.</div>}
               </CardContent>
             </Card>
          </div>

          <div className="lg:col-span-2 space-y-6">
             <div className="flex justify-between items-center mb-2">
                <h2 className="text-2xl font-bold tracking-tight">Operational Timeline</h2>
                <Button variant="outline" size="sm" className="border-white/20">Edit Timeline</Button>
             </div>
             
             <div className="space-y-4 relative before:absolute before:inset-y-0 before:left-[19px] before:w-0.5 before:bg-white/10">
               {tour.timeline.map((item: any) => (
                 <div key={item.id} className="relative pl-12">
                   <div className={`absolute left-0 w-10 h-10 rounded-full flex items-center justify-center border-4 border-black z-10 ${
                     item.booking_status === 'CONFIRMED' ? 'bg-green-500' : 
                     item.booking_status === 'PENDING' ? 'bg-yellow-500' : 'bg-red-500'
                   }`}>
                     <CheckCircle2 className="w-5 h-5 text-black" />
                   </div>
                   
                   <Card className={`glass-card border-white/10 overflow-hidden ${item.booking_status !== 'CONFIRMED' ? 'border-l-4 border-l-red-500' : 'border-l-4 border-l-green-500'}`}>
                     <CardContent className="p-5 flex justify-between items-center">
                        <div>
                           <div className="flex items-center gap-2 mb-2">
                              <Badge variant="outline" className="bg-white/5">{dayjs(item.date).format("MMM D")}</Badge>
                              <span className="text-sm text-muted-foreground flex items-center gap-1"><Clock className="w-3.5 h-3.5"/> {item.start ? dayjs(item.start).format("HH:mm") : 'Anytime'}</span>
                           </div>
                           <h4 className="font-bold text-lg mb-1">{item.activity}</h4>
                           <div className="text-sm text-muted-foreground flex items-center gap-1">
                              <MapPin className="w-3.5 h-3.5"/> {item.location || 'No location'}
                           </div>
                           {item.provider && (
                              <div className="mt-3 text-xs bg-white/5 inline-flex items-center gap-1 px-2 py-1 rounded-md border border-white/10">
                                <Store className="w-3 h-3 text-primary"/> Provider: {item.provider}
                              </div>
                           )}
                        </div>
                        <div className="text-right">
                           <div className="text-xl font-bold mb-1">${item.cost || 0}</div>
                           <div className={`text-xs font-bold ${
                              item.booking_status === 'CONFIRMED' ? 'text-green-500' : 'text-red-500'
                           }`}>{item.booking_status}</div>
                        </div>
                     </CardContent>
                   </Card>
                 </div>
               ))}
               {tour.timeline.length === 0 && <div className="pl-12 text-muted-foreground">No items in timeline.</div>}
             </div>
          </div>
          
        </div>
      </main>
    </div>
  );
}
"""
create_file("frontend/src/app/(operator)/operator/tours/[tripId]/page.tsx", tour_detail_page)

print("Frontend setup complete")
