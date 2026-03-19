import { createContext, useContext, useReducer } from "react";

const initialState = {
  commodity: "lithium",
  year: 2023,
  flowType: "export",
  selectedCountry: null,
  highlightedArc: null,
  minValue: 0,
  isPlaying: false,
  viewState: {
    longitude: 0,
    latitude: 20,
    zoom: 1.5,
    pitch: 30,
    bearing: 0,
  },
};

function explorerReducer(state, action) {
  switch (action.type) {
    case "SET_COMMODITY":
      return { ...state, commodity: action.payload };
    case "SET_YEAR":
      return { ...state, year: action.payload };
    case "SET_FLOW_TYPE":
      return { ...state, flowType: action.payload };
    case "SELECT_COUNTRY":
      return { ...state, selectedCountry: action.payload };
    case "HIGHLIGHT_ARC":
      return { ...state, highlightedArc: action.payload };
    case "SET_MIN_VALUE":
      return { ...state, minValue: action.payload };
    case "SET_PLAYING":
      return { ...state, isPlaying: action.payload };
    case "SET_VIEW_STATE":
      return { ...state, viewState: action.payload };
    case "RESET":
      return initialState;
    default:
      return state;
  }
}

const ExplorerContext = createContext(null);
const ExplorerDispatchContext = createContext(null);

export function ExplorerProvider({ children }) {
  const [state, dispatch] = useReducer(explorerReducer, initialState);
  return (
    <ExplorerContext.Provider value={state}>
      <ExplorerDispatchContext.Provider value={dispatch}>
        {children}
      </ExplorerDispatchContext.Provider>
    </ExplorerContext.Provider>
  );
}

export function useExplorer() {
  const context = useContext(ExplorerContext);
  if (!context) throw new Error("useExplorer must be used within ExplorerProvider");
  return context;
}

export function useExplorerDispatch() {
  const context = useContext(ExplorerDispatchContext);
  if (!context) throw new Error("useExplorerDispatch must be used within ExplorerProvider");
  return context;
}
