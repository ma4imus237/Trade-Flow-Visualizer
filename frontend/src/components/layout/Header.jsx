import { Link, useLocation } from "react-router-dom";

const NAV_LINKS = [
  { to: "/", label: "Explorer" },
  { to: "/country/USA", label: "Country Detail" },
  { to: "/shifts", label: "Shifts" },
];

/**
 * Top navigation bar with app title and route links.
 */
export default function Header() {
  const location = useLocation();

  return (
    <header className="flex h-12 shrink-0 items-center justify-between border-b border-white/10 bg-gray-950 px-4">
      <Link to="/" className="text-base font-bold tracking-tight text-white">
        Trade Flow Visualizer
      </Link>

      <nav className="flex items-center gap-1">
        {NAV_LINKS.map((link) => {
          const active = location.pathname === link.to;
          return (
            <Link
              key={link.to}
              to={link.to}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                active
                  ? "bg-white/10 text-white"
                  : "text-gray-400 hover:bg-white/5 hover:text-gray-200"
              }`}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}
