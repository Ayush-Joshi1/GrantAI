import { MoonStar, SunMedium } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { useDarkMode } from "@/hooks/useDarkMode";

export function ThemeToggle() {
  const { isDark, toggle } = useDarkMode();

  return (
    <Button
      type="button"
      variant="secondary"
      size="sm"
      onClick={toggle}
      className="min-w-[110px]"
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
    >
      {isDark ? <SunMedium className="size-4" /> : <MoonStar className="size-4" />}
      <span>{isDark ? "Light" : "Dark"}</span>
    </Button>
  );
}
