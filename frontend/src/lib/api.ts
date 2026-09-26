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

export async function generateItinerary(tripId: number) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/itinerary/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) throw new Error("Failed to generate itinerary");
  return res.json();
}

export async function fetchActiveItinerary(tripId: number) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/itinerary`, { cache: 'no-store' });
  if (!res.ok) {
    if (res.status === 404) return null;
    throw new Error("Failed to fetch active itinerary");
  }
  return res.json();
}

export async function fetchItineraryExplanation(tripId: number) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/itinerary/explanation`, { cache: 'no-store' });
  if (!res.ok) {
    if (res.status === 404) return null;
    throw new Error("Failed to fetch explanation");
  }
  return res.json();
}

export async function optimizeBudget(tripId: number, payload: any) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/budget/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Failed to optimize budget");
  return res.json();
}

export async function applyOptimizedScenario(tripId: number, payload: any) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/itinerary/apply-scenario`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Failed to apply scenario");
  return res.json();
}

export async function getLiveTripStatus(tripId: number) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/live`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}
export async function sendMessageToAssistant(tripId: number, message: string) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/assistant`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}

export async function getBookableItems(tripId: number) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/bookable-items`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}
export async function checkAvailability(tripId: number, itemId: number, estimatedCost: number) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/bookings/check-availability`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ itinerary_item_id: itemId, estimated_cost: estimatedCost })
  });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}
export async function createBooking(tripId: number, itemId: number, estimatedCost: number) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/bookings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ itinerary_item_id: itemId, estimated_cost: estimatedCost })
  });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}
export async function getBookings(tripId: number) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/bookings`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}
export async function getPreparation(tripId: number) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/preparation`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}
