"use client";

import Link from "next/link";
import { useParams, usePathname } from "next/navigation";
import { Compass, Briefcase, Fingerprint, Calendar, Navigation, Bot, User, Menu, X } from "lucide-react";
import { useState } from "react";

export function TravelerShell({ children }: { children: React.ReactNode }) {
  const params = useParams();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // Extract tripId if present
  const tripId = params?.id as string | undefined;

  const navItems = [
    { label: "Discover", href: "/discover", icon: Compass },
    { label: "My Trips", href: "/trips", icon: Briefcase },
    { label: "Travel DNA", href: "/personalize", icon: Fingerprint },
    { 
      label: "Bookings", 
      href: tripId ? `/trips/${tripId}/book` : "/trips", 
      icon: Calendar 
    },
    { 
      label: "Live Trip", 
      href: tripId ? `/trips/${tripId}/plan` : "/trips", 
      icon: Navigation 
    },
    { 
      label: "Assistant", 
      href: tripId ? `/trips/${tripId}/assist` : "/trips", 
      icon: Bot 
    },
  ];

  const NavLinks = () => (
    <>
      {navItems.map((item) => {
        const isActive = pathname?.startsWith(item.href) && item.href !== "/trips";
        return (
          <Link
            key={item.label}
            href={item.href}
            onClick={() => setMobileMenuOpen(false)}
            className={`text-sm font-medium transition-colors flex items-center gap-2 px-3 py-2 md:p-0 rounded-md md:bg-transparent ${
              isActive 
                ? "text-primary bg-primary/10 md:bg-transparent" 
                : "text-muted-foreground hover:text-primary hover:bg-white/5 md:hover:bg-transparent"
            }`}
          >
            <item.icon className="w-4 h-4" />
            {item.label}
          </Link>
        )
      })}
    </>
  );

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Top Navigation */}
      <header className="h-16 border-b border-border bg-card/50 backdrop-blur-md sticky top-0 z-40 flex items-center px-6 justify-between">
        <div className="flex items-center gap-4 md:gap-8">
          <button 
            className="md:hidden text-white p-1 -ml-1 rounded-md hover:bg-white/10"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
          
          <Link href="/" className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-400">
            NexTour
          </Link>
          
          <nav className="hidden md:flex items-center gap-6">
            <NavLinks />
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/profile" className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary hover:bg-primary/30 transition-colors">
            <User className="w-4 h-4" />
          </Link>
        </div>
      </header>
      
      {/* Mobile Navigation Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-border bg-black/95 backdrop-blur-xl absolute top-16 left-0 right-0 z-40 px-4 py-4 flex flex-col gap-2 shadow-2xl">
          <NavLinks />
        </div>
      )}
      
      <main className="flex-1 relative z-0">
        {children}
      </main>
    </div>
  );
}
