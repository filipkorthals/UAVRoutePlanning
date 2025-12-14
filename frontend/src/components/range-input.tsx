const RangeInput = ({
  minVal,
  maxVal,
  value,
  setValue,
}: {
  minVal: number;
  maxVal: number;
  value: number;
  setValue: (e: number) => void;
}) => {
  return (
    <input
      type="range"
      min={minVal}
      max={maxVal}
      value={value}
      onChange={(e) => setValue(e.target.valueAsNumber)}
      className="block w-2/3 accent-primary mt-2 mb-2"
    />
  );
};

export default RangeInput;
