import { AppShell } from "@/components/app/AppShell";
import { RealtimeProvider } from "@/lib/realtime/RealtimeProvider";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <RealtimeProvider>
      <AppShell>{children}</AppShell>
    </RealtimeProvider>
  );
}
