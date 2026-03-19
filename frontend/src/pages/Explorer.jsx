import Header from "../components/layout/Header";
import ControlPanel from "../components/layout/ControlPanel";
import FlowMap from "../components/map/FlowMap";
import { useFlows } from "../hooks/useFlows";

/**
 * Main Explorer page.
 * Layout: Header on top, ControlPanel on left sidebar, FlowMap filling remaining space.
 */
export default function Explorer() {
  const { flows, loading, error } = useFlows();

  return (
    <div className="flex h-screen flex-col bg-gray-950 text-white">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar - hidden on small screens, shown on md+ */}
        <div className="hidden md:block">
          <ControlPanel />
        </div>

        {/* Map area */}
        <main className="relative flex-1">
          {loading && (
            <div className="absolute inset-0 z-50 flex items-center justify-center bg-gray-950/70">
              <div className="flex items-center gap-3 rounded-lg bg-gray-900 px-5 py-3 text-sm text-gray-300 shadow-lg">
                <svg
                  className="h-5 w-5 animate-spin text-cyan-400"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                Loading trade flows...
              </div>
            </div>
          )}

          {error && (
            <div className="absolute left-1/2 top-4 z-50 -translate-x-1/2 rounded-lg border border-red-500/30 bg-red-950/80 px-4 py-2 text-sm text-red-300 shadow-lg">
              {error}
            </div>
          )}

          <FlowMap flows={flows} />
        </main>

        {/* Right sidebar placeholder for future panels */}
        <div className="hidden w-72 shrink-0 border-l border-white/10 bg-gray-950 lg:block">
          <div className="flex h-full items-center justify-center text-xs text-gray-600">
            Detail panel
          </div>
        </div>
      </div>

      {/* Mobile controls drawer - shown only on small screens */}
      <div className="border-t border-white/10 bg-gray-950 p-3 md:hidden">
        <ControlPanel />
      </div>
    </div>
  );
}
