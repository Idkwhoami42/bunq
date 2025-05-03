"use client";

import { useState, useEffect, useRef } from "react";
import { Search, Loader2, MapPin } from "lucide-react";
import { Input } from "~/components/ui/input";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandList,
} from "~/components/ui/command";
import { Alert, AlertDescription } from "~/components/ui/alert";

interface PlaceSuggestion {
  place_id: string;
  description: string;
}

interface PlaceLocation {
  lat: number;
  lng: number;
}

interface PlaceGeometry {
  location: PlaceLocation;
}

interface PlaceDetails {
  formatted_address?: string;
  geometry?: PlaceGeometry;
}

interface SelectedPlace {
  description: string;
  details: PlaceDetails | null;
}

interface PlacesAutocompleteProps {
  onPlaceSelect: (place: SelectedPlace | null) => void;
}

export default function PlacesAutocomplete({
  onPlaceSelect,
}: PlacesAutocompleteProps) {
  const [query, setQuery] = useState<string>("");
  const [suggestions, setSuggestions] = useState<PlaceSuggestion[]>([]);
  const [selectedPlace, setSelectedPlace] = useState<SelectedPlace | null>(
    null
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState<boolean>(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (query === selectedPlace?.description) return;
    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    if (!query || query.length < 2) {
      setSuggestions([]);
      return;
    }

    // Set a debounce to avoid too many requests
    timeoutRef.current = setTimeout(async () => {
      setLoading(true);
      setError(null);
      setOpen(true);

      try {
        const response = await fetch(
          `http://localhost:3000/places-autocomplete?query=${encodeURIComponent(
            query
          )}`
        );

        if (!response.ok) {
          throw new Error("Failed to fetch suggestions");
        }

        const data = await response.json();
        setSuggestions(data.predictions || []);
      } catch (err) {
        console.error("Error fetching places:", err);
        setError("Failed to load suggestions. Please try again.");
        setSuggestions([]);
      } finally {
        setLoading(false);
      }
    }, 300);

    // Clean up timeout on component unmount
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [query]);

  const handleSelectPlace = async (
    placeId: string,
    description: string
  ): Promise<void> => {
    setOpen(false);

    setLoading(true);
    setError(null);
    setSuggestions([]);

    try {
      const response = await fetch(
        `http://localhost:3000/place-details?placeId=${encodeURIComponent(
          placeId
        )}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch place details");
      }

      const data = await response.json();

      const newSelectedPlace = {
        description,
        details: data.result,
      };

      setSelectedPlace(newSelectedPlace);
      onPlaceSelect(newSelectedPlace);
      setQuery(description);
      setOpen(false);
    } catch (err) {
      console.error("Error fetching place details:", err);
      setError("Failed to load place details. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto relative">
      <div className="relative">
        <div className="relative">
          <Input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for a location"
            onFocus={() => {
              if (suggestions.length > 0) setOpen(true);
            }}
          />
          {loading && (
            <Loader2 className="absolute right-3 top-3 h-4 w-4 animate-spin text-muted-foreground" />
          )}
        </div>
      </div>

      {error && (
        <Alert variant="destructive" className="mt-2">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {open && (suggestions.length > 0 || loading) && (
        <div className="relative mt-1">
          <Command className="rounded-lg border shadow-md">
            <CommandList>
              {loading && suggestions.length === 0 ? (
                <div className="p-4 text-sm text-center text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin mx-auto mb-2" />
                  Loading suggestions...
                </div>
              ) : (
                <>
                  <CommandEmpty>No locations found.</CommandEmpty>
                  <CommandGroup heading="Suggestions">
                    {suggestions.map((suggestion) => (
                      <CommandItem
                        key={suggestion.place_id}
                        onSelect={() =>
                          handleSelectPlace(
                            suggestion.place_id,
                            suggestion.description
                          )
                        }
                        className="flex items-center gap-2 cursor-pointer"
                      >
                        <MapPin className="h-4 w-4 text-muted-foreground" />
                        <span>{suggestion.description}</span>
                      </CommandItem>
                    ))}
                  </CommandGroup>
                </>
              )}
            </CommandList>
          </Command>
        </div>
      )}
    </div>
  );
}
