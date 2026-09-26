import Link from "next/link";
import { Compass, Briefcase, Fingerprint, Calendar, Navigation, Bot, User } from "lucide-react";

export function TravelerShell({ children }: { children: React.ReactNode }) {
  const navItems = [
    { label: "Discover", href: "/discover", icon: Compass },
    { label: "My Trips", href: "/trips", icon: Briefcase },
    { label: "Travel DNA", href: "/dna", icon: Fingerprint },
    { label: "Bookings", href: "/bookings", icon: Calendar },
    { label: "Live Trip", href: "/live", icon: Navigation },
    { label: "Assistant", href: "/assistant", icon: Bot },
  ];

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Top Navigation */}
      <header className="h-16 border-b border-border bg-card/50 backdrop-blur-md sticky top-0 z-40 flex items-center px-6 justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-400">
            NexTour
          </Link>
          <nav className="hidden md:flex items-center gap-6">
            {navItems.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors flex items-center gap-2"
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/profile" className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary hover:bg-primary/30 transition-colors">
            <User className="w-4 h-4" />
          </Link>
        </div>
      </header>
      
      <main className="flex-1">
        {children}
      </main>
    </div>
  );
}
