import { useMemo } from "react";
import { Select } from "@mantine/core";
import type { ComboboxItem, SelectProps } from "@mantine/core";

interface TimezoneSelectProps {
  value: string;
  onChange: (timezone: string) => void;
}

// Fuzzy match: every whitespace-separated search token must appear in the
// option with "_" and "/" normalized to spaces, so "new york" finds
// "America/New_York".
const filterTimezones: SelectProps["filter"] = ({ options, search }) => {
  const tokens = search.toLowerCase().split(/\s+/).filter(Boolean);
  return (options as ComboboxItem[]).filter((option) => {
    const label = option.label.toLowerCase().replace(/[_/]/g, " ");
    return tokens.every((token) => label.includes(token));
  });
};

export default function TimezoneSelect({
  value,
  onChange,
}: TimezoneSelectProps) {
  const timezones = useMemo(() => Intl.supportedValuesOf("timeZone"), []);

  return (
    <Select
      label="Timezone"
      data={timezones}
      value={value}
      onChange={(selected) => selected && onChange(selected)}
      searchable
      filter={filterTimezones}
      allowDeselect={false}
    />
  );
}
