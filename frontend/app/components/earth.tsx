import { useEffect, useRef } from "react";
import { bruh } from "~/config";

interface GoogleEarthViewerProps {
  lat: number;
  lng: number;
  label: string;
}

const GoogleEarthViewer = ({ lat, lng, label }: GoogleEarthViewerProps) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const labelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const initializeMap = async () => {
      // @ts-ignore
      const { Map } = await window.google.maps.importLibrary("maps");
      // @ts-ignore
      const { AdvancedMarkerElement } = await window.google.maps.importLibrary(
        "marker"
      );

      const map = new Map(mapRef.current, {
        center: { lat, lng },
        zoom: 3,
        heading: 0,
        tilt: 67.5,
        mapTypeId: "satellite",
        mapId: "your-map-id", // Replace with your 3D-enabled Map ID
      });

      const zoomToLocation = () => {
        let zoom = 3;
        const interval = setInterval(() => {
          if (zoom < 18) {
            if (zoom < 13) zoom += 0.9;
            else {
              zoom += 0.3;
            }
            map.setZoom(zoom);
          } else {
            clearInterval(interval);
            addMarker();
            if (labelRef.current) {
              labelRef.current.classList.remove("opacity-0");
              labelRef.current.classList.add("opacity-100");
            }
          }
        }, 200);
      };

      const addMarker = () => {
        const position = { lat, lng };

        new AdvancedMarkerElement({
          map,
          position,
        });
      };

      zoomToLocation();
    };

    if (!window.google) {
      const script = document.createElement("script");
      script.src = `https://maps.googleapis.com/maps/api/js${bruh}&libraries=maps,marker`;
      script.async = true;
      script.onload = initializeMap;
      document.head.appendChild(script);
    } else {
      initializeMap();
    }
  }, [lat, lng, label]);

  return (
    <div className="relative w-[400px] h-[400px]">
      <div ref={mapRef} className="w-full h-full rounded shadow" />
    </div>
  );
};

export default GoogleEarthViewer;
