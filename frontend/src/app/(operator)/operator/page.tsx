"use client";
import { useEffect, useState } from "react";
import { DataHealth } from "@/components/DataHealth";
import { getOperatorDisruptions, getOperatorCostControl } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertTriangle, ArrowRight, DollarSign, Activity } from "lucide-react";

export default function OperatorDashboard() {
  const [disruptions, setDisruptions] = useState<any[]>([]);
  const [costControl, setCostControl] = useState<any>(null);

  useEffect(() => {
    getOperatorDisruptions().then(setDisruptions).catch(console.error);
    getOperatorCostControl().then(setCostControl).catch(console.error);
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Cost Control Tower</h1>
        <p className="text-muted-foreground">Mission control for tour operations and financial risk.</p>
      </div>
      
      {/* Metrics Row */}
      {costControl && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="p-4 rounded-xl border border-white/5 bg-black/40">
            <div className="text-xs text-muted-foreground mb-1">Active Trips</div>
            <div className="text-2xl font-bold">{costControl.active_trips}</div>
          </div>
          <div className="p-4 rounded-xl border border-destructive/20 bg-destructive/5">
            <div className="text-xs text-destructive mb-1">At-Risk Trips</div>
            <div className="text-2xl font-bold text-destructive">{costControl.at_risk_trips}</div>
          </div>
          <div className="p-4 rounded-xl border border-destructive/20 bg-destructive/5">
            <div className="text-xs text-destructive mb-1">Potential Cost Impact</div>
            <div className="text-2xl font-bold text-destructive">+${costControl.potential_cost_impact.toLocaleString()}</div>
          </div>
          <div className="p-4 rounded-xl border border-primary/20 bg-primary/5">
            <div className="text-xs text-primary mb-1">Potential Avoided Cost</div>
            <div className="text-2xl font-bold text-primary">${costControl.potential_avoided_cost.toLocaleString()}</div>
          </div>
          <div className="p-4 rounded-xl border border-white/5 bg-black/40">
            <div className="text-xs text-muted-foreground mb-1">Requires Approval</div>
            <div className="text-2xl font-bold">{costControl.trips_requiring_approval}</div>
          </div>
        </div>
      )}

      {/* COST AT RISK TABLE */}
      {costControl && costControl.cost_at_risk.length > 0 && (
        <div>
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-destructive" /> Cost At Risk
          </h2>
          <div className="border border-white/10 rounded-xl overflow-hidden bg-black/40">
            <table className="w-full text-sm text-left">
              <thead className="bg-white/5 text-muted-foreground text-xs uppercase">
                <tr>
                  <th className="px-4 py-3">Trip</th>
                  <th className="px-4 py-3">Destination</th>
                  <th className="px-4 py-3">Current Cost</th>
                  <th className="px-4 py-3 text-destructive">Impact</th>
                  <th className="px-4 py-3 text-green-400">Optimized</th>
                  <th className="px-4 py-3 text-primary">Avoided Cost</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {costControl.cost_at_risk.map((risk: any, idx: number) => (
                  <tr key={idx} className="hover:bg-white/5 transition-colors">
                    <td className="px-4 py-3 font-medium">{risk.traveler_name}</td>
                    <td className="px-4 py-3 text-muted-foreground">{risk.destination}</td>
                    <td className="px-4 py-3">${risk.current_cost.toLocaleString()}</td>
                    <td className="px-4 py-3 text-destructive font-bold">+${risk.potential_impact.toLocaleString()}</td>
                    <td className="px-4 py-3 text-green-400">${risk.optimized_cost.toLocaleString()}</td>
                    <td className="px-4 py-3 text-primary font-bold">${risk.potential_avoided_cost.toLocaleString()}</td>
                    <td className="px-4 py-3">
                      <Badge variant="outline" className={risk.status === 'DETECTED' ? 'border-destructive/50 text-destructive' : 'border-primary/50 text-primary'}>
                        {risk.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <Button size="sm" variant="outline" onClick={() => window.location.href = `/trips/${risk.trip_id}/plan`}>
                        Review <ArrowRight className="w-3 h-3 ml-1" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* DISRUPTIONS */}
      {disruptions.length > 0 && (
        <div className="mt-8">
           <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><Activity className="w-5 h-5 text-muted-foreground" /> Active Disruptions</h2>
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
