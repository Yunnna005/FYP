import { useNavigate } from "react-router-dom";
 
export default function UploadButton() {
  const navigate = useNavigate();
 
  return (
    <div
      className="relative flex flex-col items-center rounded-[22px] border border-violet-500/20 px-6 py-5 w-full cursor-pointer"
      style={{
        background: "#160d2b",
        boxShadow: "0 24px 64px rgba(0,0,0,0.4), 0 0 0 1px rgba(167,139,250,0.08) inset",
      }}
      onClick={() => navigate("/upload")}
    >
      {/* Icon ring */}
      <div
        className="w-12 h-12 rounded-full flex items-center justify-center mb-3 border border-violet-500/25"
        style={{ background: "rgba(109,40,217,0.15)" }}
      >
        <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="#a78bfa" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 12V4m0 0L8 8m4-4l4 4" />
        </svg>
      </div>
 
      <h2 className="text-[#e9e3ff] font-semibold text-[15px] mb-1.5 tracking-tight">
        Upload your file
      </h2>
      <p className="text-[#9b8cc8] text-[12px] text-center leading-relaxed mb-4 max-w-[200px]">
        Import your bank CSV or XLSX from AIB or Revolut to analyse spending.
      </p>
 
      {/* Feature icons */}
      <div className="flex gap-4 mb-4">
        {[
          { label: "AIB", icon: <><path strokeLinecap="round" strokeLinejoin="round" d="M3 10.5L12 3l9 7.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1v-9.5z"/><path strokeLinecap="round" strokeLinejoin="round" d="M9 21V12h6v9"/></> },
          { label: "Revolut", icon: <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" /> },
          { label: "CSV", icon: <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /> },
        ].map(({ label, icon }) => (
          <div key={label} className="flex flex-col items-center gap-1">
            <div
              className="w-8 h-8 rounded-[8px] flex items-center justify-center border border-violet-500/20"
              style={{ background: "rgba(109,40,217,0.12)" }}
            >
              <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="#a78bfa" strokeWidth={2}>{icon}</svg>
            </div>
            <span className="text-[9px] font-semibold text-[#7a6ba8] uppercase tracking-wide">{label}</span>
          </div>
        ))}
      </div>
 
      {/* CTA button */}
      <button
        onClick={(e) => { e.stopPropagation(); navigate("/upload"); }}
        className="w-full py-[11px] rounded-xl font-semibold text-[13px] text-white flex items-center justify-center gap-2 transition-all duration-200 active:scale-[0.985]"
        style={{ background: "#7c3aed", boxShadow: "0 0 20px rgba(139,92,246,0.3)" }}
        onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.background = "#6d28d9"; }}
        onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.background = "#7c3aed"; }}
      >
        <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="white" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 12V4m0 0L8 8m4-4l4 4" />
        </svg>
        Upload transactions
      </button>
 
      {/* Trust note */}
      <div className="flex items-center gap-1 mt-2.5">
        <svg width="10" height="10" fill="none" viewBox="0 0 24 24" stroke="#5a4a85" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
        <span className="text-[10px] text-[#5a4a85]">Delete your data anytime · no storage limits</span>
      </div>
    </div>
  );
}