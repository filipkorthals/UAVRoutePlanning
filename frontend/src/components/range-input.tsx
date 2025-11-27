const RangeInput = () => {
  return (
    <input
      type="range"
      id="vol"
      name="vol"
      min="0"
      max="50"
      className="block w-2/3 accent-primary mt-2 mb-2"
    />
  );
};

export default RangeInput;
