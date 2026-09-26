const API_BASE = "http://localhost:8000/api/v1";

export async function fetchDestinations(search?: string, style?: string) {
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (style && style !== 'All') params.append("style", style);
  
  const res = await fetch(`${API_BASE}/destinations?${params.toString()}`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch destinations");
  return res.json();
}

export async function fetchDestination(id: string) {
  const res = await fetch(`${API_BASE}/destinations/${id}`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch destination");
  return res.json();
}

export async function fetchExperiences(search?: string, category?: string, destId?: string) {
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (category && category !== 'All') params.append("category", category);
  if (destId) params.append("dest_id", destId);

  const res = await fetch(`${API_BASE}/experiences?${params.toString()}`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch experiences");
  return res.json();
}

export async function fetchExperience(id: string) {
  const res = await fetch(`${API_BASE}/experiences/${id}`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch experience");
  return res.json();
}

export async function fetchTravelDNA(travelerId: number) {
  const res = await fetch(`${API_BASE}/travel-dna/${travelerId}`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch Travel DNA");
  return res.json();
}

export async function saveTravelDNA(travelerId: number, dimensions: Record<string, number>) {
  const res = await fetch(`${API_BASE}/travel-dna/${travelerId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dimensions })
  });
  if (!res.ok) throw new Error("Failed to save Travel DNA");
  return res.json();
}

export async function fetchTripPreferences(tripId: number) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/preferences`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch trip preferences");
  return res.json();
}

export async function saveTripPreferences(tripId: number, prefs: any) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/preferences`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(prefs)
  });
  if (!res.ok) throw new Error("Failed to save trip preferences");
  return res.json();
}
