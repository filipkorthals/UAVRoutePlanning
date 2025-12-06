"use client";
import GoogleMapComponent from "@/components/google-map-component";
import UAVTitle from "@/components/uav-title";
import FormComponent from "@/components/form-component";
import { useState } from "react";
import Footer from "@/components/footer";
import ContentLayout from "@/components/content-layout";
import Marker from "@/types/marker";
import Modal from "@/components/modal";

const Home = () => {
  const [markers, setMarkers] = useState<Marker[]>([]);
  const [currentCenter, setCurrentCenter] =
    useState<google.maps.LatLngLiteral | null>(null);
  // display jest tymaczasowo do wyświetlenia wyniku planowania
  const [displayModal, setDisplayModal] = useState<boolean>(false);

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

  // TODO: naprawić port
  async function sendWaypoints() {
    let response = await fetch("http://127.0.0.1:5001/area_detection", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(markers),
    });
    const data = await response.json();
    setDisplayModal(data.imgHtml !== "" ? true : false);
  }

  return (
    <ContentLayout>
      <GoogleMapComponent
        onCenterChange={setCurrentCenter}
        markers={markers}
        setMarkers={setMarkers}
      />
      <div className="flex flex-col w-1/3 h-full p-10">
        <UAVTitle />
        <FormComponent
          onAddMarker={handleAddMarker}
          resetMarkers={resetMarkers}
          sendWaypoints={sendWaypoints}
        />
        <Footer />
      </div>

      <Modal display={displayModal} setDisplay={setDisplayModal} />
    </ContentLayout>
  );
};

export default Home;
