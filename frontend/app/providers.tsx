"use client";

import { createContext, useContext, useEffect, useState } from "react";

type Theme = "light" | "dark";

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

function getInitialThemeState(): { hasExplicitPreference: boolean; theme: Theme } {
  if (typeof window === "undefined") {
    return {
      hasExplicitPreference: false,
      theme: "light" as Theme,
    };
  }

  const saved = localStorage.getItem("theme");
  if (saved === "light" || saved === "dark") {
    return {
      hasExplicitPreference: true,
      theme: saved,
    };
  }

  return {
    hasExplicitPreference: false,
    theme: window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light",
  };
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [{ hasExplicitPreference, theme }, setThemeState] = useState(getInitialThemeState);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");

    if (hasExplicitPreference) {
      localStorage.setItem("theme", theme);
      return;
    }

    localStorage.removeItem("theme");
  }, [hasExplicitPreference, theme]);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = (e: MediaQueryListEvent) => {
      setThemeState((current) =>
        current.hasExplicitPreference ? current : { ...current, theme: e.matches ? "dark" : "light" }
      );
    };

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, [hasExplicitPreference]);

  const toggleTheme = () => {
    setThemeState((current) => ({
      hasExplicitPreference: true,
      theme: current.theme === "light" ? "dark" : "light",
    }));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}
