import { useState } from "react";
import RangeInput from "./range-input";
import ToggleSwitch from "./toggle-switch";
import { maxTime, maxVel, minTime, minVel } from "@/utils/form-values";

const FormComponent = ({
  showMarkers,
  setShowMarkers,
  onAddMarker,
  resetMarkers,
  resetPath,
  sendWaypoints,
  time,
  setTime,
  velocity,
  setVelocity,
}: {
  showMarkers: boolean;
  setShowMarkers: (value: boolean) => void;
  onAddMarker: () => void;
  resetMarkers: () => void;
  resetPath: () => void;
  sendWaypoints: () => void;
  time: number;
  setTime: (value: number) => void;
  velocity: number;
  setVelocity: (value: number) => void;
}) => {
  return (
    <div className="h-full content-center">
      <div>
        <div className="flex flex-row place-content-between w-2/3">
          <h6>Max time</h6>
          <h6>{time} min</h6>
        </div>
        <RangeInput
          minVal={minTime}
          maxVal={maxTime}
          value={time}
          setValue={setTime}
        />
        <h6 className="text-primary-light">The maximal time of flight</h6>
      </div>
      <div className="mt-5">
        <div className="flex flex-row place-content-between w-2/3">
          <h6>Velocity</h6>
          <h6>{velocity} km/h</h6>
        </div>
        <RangeInput
          minVal={minVel}
          maxVal={maxVel}
          value={velocity}
          setValue={setVelocity}
        />
        <h6 className="text-primary-light">Flight velocity of the UAV</h6>
      </div>
      <div className="grid mt-5 grid-flow-col content-center justify-start">
        <ToggleSwitch isChecked={showMarkers} setIsChecked={setShowMarkers} />
        <h6 className="inline content-center ml-4">Show waypoints</h6>
      </div>
      <button
        type="button"
        className="block py-2 px-4 bg-primary text-white rounded-lg mt-5"
        onClick={onAddMarker}
      >
        Add waypoint
      </button>
      <button
        type="button"
        className="block py-2 px-4 bg-primary text-white rounded-lg mt-5"
        onClick={sendWaypoints}
      >
        Generate path
      </button>
      <button
        type="button"
        className="block py-2 px-4 bg-secondary text-white rounded-lg mt-5"
        onClick={resetMarkers}
      >
        Clear waypoints
      </button>
      <button
        type="button"
        className="block py-2 px-4 bg-secondary text-white rounded-lg mt-5"
        onClick={resetPath}
      >
        Clear path
      </button>
    </div>
  );
};

export default FormComponent;
