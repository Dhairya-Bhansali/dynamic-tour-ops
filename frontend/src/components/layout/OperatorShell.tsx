import Link from "next/link";
import { 
  TowerControl, Map, Users, Calendar, Store, Building, 
  Bus, Activity, Users2, Bell, BrainCircuit, BarChart3, Settings
} from "lucide-react";

export function OperatorShell({ children }: { children: React.ReactNode }) {
  const sidebarItems = [
    { label: "Control Tower", href: "/operator", icon: TowerControl },
    { label: "Tours", href: "/operator/tours", icon: Map },
    { label: "Travelers", href: "/operator/travelers", icon: Users },
    { label: "Bookings", href: "/operator/bookings", icon: Calendar },
    { label: "Vendors", href: "/operator/vendors", icon: Store },
    { label: "Hotels", href: "/operator/hotels", icon: Building },
    { label: "Transportation", href: "/operator/transportation", icon: Bus },
    { label: "Activities", href: "/operator/activities", icon: Activity },
    { label: "Groups", href: "/operator/groups", icon: Users2 },
    { label: "Alerts", href: "/operator/alerts", icon: Bell },
    { label: "AI Resolution Center", href: "/operator/resolution", icon: BrainCircuit },
    { label: "Analytics", href: "/operator/analytics", icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-card/30 flex flex-col hidden md:flex sticky top-0 h-screen">
        <div className="h-16 flex items-center px-6 border-b border-border">
          <Link href="/operator" className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <TowerControl className="w-5 h-5 text-primary" />
            Operator Ops
          </Link>
        </div>
        
        <div className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {sidebarItems.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-white/5 transition-colors"
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </Link>
          ))}
        </div>
        
        <div className="p-4 border-t border-border">
          <button className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-white/5 w-full transition-colors">
            <Settings className="w-4 h-4" />
            Settings
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 flex flex-col min-h-screen">
        <header className="h-16 border-b border-border bg-background/50 backdrop-blur-md sticky top-0 z-40 flex items-center justify-end px-6 md:hidden">
          <Link href="/" className="font-bold">Operator Ops</Link>
        </header>
        <div className="flex-1 p-6 overflow-x-hidden">
          {children}
        </div>
      </main>
    </div>
  );
}
