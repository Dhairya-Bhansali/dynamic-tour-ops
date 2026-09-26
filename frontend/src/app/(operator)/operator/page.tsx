"use client";
import { useEffect, useState } from "react";
import { DataHealth } from "@/components/DataHealth";
import { getOperatorDisruptions } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertTriangle, ArrowRight } from "lucide-react";

export default function OperatorDashboard() {
  const [disruptions, setDisruptions] = useState<any[]>([]);

  useEffect(() => {
    getOperatorDisruptions().then(setDisruptions).catch(console.error);
  }, []);

  const activeCount = disruptions.filter(d => d.status === "DETECTED" || d.status === "ALTERNATIVES_READY").length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Control Tower</h1>
        <p className="text-muted-foreground">Mission control for tour operations.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="h-32 rounded-xl border border-white/5 glass flex flex-col justify-center px-6">
          <p className="text-sm text-muted-foreground font-medium mb-1">Active Tours</p>
          <p className="text-3xl font-bold">12</p>
        </div>
        <div className="h-32 rounded-xl border border-white/5 glass flex flex-col justify-center px-6">
          <p className="text-sm text-muted-foreground font-medium mb-1">Disruption Alerts</p>
          <p className="text-3xl font-bold text-destructive">{activeCount}</p>
        </div>
        <div className="h-32 rounded-xl border border-white/5 glass flex flex-col justify-center px-6">
          <p className="text-sm text-muted-foreground font-medium mb-1">Pending Approvals</p>
          <p className="text-3xl font-bold text-primary">5</p>
        </div>
      </div>
      
      {disruptions.length > 0 && (
        <div className="mt-8">
           <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><AlertTriangle className="w-5 h-5 text-destructive" /> Active Disruptions</h2>
           <div className="space-y-4">
              {disruptions.map(d => (
                 <Card key={d.id} className="glass-card border-white/10">
                    <CardContent className="p-4 flex items-center justify-between">
                       <div>
                          <div className="flex items-center gap-3 mb-1">
                             <Badge variant="outline" className="bg-destructive/10 text-destructive border-destructive/20">{d.type}</Badge>
                             <Badge variant="outline" className="border-white/20 text-muted-foreground">{d.status}</Badge>
                             <span className="text-sm text-muted-foreground">Trip #{d.trip_id}</span>
                          </div>
                          <h3 className="font-bold text-lg">{d.title}</h3>
                          <div className="text-sm text-muted-foreground mt-1 flex gap-4">
                             <span>Severity: {d.severity}</span>
                             {d.impact && <span className="text-destructive font-medium">Impact: +${d.impact.cost_impact}</span>}
                          </div>
                       </div>
                       <Button variant="outline" onClick={() => window.location.href = `/trips/${d.trip_id}/plan`}>
                          Review Trip <ArrowRight className="w-4 h-4 ml-2" />
                       </Button>
                    </CardContent>
                 </Card>
              ))}
           </div>
        </div>
      )}

      <div className="mt-8">
        <DataHealth />
      </div>
    </div>
  );
}
