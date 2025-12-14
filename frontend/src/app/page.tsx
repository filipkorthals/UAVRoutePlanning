"use client";
import GoogleMapComponent from "@/components/google-map-component";
import UAVTitle from "@/components/uav-title";
import FormComponent from "@/components/form-component";
import { useState } from "react";
import Footer from "@/components/footer";
import ContentLayout from "@/components/content-layout";
import Marker from "@/types/marker";
import Modal from "@/components/modal";
import { minTime, minVel } from "@/utils/form-values";
import { sortMarkersClockwise } from "@/utils/geometry";
import { sendWaypoints } from "@/services/route-planner";

const Home = () => {
  const [markers, setMarkers] = useState<Marker[]>([]);
  const [currentCenter, setCurrentCenter] =
    useState<google.maps.LatLngLiteral | null>(null);
  const [showMarkers, setShowMarkers] = useState(true);
  const [time, setTime] = useState(minTime);
  const [velocity, setVelocity] = useState(minVel);

  const [plannedPath, setPlannedPath] = useState<google.maps.LatLngLiteral[]>(
    []
  );
  const [detectedArea, setDetectedArea] = useState<google.maps.LatLngLiteral[]>(
    []
  );

  const [isLoading, setIsLoading] = useState(false);

  async function handleSendWaypoints() {
    if (markers.length < 3) {
      alert("Minimum 3 waypoints required.");
      return;
    }

    setIsLoading(true);
    try {
      const data = await sendWaypoints(markers, time, velocity);

      if (data.path) {
        setPlannedPath(data.path);
      }

      if (data.area) {
        setDetectedArea(data.area);
      }

      setMarkers(sortMarkersClockwise(markers));
    } catch (error) {
      alert("Error occured.");
    } finally {
      setIsLoading(false);
    }
  }

  const handleAddMarker = () => {
    if (!currentCenter) return;
    setMarkers((prev) => [
      ...prev,
      { id: Date.now(), position: currentCenter },
    ]);
  };
  const resetMarkers = () => {
    setMarkers([]);
  };
  const resetPath = () => {
    setPlannedPath([]);
    setDetectedArea([]);
  };

  return (
    <ContentLayout>
      <GoogleMapComponent
        onCenterChange={setCurrentCenter}
        markers={markers}
        setMarkers={setMarkers}
        showMarkers={showMarkers}
        plannedPath={plannedPath}
        detectedArea={detectedArea}
      />
      <div className="flex flex-col w-1/3 h-full p-10">
        <UAVTitle />
        <FormComponent
          showMarkers={showMarkers}
          setShowMarkers={setShowMarkers}
          onAddMarker={handleAddMarker}
          resetMarkers={resetMarkers}
          resetPath={resetPath}
          sendWaypoints={handleSendWaypoints}
          time={time}
          setTime={setTime}
          velocity={velocity}
          setVelocity={setVelocity}
        />
        <Footer />
      </div>

      <Modal display={isLoading} />
    </ContentLayout>
  );
};

export default Home;
