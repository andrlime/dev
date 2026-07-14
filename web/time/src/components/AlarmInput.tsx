import { TextInput } from "@mantine/core";

interface AlarmInputProps {
  value: string;
  invalid: boolean;
  onChange: (value: string) => void;
}

export default function AlarmInput({
  value,
  invalid,
  onChange,
}: AlarmInputProps) {
  return (
    <TextInput
      label="Flash at (HH:mm)"
      placeholder="13:37"
      value={value}
      onChange={(event) => onChange(event.currentTarget.value)}
      error={invalid ? "Use HH:mm" : undefined}
    />
  );
}
