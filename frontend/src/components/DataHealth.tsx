"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { RefreshCw, Activity, Database, AlertCircle, Wifi, Clock, CheckCircle2, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface DataSource {
  id: number;
  provider_name: string;
  provider_type: string;
  mode: string;
  status: string;
  freshness_status: string;
  last_successful_sync: string | null;
  last_attempted_sync: string | null;
  records_received: number;
  records_inserted: number;
  records_updated: number;
  records_rejected: number;
  stale_record_count: number;
  error_count: number;
  enabled: boolean;
}

interface IngestionRun {
  run_id: string;
  provider: string;
  dataset_type: string;
  started_at: string;
  completed_at: string;
  duration: number;
  status: string;
  records_received: number;
  records_inserted: number;
  records_rejected: number;
  error_message: string;
}

export function DataHealth() {
  const [sources, setSources] = useState<DataSource[]>([]);
  const [runs, setRuns] = useState<IngestionRun[]>([]);
  const [healthData, setHealthData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [env, setEnv] = useState("DEMO");

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/ingestion/health?env=${env}`);
      if (res.ok) {
        const data = await res.json();
        setHealthData(data);
        setSources(data.sources);
      }
      
      const runsRes = await fetch(`http://localhost:8000/api/v1/ingestion/runs`);
      if (runsRes.ok) {
        const runsData = await runsRes.json();
        setRuns(runsData);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchStatus();
  }, [env]);

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

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "HEALTHY": return <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20">HEALTHY</Badge>;
      case "DEGRADED": return <Badge variant="outline" className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20">DEGRADED</Badge>;
      case "STALE": return <Badge variant="outline" className="bg-orange-500/10 text-orange-500 border-orange-500/20">STALE</Badge>;
      case "ERROR": return <Badge variant="outline" className="bg-red-500/10 text-red-500 border-red-500/20">ERROR</Badge>;
      default: return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getFreshnessBadge = (status: string) => {
    if (status === "FRESH") return <span className="text-green-400 font-medium">FRESH</span>;
    if (status === "STALE") return <span className="text-orange-400 font-medium">STALE</span>;
    return <span className="text-muted-foreground">{status}</span>;
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Database className="w-5 h-5 text-primary" />
          Data Health Center
        </h2>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center border border-white/10 rounded-md overflow-hidden bg-black/50">
            <button onClick={() => setEnv("DEMO")} className={`px-3 py-1 text-xs font-medium ${env === "DEMO" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-white"}`}>DEMO</button>
            <button onClick={() => setEnv("TEST")} className={`px-3 py-1 text-xs font-medium ${env === "TEST" ? "bg-amber-500 text-black" : "text-muted-foreground hover:text-white"}`}>TEST</button>
            <button onClick={() => setEnv("LIVE")} className={`px-3 py-1 text-xs font-medium ${env === "LIVE" ? "bg-green-500 text-black" : "text-muted-foreground hover:text-white"}`}>LIVE</button>
          </div>
          <Button variant="outline" size="sm" onClick={fetchStatus} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {healthData && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl border border-white/5 bg-black/40">
            <div className="text-xs text-muted-foreground uppercase mb-1">Providers Healthy</div>
            <div className="text-2xl font-bold text-green-400">{healthData.providers_healthy}</div>
          </div>
          <div className="p-4 rounded-xl border border-white/5 bg-black/40">
            <div className="text-xs text-muted-foreground uppercase mb-1">Providers Degraded</div>
            <div className="text-2xl font-bold text-yellow-500">{healthData.providers_degraded}</div>
          </div>
          <div className="p-4 rounded-xl border border-white/5 bg-black/40">
            <div className="text-xs text-muted-foreground uppercase mb-1">Total Sources</div>
            <div className="text-2xl font-bold text-primary">{sources.length}</div>
          </div>
        </div>
      )}

      <div className="flex gap-2 mb-4">
        <Button variant="secondary" size="sm" onClick={() => triggerSync("flights")}>Sync Flights</Button>
        <Button variant="secondary" size="sm" onClick={() => triggerSync("weather")}>Sync Weather</Button>
      </div>

      <div className="rounded-xl border border-white/5 bg-black/20 overflow-hidden">
        <table className="w-full text-sm text-left">
          <thead className="text-xs uppercase bg-white/5 text-muted-foreground">
            <tr>
              <th className="px-6 py-3 font-medium">Provider</th>
              <th className="px-6 py-3 font-medium">Status</th>
              <th className="px-6 py-3 font-medium">Last Sync</th>
              <th className="px-6 py-3 font-medium">Freshness</th>
              <th className="px-6 py-3 font-medium text-right">Records</th>
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
                    {s.provider_name} <span className="text-muted-foreground text-xs font-normal">({s.provider_type})</span>
                  </td>
                  <td className="px-6 py-4">{getStatusBadge(s.status)}</td>
                  <td className="px-6 py-4 text-xs text-muted-foreground">
                    {s.last_successful_sync ? new Date(s.last_successful_sync).toLocaleTimeString() : 'Never'}
                  </td>
                  <td className="px-6 py-4 text-xs">
                    {getFreshnessBadge(s.freshness_status)}
                  </td>
                  <td className="px-6 py-4 font-mono text-right">{s.records_inserted}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Ingestion Timeline */}
      {runs.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-bold flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-muted-foreground" /> 
            Ingestion Activity Timeline
          </h3>
          <div className="space-y-4 pl-4 border-l-2 border-white/10">
            {runs.map(run => (
              <div key={run.run_id} className="relative pl-6">
                <div className={`absolute -left-[31px] top-1 w-3 h-3 rounded-full border-2 border-background ${run.status === 'SUCCESS' ? 'bg-green-500' : run.status === 'PARTIAL' ? 'bg-yellow-500' : 'bg-red-500'}`} />
                <div className="bg-black/40 border border-white/5 p-4 rounded-xl">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2 font-bold">
                      {run.provider} {run.dataset_type} sync
                      {run.status === 'SUCCESS' && <CheckCircle2 className="w-4 h-4 text-green-500" />}
                      {run.status === 'FAILED' && <XCircle className="w-4 h-4 text-red-500" />}
                    </div>
                    <div className="text-xs text-muted-foreground flex items-center gap-1">
                      <Clock className="w-3 h-3" /> {new Date(run.started_at).toLocaleTimeString()}
                    </div>
                  </div>
                  <div className="text-sm space-y-1 text-muted-foreground">
                    <div>{run.records_received} records received</div>
                    {run.records_inserted > 0 && <div className="text-green-400">{run.records_inserted} records accepted</div>}
                    {run.records_rejected > 0 && <div className="text-red-400">{run.records_rejected} records rejected</div>}
                    {run.status === 'SUCCESS' && <div>Sync completed in {run.duration.toFixed(2)}s</div>}
                    {run.status === 'FAILED' && <div className="text-red-500 mt-2">Error: {run.error_message}</div>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
