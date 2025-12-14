import { useMap, useMapsLibrary } from "@vis.gl/react-google-maps";
import { useEffect, useRef } from "react";

type PolygonProps = google.maps.PolygonOptions;

const Polygon = (props: PolygonProps) => {
  const map = useMap();
  const mapsLib = useMapsLibrary("maps");
  const polygonRef = useRef<google.maps.Polygon | null>(null);

  useEffect(() => {
    if (!map || !mapsLib) return;

    const newPolygon = new mapsLib.Polygon();
    newPolygon.setMap(map);
    polygonRef.current = newPolygon;

    return () => {
      newPolygon.setMap(null);
    };
  }, [map, mapsLib]);

  useEffect(() => {
    const polygon = polygonRef.current;
    if (!polygon) return;

    polygon.setOptions(props);
  }, [props, map]);

  return null;
};

export default Polygon;
