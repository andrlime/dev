import { useRef, useState } from "react";
import { Group } from "@mantine/core";

import AlarmInput from "@/components/AlarmInput";
import Clock from "@/components/Clock";
import ColorSchemeToggle from "@/components/ColorSchemeToggle";
import StopButton from "@/components/StopButton";
import TimezoneSelect from "@/components/TimezoneSelect";
import useFlash from "@/hooks/useFlash";
import useNow from "@/hooks/useNow";
import { parseTimeOfDay, secondsBetween, timeParts } from "@/shared/time";

import "./app.scss";

const CLOCK_TICK_MS = 250;
const FLASH_WINDOW_SECONDS = 3 * 60;

export default function App() {
  const [timezone, setTimezone] = useState(
    () => Intl.DateTimeFormat().resolvedOptions().timeZone,
  );
  const [alarm, setAlarm] = useState("");
  const [suspended, setSuspended] = useState(false);
  const [zoomed, setZoomed] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  const now = useNow(CLOCK_TICK_MS);
  const [hh, mm, ss] = timeParts(now, timezone);
  const currentSeconds = Number(hh) * 3600 + Number(mm) * 60 + Number(ss);

  const alarmSeconds = parseTimeOfDay(alarm);
  const inWindow =
    alarmSeconds !== null &&
    secondsBetween(currentSeconds, alarmSeconds) <= FLASH_WINDOW_SECONDS;
  const flashing = inWindow && !suspended;

  useFlash(rootRef, flashing);

  return (
    <div className={zoomed ? "app app--zoomed" : "app"} ref={rootRef}>
      <ColorSchemeToggle className="app__chrome app__scheme_toggle" />

      <Clock
        time={`${hh}:${mm}:${ss}`}
        zoomed={zoomed}
        onToggleZoom={() => setZoomed((z) => !z)}
      />

      {flashing && <StopButton onClick={() => setSuspended(true)} />}

      <Group className="app__chrome" justify="center" align="flex-start">
        <TimezoneSelect value={timezone} onChange={setTimezone} />
        <AlarmInput
          value={alarm}
          invalid={alarm.trim() !== "" && alarmSeconds === null}
          onChange={(value) => {
            setAlarm(value);
            setSuspended(false);
          }}
        />
      </Group>
    </div>
  );
}
