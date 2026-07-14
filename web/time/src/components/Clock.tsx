import { useRef } from "react";

import useFitToWindow from "@/hooks/useFitToWindow";

import "./clock.scss";

interface ClockProps {
  time: string;
  zoomed: boolean;
  onToggleZoom: () => void;
}

/** The big time display. Clicking it toggles zoomed mode, where the text is
 * sized to span the entire window. */
export default function Clock({ time, zoomed, onToggleZoom }: ClockProps) {
  const ref = useRef<HTMLDivElement>(null);
  useFitToWindow(ref, zoomed);

  return (
    <div className="clock" ref={ref} onClick={onToggleZoom}>
      {time}
    </div>
  );
}
