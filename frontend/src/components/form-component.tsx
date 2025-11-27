import RangeInput from "./range-input";
import ToggleSwitch from "./toggle-switch";

const FormComponent = ({
  onAddMarker,
  resetMarkers,
  sendWaypoints,
}: {
  onAddMarker: () => void;
  resetMarkers: () => void;
  sendWaypoints: () => void;
}) => {
  return (
    <div className="h-full content-center">
      <div>
        <div className="flex flex-row place-content-between w-2/3">
          <h6>Max time</h6>
          <h6>(max 40 min)</h6>
        </div>
        <RangeInput />
        <h6 className="text-primary-light">The maximal time of flight</h6>
      </div>
      <div className="mt-5">
        <div className="flex flex-row place-content-between w-2/3">
          <h6>Velocity</h6>
          <h6>(max 70 km/h)</h6>
        </div>
        <RangeInput />
        <h6 className="text-primary-light">Flight velocity of the UAV</h6>
      </div>
      <div className="grid mt-5 grid-flow-col content-center justify-start">
        <ToggleSwitch />
        <h6 className="inline content-center ml-4">Show selected field</h6>
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
      >
        Clear path
      </button>
    </div>
  );
};

export default FormComponent;
