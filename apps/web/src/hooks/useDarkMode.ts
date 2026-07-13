import * as React from "react";

const STORAGE_KEY = "grant-agent-theme";

type Theme = "dark" | "light";

export function useDarkMode() {
  const [theme, setTheme] = React.useState<Theme>(() => {
    if (typeof window === "undefined") return "light";
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return stored === "dark" ? "dark" : "light";
  });

  React.useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") root.classList.add("dark");
    else root.classList.remove("dark");
    window.localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  return {
    isDark: theme === "dark",
    theme,
    setTheme,
    toggle: () => setTheme((t) => (t === "dark" ? "light" : "dark"))
  };
}

