"use client";
import {
  Map,
  MapControl,
  ControlPosition,
  AdvancedMarker,
  Pin,
  useMap,
  MapCameraChangedEvent,
} from "@vis.gl/react-google-maps";
import { AutocompleteWebComponent } from "./autocomplete-webcomponent";
import Marker from "@/types/marker";
import Polyline from "./polyline";
import Polygon from "./polygon";

const containerStyle = {
  width: "100%",
  height: "100vh",
};

// Gdansk
const defaultCenter = {
  lat: 54.352024,
  lng: 18.646639,
};

const GoogleMapInner = ({
  onCenterChange,
  markers,
  setMarkers,
  showMarkers,
  plannedPath,
  detectedArea,
}: {
  onCenterChange: (center: google.maps.LatLngLiteral) => void;
  markers: Marker[];
  setMarkers: React.Dispatch<React.SetStateAction<Marker[]>>;
  showMarkers: boolean;
  plannedPath?: google.maps.LatLngLiteral[];
  detectedArea?: google.maps.LatLngLiteral[];
}) => {
  const map = useMap();

  const handleNewCenter = (place: google.maps.places.Place | null) => {
    if (place == null || place == undefined) return;
    map?.setCenter(place.location!);
  };

  const handleMarkerDrag = (
    id: number,
    position: google.maps.LatLngLiteral
  ) => {
    setMarkers((prev) =>
      prev.map((marker) =>
        marker.id == id ? { ...marker, position: position } : marker
      )
    );
  };

  return (
    <Map
      defaultZoom={13}
      defaultCenter={defaultCenter}
      mapId="DEMO_MAP_ID"
      style={containerStyle}
      mapTypeId={"hybrid"}
      onCameraChanged={(ev: MapCameraChangedEvent) =>
        onCenterChange(ev.detail.center)
      }
    >
      {detectedArea && detectedArea.length > 0 && (
        <Polygon
          paths={detectedArea}
          strokeColor={"#FFF"}
          strokeOpacity={0.8}
          strokeWeight={2}
          fillColor={"#FFF"}
          fillOpacity={0.35}
          zIndex={1}
        />
      )}

      {detectedArea && detectedArea.length > 0 && (
        <Polygon
          paths={markers.map((m) => m.position)}
          strokeColor={"#F00"}
          strokeOpacity={0.8}
          strokeWeight={2}
          fillColor={"#F00"}
          fillOpacity={0.35}
          zIndex={2}
        />
      )}

      {plannedPath && plannedPath.length > 0 && (
        <Polyline
          path={plannedPath}
          strokeColor={"#000"}
          strokeOpacity={1.0}
          strokeWeight={10}
          zIndex={3}
        />
      )}

      {showMarkers &&
        markers.map((marker) => (
          <AdvancedMarker
            key={marker.id}
            position={marker.position}
            draggable={true}
            onDragEnd={(e) =>
              e.latLng &&
              handleMarkerDrag(marker.id, {
                lat: e.latLng.lat(),
                lng: e.latLng.lng(),
              })
            }
          >
            <Pin
              background={"oklch(39.6% 0.141 25.723)"}
              glyphColor={"oklch(0.268 0.01 67.558)"}
              borderColor={"oklch(39.6% 0.141 25.723)"}
            />
          </AdvancedMarker>
        ))}

      <MapControl position={ControlPosition.TOP_LEFT}>
        <div className="mt-2">
          <AutocompleteWebComponent onPlaceSelect={handleNewCenter} />
        </div>
      </MapControl>
    </Map>
  );
};

export default GoogleMapInner;
