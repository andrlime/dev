import { useEffect } from "react";
import type { RefObject } from "react";

const FLASH_PERIOD_MS = 500;

/**
 * While `active`, flashes the element's background (and text color) between
 * light and dark. The style is mutated directly instead of going through
 * React state so the flashing does not trigger re-renders, and the timer is
 * phase-locked to the wall clock so the dark flip lands exactly on each
 * seconds change and the light flip on each half-second.
 */
export default function useFlash(
  ref: RefObject<HTMLElement | null>,
  active: boolean,
): void {
  useEffect(() => {
    const el = ref.current;
    if (!el || !active) return;

    let timeout: ReturnType<typeof setTimeout>;
    const tick = () => {
      const ms = Date.now();
      const on = Math.floor(ms / FLASH_PERIOD_MS) % 2 === 0;
      el.style.backgroundColor = on
        ? "var(--mantine-color-dark-7)"
        : "var(--mantine-color-white)";
      el.style.color = on
        ? "var(--mantine-color-dark-0)"
        : "var(--mantine-color-black)";
      timeout = setTimeout(tick, FLASH_PERIOD_MS - (ms % FLASH_PERIOD_MS));
    };
    tick();

    return () => {
      clearTimeout(timeout);
      el.style.backgroundColor = "";
      el.style.color = "";
    };
  }, [ref, active]);
}
