export default function OperatorDashboard() {
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
          <p className="text-3xl font-bold text-destructive">3</p>
        </div>
        <div className="h-32 rounded-xl border border-white/5 glass flex flex-col justify-center px-6">
          <p className="text-sm text-muted-foreground font-medium mb-1">Pending Approvals</p>
          <p className="text-3xl font-bold text-primary">5</p>
        </div>
      </div>
      
      <div className="h-96 rounded-xl border border-white/5 glass flex items-center justify-center">
        <p className="text-muted-foreground">Dashboard map & alerts coming soon.</p>
      </div>
    </div>
  );
}
