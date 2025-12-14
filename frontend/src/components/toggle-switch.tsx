"use client";

import clsx from "clsx";
import { useState } from "react";

const ToggleSwitch = ({
  isChecked,
  setIsChecked,
}: {
  isChecked: boolean;
  setIsChecked: (value: boolean) => void;
}) => {
  const customCheckbox = clsx(
    "absolute cursor-pointer w-full h-full rounded-full before:content-[] before:absolute before:h-6 before:w-6 before:rounded-full before:bg-white before:left-1 before:top-1 before:duration-200 duration-200",
    {
      "bg-neutral-300": !isChecked,
      "bg-primary before:translate-x-4": isChecked,
    }
  );

  function handleChange() {
    setIsChecked(!isChecked);
  }

  return (
    <label className="relative inline-block w-12 h-8">
      <input
        type="checkbox"
        className="w-0 h-0 opacity-0"
        checked={isChecked}
        onChange={handleChange}
      />
      <span className={customCheckbox}></span>
    </label>
  );
};

export default ToggleSwitch;
