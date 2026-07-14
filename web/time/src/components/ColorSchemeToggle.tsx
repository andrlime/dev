import {
  ActionIcon,
  useComputedColorScheme,
  useMantineColorScheme,
} from "@mantine/core";

interface ColorSchemeToggleProps {
  className?: string;
}

export default function ColorSchemeToggle({
  className,
}: ColorSchemeToggleProps) {
  const { setColorScheme } = useMantineColorScheme();
  const colorScheme = useComputedColorScheme("light");

  return (
    <ActionIcon
      className={className}
      variant="default"
      size="lg"
      aria-label="Toggle color scheme"
      onClick={() => setColorScheme(colorScheme === "light" ? "dark" : "light")}
    >
      {colorScheme === "light" ? "🌙" : "☀️"}
    </ActionIcon>
  );
}
