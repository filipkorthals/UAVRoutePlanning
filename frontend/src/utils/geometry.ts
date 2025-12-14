import Marker from "@/types/marker";

export const sortMarkersClockwise = (markers: Marker[]): Marker[] => {
  if (markers.length < 3) return markers;

  const center = markers.reduce(
    (acc, marker) => {
      return {
        lat: acc.lat + marker.position.lat,
        lng: acc.lng + marker.position.lng,
      };
    },
    { lat: 0, lng: 0 }
  );

  center.lat /= markers.length;
  center.lng /= markers.length;

  return [...markers].sort((a, b) => {
    const angleA = Math.atan2(
      a.position.lat - center.lat,
      a.position.lng - center.lng
    );
    const angleB = Math.atan2(
      b.position.lat - center.lat,
      b.position.lng - center.lng
    );

    return angleA - angleB;
  });
};
