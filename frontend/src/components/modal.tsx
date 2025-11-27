import Link from "next/link";

const Modal = ({
  display,
  setDisplay,
}: {
  display: boolean;
  setDisplay: React.Dispatch<React.SetStateAction<boolean>>;
}) => {
  if (!display) return;

  return (
    <div className="absolute bg-gray-600/70 h-full w-full flex items-center justify-center">
      <div className="p-4 w-170 shadow-xl rounded-lg bg-white">
        <div className="text-center">
          <h3 className="text-2xl font-bold">Planned path</h3>
          <div className="mt-2">
            <img src="http://127.0.0.1:5001/static/Planned_path.jpg" />
          </div>
          <div className="justify-center mb-2">
            <Link
              href="/"
              className="px-4 py-2 bg-secondary text-white rounded-lg"
              onClick={() => setDisplay(false)}
            >
              Close
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Modal;
