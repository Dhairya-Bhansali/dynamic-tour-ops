import Link from "next/link";
import { fetchTrips } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPin, Calendar, CreditCard, CheckCircle2, Navigation } from "lucide-react";
import dayjs from "dayjs";

export const dynamic = "force-dynamic";

export default async function MyTripsPage() {
  let trips = [];
  try {
    const res = await fetch("http://localhost:8000/api/v1/trips", { cache: "no-store" });
    if (res.ok) {
      trips = await res.json();
    }
  } catch (err) {
    console.error("Failed to load trips", err);
  }

  if (trips.length === 0) {
    return (
      <div className="min-h-screen bg-black/95 text-white flex items-center justify-center p-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">No trips found</h2>
          <p className="text-muted-foreground mb-6">Start planning your next adventure.</p>
          <Link href="/discover" className="bg-primary px-6 py-3 rounded-full font-medium">Discover Destinations</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black/95 text-white pt-24 pb-12 px-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">My Trips</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {trips.map((trip: any) => (
            <Link href={`/trips/${trip.id}/plan`} key={trip.id}>
              <Card className="glass-card border-white/10 hover:border-primary/50 transition-colors h-full">
                <CardHeader className="bg-white/5 border-b border-white/10 p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-primary" /> {trip.title || "Destination"}
                      </CardTitle>
                      <div className="text-sm text-muted-foreground mt-1 flex items-center gap-2">
                        <Calendar className="w-3.5 h-3.5" /> 
                        {trip.start_date ? dayjs(trip.start_date).format("MMM D") : "TBD"} - 
                        {trip.end_date ? dayjs(trip.end_date).format("MMM D, YYYY") : "TBD"}
                      </div>
                    </div>
                    <Badge variant={trip.status === "ACTIVE" ? "default" : "secondary"}>
                      {trip.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="p-4 space-y-4 text-sm">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-muted-foreground mb-1 flex items-center gap-1"><CreditCard className="w-3.5 h-3.5"/> Budget</div>
                      <div className="font-medium">${trip.budget || 0}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground mb-1 flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5"/> Status</div>
                      <div className="font-medium">{trip.status || "Draft"}</div>
                    </div>
                  </div>
                  <div className="pt-4 border-t border-white/10 flex justify-between items-center text-primary font-medium group-hover:translate-x-1 transition-transform">
                    View Itinerary <Navigation className="w-4 h-4" />
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
