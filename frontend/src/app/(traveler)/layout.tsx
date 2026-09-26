import { TravelerShell } from "@/components/layout/TravelerShell";

export default function TravelerLayout({ children }: { children: React.ReactNode }) {
  return <TravelerShell>{children}</TravelerShell>;
}
