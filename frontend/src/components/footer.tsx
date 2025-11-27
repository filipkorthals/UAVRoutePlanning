const Footer = () => {
  return (
    <div className="flex flex-col w-full text-right">
      <div className="flex flex-row gap-2 w-full justify-end">
        <button
          type="button"
          className="py-1 px-2 bg-primary text-white rounded-lg mt-5"
        >
          polski
        </button>
        <button
          type="button"
          className="py-1 px-2 bg-primary text-white rounded-lg mt-5"
        >
          Help
        </button>
        <button
          type="button"
          className="py-1 px-2 bg-primary text-white rounded-lg mt-5"
        >
          Credits
        </button>
      </div>
      <h2 className="text-xl">Gdańsk Tech 2025</h2>
    </div>
  );
};

export default Footer;
