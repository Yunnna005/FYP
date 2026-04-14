interface StatProps {
  title: string;
  value: string;
  desc: string;
  accent?: string;
}
 
export default function Stat({ title, value, desc, accent = "bg-sky-500" }: StatProps) {
  return (
    <div className="flex-1 min-w-[160px] bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
      {/* Accent bar */}
      <div className={`h-1 w-full ${accent}`} />
      <div className="px-5 py-4">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-1">
          {title}
        </p>
        <p className="text-2xl font-bold text-slate-800 leading-tight mb-1">
          {value}
        </p>
        <p className="text-xs text-slate-400">{desc}</p>
      </div>
    </div>
  );
}