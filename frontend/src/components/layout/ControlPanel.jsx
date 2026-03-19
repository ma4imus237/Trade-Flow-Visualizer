import CommoditySelector from "../controls/CommoditySelector";
import YearSelector from "../controls/YearSelector";
import FlowTypeToggle from "../controls/FlowTypeToggle";
import ValueFilter from "../controls/ValueFilter";
import TimeSlider from "../controls/TimeSlider";

/**
 * Left sidebar containing all map controls.
 */
export default function ControlPanel() {
  return (
    <aside className="flex w-64 shrink-0 flex-col gap-5 overflow-y-auto border-r border-white/10 bg-gray-950 p-4">
      <CommoditySelector />
      <FlowTypeToggle />
      <YearSelector />
      <ValueFilter />
      <TimeSlider />
    </aside>
  );
}
