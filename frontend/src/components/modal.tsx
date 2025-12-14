const Modal = ({ display }: { display: boolean }) => {
  if (!display) return;

  return (
    <div className="absolute bg-gray-600/70 h-full w-full flex items-center justify-center">
      <div className="p-4 w-120 shadow-xl rounded-lg bg-white">
        <div className="text-center">
          <h3 className="text-2xl font-bold">Loading...</h3>
        </div>
      </div>
    </div>
  );
};

export default Modal;
