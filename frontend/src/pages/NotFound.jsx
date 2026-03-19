import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex h-screen items-center justify-center bg-gray-950 text-white">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-600">404</h1>
        <p className="mt-4 text-lg text-gray-400">Page not found</p>
        <Link
          to="/"
          className="mt-6 inline-block rounded-lg bg-cyan-600 px-6 py-2 text-sm font-medium hover:bg-cyan-500 transition-colors"
        >
          Back to Explorer
        </Link>
      </div>
    </div>
  );
}
