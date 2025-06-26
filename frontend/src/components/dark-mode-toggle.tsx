import { Sun, Moon } from "@/lib/icons";
import { useTheme } from "./theme-provider";

export function DarkModeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="dark-mode-toggle"
      aria-label="Toggle dark mode"
    >
      {theme === "light" ? (
        <Moon className="h-5 w-5" />
      ) : (
        <Sun className="h-5 w-5" />
      )}
    </button>
  );
}