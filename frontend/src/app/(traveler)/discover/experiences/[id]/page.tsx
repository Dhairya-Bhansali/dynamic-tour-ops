"use client";
import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { fetchExperience } from "@/lib/api";
import { useTripStore } from "@/store/useTripStore";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeft, MapPin, Clock, DollarSign, Plus, Check } from "lucide-react";
import { toast } from "sonner";

export default function ExperienceDetail({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const router = useRouter();
  const [exp, setExp] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  const { addExperience, removeExperience, selectedExperiences } = useTripStore();

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchExperience(unwrappedParams.id);
        setExp(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [unwrappedParams.id]);

  if (loading) return <div className="p-10"><Skeleton className="w-full h-96 rounded-3xl" /></div>;
  if (!exp) return <div className="p-10 text-center">Experience not found.</div>;

  const isSelected = selectedExperiences.some(e => e.id === exp.id);

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-5xl mx-auto px-6 py-12">
        <Button variant="ghost" className="mb-6 -ml-4 text-muted-foreground hover:text-foreground" onClick={() => router.back()}>
          <ArrowLeft className="w-4 h-4 mr-2" /> Back
        </Button>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          {/* Image */}
          <div className="rounded-3xl overflow-hidden border border-white/10 h-[500px]">
            <img src={exp.image} alt={exp.name} className="w-full h-full object-cover" />
          </div>

          {/* Content */}
          <div className="flex flex-col justify-center">
            <div className="inline-block px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4 w-fit border border-primary/20">
              {exp.category}
            </div>
            
            <h1 className="text-4xl font-bold mb-4 leading-tight">{exp.name}</h1>
            
            <div className="flex flex-col gap-3 mb-8 text-muted-foreground">
              <div className="flex items-center gap-3">
                <MapPin className="w-5 h-5 text-primary/70" />
                <span>{exp.location}</span>
              </div>
              <div className="flex items-center gap-3">
                <Clock className="w-5 h-5 text-primary/70" />
                <span>{exp.duration} hours</span>
              </div>
              <div className="flex items-center gap-3">
                <DollarSign className="w-5 h-5 text-primary/70" />
                <span className="font-semibold text-foreground text-xl">${exp.price_estimate}</span>
              </div>
            </div>

            <p className="text-lg leading-relaxed text-foreground/80 mb-10">
              {exp.description}
            </p>

            {isSelected ? (
              <Button size="lg" variant="outline" className="w-full md:w-auto h-14 rounded-xl border-destructive/50 text-destructive hover:bg-destructive/10" onClick={() => {
                removeExperience(exp.id);
                toast("Removed from your trip plan.");
              }}>
                Remove from Trip
              </Button>
            ) : (
              <Button size="lg" className="w-full md:w-auto h-14 rounded-xl shadow-[0_0_20px_rgba(168,85,247,0.25)]" onClick={() => {
                addExperience(exp);
                toast.success("Added to your trip plan!");
              }}>
                <Plus className="w-5 h-5 mr-2" /> Add to My Trip
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
