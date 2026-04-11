import { usePipelineStatus } from "../hooks/usePipelineStatus";

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  idle:    { label: "Waiting...",       color: "bg-slate-400" },
  started: { label: "Start Analysing...",     color: "bg-yellow-400 animate-pulse" },
  running: { label: "Analysing Transactions...",     color: "bg-yellow-400 animate-pulse" },
  done:    { label: "Up to date",       color: "bg-green-500" },
  failed:  { label: "Analysis failed",  color: "bg-red-500" },
};

export default function PipelineIndicator() {
  const userId = localStorage.getItem("user_id");
  const status = usePipelineStatus(userId);

  if (!userId) return null;

  const config = STATUS_CONFIG[status] ?? { label: `Unknown: ${status}`, color: "bg-red-500" };

  return (
    <div className="flex items-center gap-2 text-sm">
      <span className={`inline-block w-2.5 h-2.5 rounded-full ${config.color}`}></span>
      <span>{config.label}</span>
    </div>
  );
}