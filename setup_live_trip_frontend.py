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
export async function getLiveTripStatus(tripId: number) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/live`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}
export async function sendMessageToAssistant(tripId: number, message: string) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/assistant`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}
"""
append_to_file("frontend/src/lib/api.ts", api_methods)

# 2. Update Plan page to add Live Trip entry point
replace_in_file("frontend/src/app/(traveler)/trips/[id]/plan/page.tsx",
                """<Button size="lg" onClick={() => router.push(`/trips/${tripId}/book`)} className="rounded-full h-14 px-8 text-lg font-medium shadow-[0_0_30px_rgba(168,85,247,0.3)]">
                Review & Book <ArrowRight className="w-5 h-5 ml-2" />
              </Button>""",
                """<div className="flex gap-4"><Button size="lg" onClick={() => router.push(`/trips/${tripId}/book`)} className="rounded-full h-14 px-8 text-lg font-medium shadow-[0_0_30px_rgba(168,85,247,0.3)]">
                Review & Book
              </Button>
              <Button size="lg" onClick={() => router.push(`/trips/${tripId}/assist`)} variant="secondary" className="rounded-full h-14 px-8 text-lg font-medium shadow-[0_0_30px_rgba(255,255,255,0.1)] border border-white/20">
                LIVE TRIP <ArrowRight className="w-5 h-5 ml-2" />
              </Button></div>""")

# 3. Create Live Trip Assist page
assist_page = """
"use client";

import { useEffect, useState, use, useRef } from "react";
import { useRouter } from "next/navigation";
import { getLiveTripStatus, sendMessageToAssistant } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { AlertCircle, ArrowRight, ArrowLeft, Send, Compass, MapPin, CheckCircle2, Clock, Map } from "lucide-react";
import dayjs from "dayjs";

export default function LiveTripPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const router = useRouter();
  const tripId = parseInt(unwrappedParams.id);
  
  const [live, setLive] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  const [chat, setChat] = useState<{sender: 'user'|'assistant', text: string}[]>([
     { sender: 'assistant', text: "I'm your Live Trip Assistant! Ask me what's next, check your status, or get details about today's itinerary." }
  ]);
  const [msg, setMsg] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadData();
  }, [tripId]);
  
  useEffect(() => {
    if(chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;
  }, [chat]);

  async function loadData() {
    setLoading(true);
    try {
      const data = await getLiveTripStatus(tripId);
      setLive(data);
    } catch(err) {
      toast.error("Failed to load live trip context.");
    } finally {
      setLoading(false);
    }
  }

  const handleSend = async () => {
    if(!msg.trim()) return;
    const m = msg;
    setMsg("");
    setChat(prev => [...prev, { sender: 'user', text: m }]);
    
    setChatLoading(true);
    try {
      const res = await sendMessageToAssistant(tripId, m);
      // Format markdown response slightly for demo
      const cleanRes = res.response.replace(/\\n/g, "\\n");
      setChat(prev => [...prev, { sender: 'assistant', text: cleanRes }]);
    } catch(e) {
      toast.error("Assistant failed to respond.");
    } finally {
      setChatLoading(false);
    }
  };

  if (loading || !live) return <div className="p-12 max-w-4xl mx-auto"><Skeleton className="h-[500px] w-full rounded-3xl" /></div>;

  return (
    <div className="min-h-screen bg-black/95 text-white pb-24">
      {/* Header */}
      <header className="relative border-b border-white/10 bg-black/50 backdrop-blur-md z-10 pt-20 pb-6 px-6 sticky top-0">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-4">
             <Button variant="ghost" size="icon" onClick={() => router.push(`/trips/${tripId}/plan`)} className="rounded-full">
                <ArrowLeft className="w-5 h-5" />
             </Button>
             <div>
                <div className="flex items-center gap-3">
                   <h1 className="text-2xl font-bold tracking-tight">Trip to Destination</h1>
                   <Badge variant={live.status_label === 'ACTIVE' ? 'default' : 'secondary'} className="h-6">
                     {live.status_label}
                   </Badge>
                </div>
                <p className="text-sm text-primary font-medium">{live.day_label}</p>
             </div>
          </div>
          <div>
            <Button variant="outline" className="border-white/20">Assist Menu</Button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        
        {live.next_action && (
          <Card className="glass-card bg-primary/10 border-primary/30 mb-8 overflow-hidden relative">
            <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-transparent pointer-events-none" />
            <CardContent className="p-6 relative z-10">
               <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-sm uppercase tracking-wider font-bold text-primary mb-1">Next Action</h3>
                    <div className="text-lg font-medium">{live.next_action.description}</div>
                  </div>
                  <Button size="lg" className="rounded-full shadow-lg shrink-0">Open Maps <ArrowRight className="w-4 h-4 ml-2"/></Button>
               </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          <div className="lg:col-span-2 space-y-8">
             
             {/* Timeline */}
             <div>
               <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><Clock className="w-5 h-5"/> Today's Timeline</h2>
               <div className="space-y-4">
                  {live.timeline.length === 0 ? (
                     <div className="text-muted-foreground bg-white/5 p-6 rounded-xl border border-white/5 text-center">No activities scheduled for today.</div>
                  ) : live.timeline.map((item: any, i: number) => (
                    <Card key={i} className={`glass-card border-white/10 ${item.time_label === 'NOW' ? 'bg-primary/5 border-primary/20' : ''}`}>
                      <CardContent className="p-5 flex justify-between items-center">
                         <div className="flex items-center gap-4">
                            <div className={`w-16 text-center font-bold text-sm ${item.time_label === 'NOW' ? 'text-primary' : 'text-muted-foreground'}`}>
                               {item.time_label}
                            </div>
                            <div>
                               <h4 className="font-bold">{item.title}</h4>
                               <div className="text-sm text-muted-foreground flex items-center gap-1 mt-1">
                                  <MapPin className="w-3.5 h-3.5"/> {item.location}
                               </div>
                            </div>
                         </div>
                         <div className="text-right">
                            <div className="font-mono text-lg">{item.time ? dayjs(item.time).format("HH:mm") : 'TBD'}</div>
                         </div>
                      </CardContent>
                    </Card>
                  ))}
               </div>
             </div>
             
             {/* Bookings & Prep */}
             <div className="grid grid-cols-2 gap-4">
               <Card className="glass-card border-white/10">
                 <CardContent className="p-5">
                   <h3 className="font-bold text-sm text-muted-foreground mb-2">Bookings</h3>
                   <div className="text-xl font-medium">{live.bookings_summary}</div>
                 </CardContent>
               </Card>
               <Card className="glass-card border-white/10">
                 <CardContent className="p-5">
                   <h3 className="font-bold text-sm text-muted-foreground mb-2">Preparation</h3>
                   <div className="text-xl font-medium">{live.prep_summary}</div>
                 </CardContent>
               </Card>
             </div>
             
             {/* Map */}
             <Card className="glass-card border-white/10 overflow-hidden">
               <CardHeader className="bg-white/5 border-b border-white/10 pb-3">
                 <CardTitle className="text-sm flex items-center gap-2"><Map className="w-4 h-4"/> Today's Map</CardTitle>
               </CardHeader>
               <CardContent className="p-0">
                 <div className="h-64 relative bg-[#1a1a1a] flex items-center justify-center">
                    <Badge variant="outline" className="bg-black/50 backdrop-blur z-10">DEMO MAP DATA</Badge>
                    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-white/10 via-transparent to-transparent"></div>
                 </div>
               </CardContent>
             </Card>
             
          </div>

          <div className="space-y-6">
             
             {/* Alerts */}
             {live.alerts.length > 0 && (
                <div className="space-y-3">
                   {live.alerts.map((a: any) => (
                      <div key={a.id} className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-start gap-3">
                         <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                         <div>
                            <div className="font-bold text-sm text-red-400 mb-0.5">{a.severity}</div>
                            <div className="text-sm">{a.message}</div>
                         </div>
                      </div>
                   ))}
                </div>
             )}
             
             {/* Copilot Assistant */}
             <Card className="glass-card border-white/10 flex flex-col h-[600px] sticky top-28">
               <CardHeader className="border-b border-white/10 bg-primary/10 pb-4">
                 <CardTitle className="text-base flex items-center gap-2 text-primary"><Compass className="w-5 h-5"/> Live Assistant</CardTitle>
               </CardHeader>
               <CardContent className="p-0 flex-1 flex flex-col overflow-hidden">
                  <div ref={chatRef} className="flex-1 overflow-y-auto p-4 space-y-4">
                     {chat.map((c, i) => (
                        <div key={i} className={`flex ${c.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                           <div className={`max-w-[85%] rounded-2xl p-3 text-sm ${c.sender === 'user' ? 'bg-primary text-white rounded-br-none' : 'bg-white/10 text-white/90 rounded-bl-none whitespace-pre-wrap'}`}>
                              {c.text}
                           </div>
                        </div>
                     ))}
                     {chatLoading && (
                        <div className="flex justify-start">
                           <div className="bg-white/10 rounded-2xl rounded-bl-none p-3 px-4 text-sm flex gap-1 items-center">
                              <div className="w-1.5 h-1.5 bg-white/50 rounded-full animate-bounce"></div>
                              <div className="w-1.5 h-1.5 bg-white/50 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                              <div className="w-1.5 h-1.5 bg-white/50 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
                           </div>
                        </div>
                     )}
                  </div>
                  <div className="p-4 border-t border-white/10 bg-black/40">
                     <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-2">
                        <Input value={msg} onChange={(e) => setMsg(e.target.value)} placeholder="Ask about your trip..." className="bg-white/5 border-white/10 rounded-full px-4" />
                        <Button type="submit" size="icon" className="rounded-full shrink-0" disabled={!msg.trim() || chatLoading}><Send className="w-4 h-4"/></Button>
                     </form>
                  </div>
               </CardContent>
             </Card>

          </div>
        </div>
      </main>
    </div>
  );
}
"""
create_file("frontend/src/app/(traveler)/trips/[id]/assist/page.tsx", assist_page)

print("Frontend live trip setup complete")
