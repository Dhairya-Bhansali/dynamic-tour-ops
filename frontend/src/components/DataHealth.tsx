"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { RefreshCw, Activity, Database, AlertCircle, Wifi } from "lucide-react";
import { Button } from "@/components/ui/button";

interface DataSource {
  id: number;
  provider: string;
  data_type: string;
  environment: string;
  status: string;
  last_success_at: string | null;
  last_failure_at: string | null;
  last_error: string | null;
  records_ingested: number;
  enabled: boolean;
}

export function DataHealth() {
  const [sources, setSources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [env, setEnv] = useState("DEMO");

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/ingestion/status?env=${env}`);
      if (res.ok) {
        const data = await res.json();
        setSources(data);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchStatus();
  }, [env]);

  // Sync test buttons
  const triggerSync = async (type: string) => {
    try {
      if (type === "flights") {
        await fetch(`http://localhost:8000/api/v1/ingestion/sync/flights?origin=JFK&destination=LHR&date=2024-12-01&env=${env}`, { method: 'POST' });
      } else if (type === "weather") {
        await fetch(`http://localhost:8000/api/v1/ingestion/sync/weather?lat=40.71&lng=-74.00&location_name=NYC&env=${env}`, { method: 'POST' });
      }
      fetchStatus();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Database className="w-5 h-5 text-primary" />
          Data Sources Health
        </h2>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center border border-white/10 rounded-md overflow-hidden bg-black/50">
            <button onClick={() => setEnv("DEMO")} className={`px-3 py-1 text-xs font-medium ${env === "DEMO" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-white"}`}>DEMO</button>
            <button onClick={() => setEnv("TEST")} className={`px-3 py-1 text-xs font-medium ${env === "TEST" ? "bg-amber-500 text-black" : "text-muted-foreground hover:text-white"}`}>TEST API</button>
            <button onClick={() => setEnv("LIVE")} className={`px-3 py-1 text-xs font-medium ${env === "LIVE" ? "bg-green-500 text-black" : "text-muted-foreground hover:text-white"}`}>LIVE</button>
          </div>
          <Button variant="outline" size="sm" onClick={fetchStatus} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      <div className="flex gap-2 mb-4">
        <Button variant="secondary" size="sm" onClick={() => triggerSync("flights")}>Trigger Flight Sync</Button>
        <Button variant="secondary" size="sm" onClick={() => triggerSync("weather")}>Trigger Weather Sync</Button>
      </div>

      <div className="rounded-xl border border-white/5 bg-black/20 overflow-hidden">
        <table className="w-full text-sm text-left">
          <thead className="text-xs uppercase bg-white/5 text-muted-foreground">
            <tr>
              <th className="px-6 py-3 font-medium">Provider</th>
              <th className="px-6 py-3 font-medium">Type</th>
              <th className="px-6 py-3 font-medium">Status</th>
              <th className="px-6 py-3 font-medium">Last Success</th>
              <th className="px-6 py-3 font-medium">Records</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {sources.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-muted-foreground">
                  No data sources registered for {env} environment yet. Try triggering a sync.
                </td>
              </tr>
            ) : (
              sources.map(s => (
                <tr key={s.id} className="hover:bg-white/5">
                  <td className="px-6 py-4 font-medium flex items-center gap-2">
                    <Wifi className="w-4 h-4 text-muted-foreground" />
                    {s.provider}
                  </td>
                  <td className="px-6 py-4 capitalize text-muted-foreground">{s.data_type}</td>
                  <td className="px-6 py-4">
                    {s.status === "ACTIVE" ? (
                      <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20">Active</Badge>
                    ) : (
                      <Badge variant="outline" className="bg-red-500/10 text-red-500 border-red-500/20">Error</Badge>
                    )}
                  </td>
                  <td className="px-6 py-4 text-xs text-muted-foreground">
                    {s.last_success_at ? new Date(s.last_success_at).toLocaleString() : 'Never'}
                  </td>
                  <td className="px-6 py-4 font-mono">{s.records_ingested}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
