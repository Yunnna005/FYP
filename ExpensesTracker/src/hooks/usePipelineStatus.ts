import { useEffect, useState } from "react";

export type PipelineStatus = "idle" | "running" | "done" | "failed";

export function usePipelineStatus(userId: string | null) {
  const [status, setStatus] = useState<PipelineStatus>("idle");

  useEffect(() => {
    console.log("usePipelineStatus effect running, userId:", userId);
    if (!userId) return;

    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;

    // Kick off pipeline once
    fetch(`/api/pipeline/run?user_id=${encodeURIComponent(userId)}`, { method: "POST" })
      .then((r) => r.json())
      .then((d) => !cancelled && setStatus(d.status === "started" ? "running" : d.status));

    // Poll status
    async function poll() {
      try {
        const res = await fetch(`/api/pipeline/status?user_id=${encodeURIComponent(userId!)}`);
        const data = await res.json();
        if (cancelled) return;
        setStatus(data.status);
        if (data.status === "running") {
          timer = setTimeout(poll, 2000);
        }
      } catch {
        if (!cancelled) timer = setTimeout(poll, 3000);
      }
    }
    timer = setTimeout(poll, 1000);

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [userId]);

  return status;
}