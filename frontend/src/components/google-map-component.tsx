import { APIProvider } from "@vis.gl/react-google-maps";
import GoogleMapInner from "./google-map-inner";
import Marker from "@/types/marker";

const GoogleMapComponent = ({
  onCenterChange,
  markers,
  setMarkers,
}: {
  onCenterChange: (center: google.maps.LatLngLiteral) => void;
  markers: Marker[];
  setMarkers: React.Dispatch<React.SetStateAction<Marker[]>>;
}) => {
  return (
    <div className="w-2/3">
      <APIProvider
        apiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY!}
        onLoad={() => console.log("Maps API has loaded.")}
      >
        <GoogleMapInner
          onCenterChange={onCenterChange}
          markers={markers}
          setMarkers={setMarkers}
        />
      </APIProvider>
    </div>
  );
};

export default GoogleMapComponent;
