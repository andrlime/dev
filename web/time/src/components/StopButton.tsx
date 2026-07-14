import { Button } from "@mantine/core";

interface StopButtonProps {
  onClick: () => void;
}

export default function StopButton({ onClick }: StopButtonProps) {
  return (
    <Button color="red" onClick={onClick}>
      Stop
    </Button>
  );
}
