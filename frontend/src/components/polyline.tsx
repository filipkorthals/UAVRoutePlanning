import { useEffect, useRef } from "react";
import { useMap, useMapsLibrary } from "@vis.gl/react-google-maps";

type PolylineProps = google.maps.PolylineOptions;

const Polyline = (props: PolylineProps) => {
  const map = useMap();
  const mapsLib = useMapsLibrary("maps");
  const polylineRef = useRef<google.maps.Polyline | null>(null);

  useEffect(() => {
    if (!map || !mapsLib) return;

    const newPolyline = new mapsLib.Polyline();
    newPolyline.setMap(map);
    polylineRef.current = newPolyline;

    return () => {
      newPolyline.setMap(null);
    };
  }, [map, mapsLib]);

  useEffect(() => {
    const polyline = polylineRef.current;
    if (!polyline) return;

    polyline.setOptions(props);
  }, [props, map]);

  return null;
};

export default Polyline;
