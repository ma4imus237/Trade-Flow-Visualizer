import { useExplorer, useExplorerDispatch } from "../../context/ExplorerContext";
import useCountryProfile from "../../hooks/useCountryProfile";
import { formatUSD } from "../../utils/formatters";

function ProfileSkeleton() {
  return (
    <div className="animate-pulse space-y-4 p-4">
      <div className="h-6 bg-gray-700 rounded w-2/3" />
      <div className="h-4 bg-gray-700 rounded w-1/3" />
      <div className="space-y-2 mt-6">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-4 bg-gray-700 rounded" />
        ))}
      </div>
    </div>
  );
}

function PartnerBar({ name, value, maxValue }) {
  const width = maxValue > 0 ? Math.max((value / maxValue) * 100, 2) : 0;
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="w-20 truncate text-gray-300 shrink-0" title={name}>
        {name}
      </span>
      <div className="flex-1 h-4 bg-gray-700/50 rounded overflow-hidden">
        <div
          className="h-full bg-cyan-500/60 rounded transition-all duration-300"
          style={{ width: `${width}%` }}
        />
      </div>
      <span className="text-gray-400 text-xs w-16 text-right shrink-0">
        {formatUSD(value)}
      </span>
    </div>
  );
}

function PartnerSection({ title, partners }) {
  if (!partners || partners.length === 0) return null;
  const maxValue = Math.max(...partners.map((p) => p.value_usd));

  return (
    <div className="space-y-2">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
        {title}
      </h4>
      <div className="space-y-1.5">
        {partners.slice(0, 8).map((p) => (
          <PartnerBar
            key={p.iso3}
            name={p.name}
            value={p.value_usd}
            maxValue={maxValue}
          />
        ))}
      </div>
    </div>
  );
}

export default function CountryProfile() {
  const { selectedCountry, year, commodity } = useExplorer();
  const dispatch = useExplorerDispatch();
  const { profile, loading, error } = useCountryProfile(
    selectedCountry,
    year,
    commodity
  );

  if (!selectedCountry) return null;

  const handleClose = () => {
    dispatch({ type: "SELECT_COUNTRY", payload: null });
  };

  return (
    <div className="absolute inset-y-0 right-0 w-80 bg-gray-900/95 backdrop-blur-sm border-l border-gray-700/50 overflow-y-auto z-30 animate-slide-in-right">
      <div className="sticky top-0 bg-gray-900/95 backdrop-blur-sm border-b border-gray-700/50 p-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white truncate">
          {loading ? selectedCountry : profile?.name || selectedCountry}
        </h3>
        <button
          onClick={handleClose}
          className="p-1 rounded hover:bg-gray-700 text-gray-400 hover:text-white transition-colors"
          aria-label="Close country profile"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      {loading && <ProfileSkeleton />}

      {error && (
        <div className="p-4">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {profile && !loading && (
        <div className="p-4 space-y-5">
          {profile.region && (
            <span className="inline-block px-2 py-0.5 text-xs rounded bg-gray-700 text-gray-300">
              {profile.region}
            </span>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-gray-800/60 rounded-lg p-3">
              <p className="text-xs text-gray-500 uppercase tracking-wider">Exports</p>
              <p className="text-lg font-semibold text-green-400">
                {formatUSD(profile.total_exports)}
              </p>
            </div>
            <div className="bg-gray-800/60 rounded-lg p-3">
              <p className="text-xs text-gray-500 uppercase tracking-wider">Imports</p>
              <p className="text-lg font-semibold text-red-400">
                {formatUSD(profile.total_imports)}
              </p>
            </div>
          </div>

          <PartnerSection
            title="Top Export Partners"
            partners={profile.top_export_partners}
          />

          <PartnerSection
            title="Top Import Partners"
            partners={profile.top_import_partners}
          />

          {profile.top_commodities && profile.top_commodities.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
                Top Commodities
              </h4>
              <div className="space-y-1">
                {profile.top_commodities.slice(0, 6).map((c) => (
                  <div
                    key={c.code}
                    className="flex items-center justify-between text-sm"
                  >
                    <span className="text-gray-300">{c.name}</span>
                    <span className="text-gray-400 text-xs">
                      {formatUSD(c.value_usd)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
