import { useLayoutEffect } from "react";
import type { RefObject } from "react";

const REFERENCE_FONT_SIZE_PX = 100;
const PADDING_REM = 1;

/**
 * While `enabled`, sizes the element's font so its content fills the window
 * up to a 1rem padding on each side: the element is measured at a reference
 * size, then scaled by the tighter of the two viewport ratios. Assumes the
 * content's dimensions are proportional to font size (true for single-line
 * text).
 */
export default function useFitToWindow(
  ref: RefObject<HTMLElement | null>,
  enabled: boolean,
): void {
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el || !enabled) return;

    const fit = () => {
      const padding =
        2 *
        PADDING_REM *
        parseFloat(getComputedStyle(document.documentElement).fontSize);
      el.style.fontSize = `${REFERENCE_FONT_SIZE_PX}px`;
      const rect = el.getBoundingClientRect();
      const scale = Math.min(
        (window.innerWidth - padding) / rect.width,
        (window.innerHeight - padding) / rect.height,
      );
      el.style.fontSize = `${Math.floor(REFERENCE_FONT_SIZE_PX * scale)}px`;
    };
    fit();
    window.addEventListener("resize", fit);

    return () => {
      window.removeEventListener("resize", fit);
      el.style.fontSize = "";
    };
  }, [ref, enabled]);
}
