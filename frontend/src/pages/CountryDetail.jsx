import { useParams, useNavigate } from "react-router-dom";
import { useExplorer, useExplorerDispatch } from "../context/ExplorerContext";
import useCountryProfile from "../hooks/useCountryProfile";
import FlowBarChart from "../components/charts/FlowBarChart";
import TimeSeriesChart from "../components/charts/TimeSeriesChart";
import { formatUSD } from "../utils/formatters";

function StatCard({ label, value, colorClass }) {
  return (
    <div className="bg-gray-800/60 rounded-lg p-4">
      <p className="text-xs text-gray-500 uppercase tracking-wider">{label}</p>
      <p className={`text-2xl font-bold mt-1 ${colorClass}`}>{value}</p>
    </div>
  );
}

function SkeletonPage() {
  return (
    <div className="animate-pulse space-y-6 p-6">
      <div className="h-8 bg-gray-700 rounded w-1/3" />
      <div className="grid grid-cols-2 gap-4">
        <div className="h-24 bg-gray-700 rounded" />
        <div className="h-24 bg-gray-700 rounded" />
      </div>
      <div className="h-64 bg-gray-700 rounded" />
      <div className="h-48 bg-gray-700 rounded" />
    </div>
  );
}

export default function CountryDetail() {
  const { iso3 } = useParams();
  const navigate = useNavigate();
  const { year, commodity } = useExplorer();
  const dispatch = useExplorerDispatch();
  const { profile, loading, error } = useCountryProfile(iso3, year, commodity);

  const topExportPartner = profile?.top_export_partners?.[0];

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur-sm sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center gap-4">
          <button
            onClick={() => navigate(-1)}
            className="p-2 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white transition-colors"
            aria-label="Go back"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </button>
          <div>
            <h1 className="text-lg font-bold">
              {loading ? iso3 : profile?.name || iso3}
            </h1>
            {profile?.region && (
              <span className="text-xs text-gray-500">{profile.region}</span>
            )}
          </div>
          <div className="ml-auto flex items-center gap-3 text-sm text-gray-400">
            <span>{commodity}</span>
            <span className="text-gray-600">|</span>
            <span>{year}</span>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {loading && <SkeletonPage />}

        {error && (
          <div className="rounded-lg bg-red-500/10 border border-red-500/30 p-4">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {profile && !loading && (
          <div className="space-y-8">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                label="Total Exports"
                value={formatUSD(profile.total_exports)}
                colorClass="text-green-400"
              />
              <StatCard
                label="Total Imports"
                value={formatUSD(profile.total_imports)}
                colorClass="text-red-400"
              />
              <StatCard
                label="Export Partners"
                value={profile.top_export_partners?.length || 0}
                colorClass="text-cyan-400"
              />
              <StatCard
                label="Import Partners"
                value={profile.top_import_partners?.length || 0}
                colorClass="text-amber-400"
              />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-gray-900/60 rounded-xl border border-gray-800 p-4">
                <h2 className="text-sm font-semibold text-gray-400 mb-3">
                  Top Export Partners
                </h2>
                <div className="h-72">
                  <FlowBarChart
                    partners={profile.top_export_partners}
                    commodity={commodity}
                  />
                </div>
              </div>

              <div className="bg-gray-900/60 rounded-xl border border-gray-800 p-4">
                <h2 className="text-sm font-semibold text-gray-400 mb-3">
                  Top Import Partners
                </h2>
                <div className="h-72">
                  <FlowBarChart
                    partners={profile.top_import_partners}
                    commodity={commodity}
                  />
                </div>
              </div>
            </div>

            {topExportPartner && (
              <div className="bg-gray-900/60 rounded-xl border border-gray-800 p-4">
                <h2 className="text-sm font-semibold text-gray-400 mb-3">
                  Trade with {topExportPartner.name} over time
                </h2>
                <div className="h-64">
                  <TimeSeriesChart
                    reporter={iso3}
                    partner={topExportPartner.iso3}
                    commodity={commodity}
                  />
                </div>
              </div>
            )}

            {profile.top_commodities && profile.top_commodities.length > 0 && (
              <div className="bg-gray-900/60 rounded-xl border border-gray-800 p-4">
                <h2 className="text-sm font-semibold text-gray-400 mb-3">
                  Top Commodities
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                  {profile.top_commodities.map((c) => (
                    <div
                      key={c.code}
                      className="flex items-center justify-between bg-gray-800/40 rounded-lg px-3 py-2"
                    >
                      <span className="text-sm text-gray-300">{c.name}</span>
                      <span className="text-sm text-gray-400 font-mono">
                        {formatUSD(c.value_usd)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
