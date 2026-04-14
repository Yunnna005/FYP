import { useState } from "react";
import { useNavigate } from "react-router-dom";
import BloomLogo from "../assets/logo-dark-only-removebg-preview.png";

const icons = [
  { icon: <svg width="26" height="26" fill="none" viewBox="0 0 24 24"><rect x="2" y="6" width="20" height="14" rx="3" stroke="#c084fc" strokeWidth="1.5"/><path d="M2 10h20" stroke="#c084fc" strokeWidth="1.5"/><circle cx="6" cy="15" r="1" fill="#c084fc"/></svg>, style: "top-[5%] left-[3%] w-13 h-13 bg-[#2a0f4f] -rotate-[8deg]", delay: "0s" },
  { icon: <svg width="30" height="30" fill="none" viewBox="0 0 24 24"><path d="M3 17l4-8 4 5 3-3 4 6" stroke="#d8b4fe" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>, style: "top-[40%] right-[2%] w-14 h-14 bg-[#1f0a42] rotate-[5deg]", delay: "1s" },
  { icon: <svg width="24" height="24" fill="none" viewBox="0 0 24 24"><path d="M12 1v22M17 5H9.5a3.5 3.5 0 100 7h5a3.5 3.5 0 110 7H6" stroke="#c084fc" strokeWidth="1.5" strokeLinecap="round"/></svg>, style: "bottom-[8%] left-[4%] w-12 h-12 bg-[#1a0638] rotate-[12deg]", delay: "2s" },
  { icon: <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" stroke="#c084fc" strokeWidth="1.5" strokeLinecap="round"/></svg>, style: "top-[5%] right-[4%] w-14 h-14 bg-[#2a0f4f] rotate-[10deg]", delay: "0.5s" },
  { icon: <svg width="25" height="25" fill="none" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="#d8b4fe" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>, style: "bottom-[6%] right-[3%] w-12 h-12 bg-[#1f0a42] -rotate-[3deg]", delay: "3.5s" },
  { icon: <svg width="26" height="26" fill="none" viewBox="0 0 24 24"><path d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2 5h14" stroke="#e0bbff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>, style: "top-[55%] left-[1%] w-13 h-13 bg-[#2a0f4f] rotate-[6deg]", delay: "1.5s" },
];

export default function UploadAuth() {
  const [mode, setMode] = useState<"signup" | "login">("signup");
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [fullName, setFullName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [accountName, setAccountName] = useState("");
  const [bank, setBank] = useState("aib");
  const [file, setFile] = useState<File | null>(null);

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!file) { setError("Please select a CSV file"); return; }
    setLoading(true);
    const formData = new FormData();
    formData.append("bank", bank);
    formData.append("email", email);
    formData.append("password", password);
    formData.append("full_name", fullName);
    formData.append("phone_number", phoneNumber);
    formData.append("account_name", accountName);
    formData.append("file", file);
    try {
      const res = await fetch("/api/upload/signup", { method: "POST", body: formData });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("login_method", "csv");
        navigate("/dashboard");
      } else {
        setError(data.detail || "Signup failed");
      }
    } catch (err) {
      setError("Network error: " + err);
    } finally {
      setLoading(false);
    }
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/upload/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("login_method", "csv");
        navigate("/dashboard");
      } else {
        setError(data.detail || "Login failed");
      }
    } catch (err) {
      setError("Network error: " + err);
    } finally {
      setLoading(false);
    }
  }

  const inputClass =
    "w-full px-4 py-[10px] rounded-xl text-[13px] text-slate-700 placeholder-slate-400 outline-none transition-all duration-150 disabled:opacity-50";
  const inputStyle = {
    background: "#f8f7ff",
    border: "1px solid rgba(139,92,246,0.18)",
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-[#0a0118] py-8">

      {/* Floating icons */}
      {icons.map((item, i) => (
        <div
          key={i}
          className={`absolute flex items-center justify-center rounded-2xl ${item.style}`}
          style={{
            animationName: "bloomFloat",
            animationDuration: "6.5s",
            animationTimingFunction: "ease-in-out",
            animationIterationCount: "infinite",
            animationDelay: item.delay,
          }}
        >
          {item.icon}
        </div>
      ))}

      {/* Radial glow */}
      <div
        className="absolute w-[600px] h-[600px] rounded-full pointer-events-none z-0"
        style={{
          background: "radial-gradient(circle, rgba(167,139,250,0.18) 0%, transparent 65%)",
          top: "50%", left: "50%",
          transform: "translate(-50%, -50%)",
        }}
      />

      <style>{`
        @keyframes bloomFloat {
          0%, 100% { transform: translateY(0px) rotate(var(--tw-rotate, 0deg)); }
          50%       { transform: translateY(-14px) rotate(var(--tw-rotate, 0deg)); }
        }
      `}</style>

      <div className="relative z-10 w-full max-w-md mx-4">
        <div
          className="rounded-[2.2rem] border border-violet-100 px-8 py-8 flex flex-col"
          style={{
            background: "#ffffff",
            boxShadow: "0 24px 80px rgba(139,92,246,0.15), 0 0 0 1px rgba(139,92,246,0.08) inset",
          }}
        >
          {/* Header */}
          <div className="flex flex-col items-center mb-6">
            <img
              src={BloomLogo}
              alt="Bloom"
              className="w-16 h-16 object-contain mb-2"
              style={{ filter: "drop-shadow(0 0 20px rgba(167,139,250,0.35))" }}
            />
            <p
              className="text-[18px] text-violet-300 tracking-wide leading-none"
              style={{ fontFamily: "'Bagel Fat One', system-ui", fontWeight: 400 }}
            >
              Bloom
            </p>
            <p className="text-[9px] font-semibold tracking-[0.2em] text-violet-400/70 uppercase mt-1">
              Upload your transactions
            </p>
          </div>

          {/* Tabs */}
          <div
            className="flex rounded-2xl p-1 mb-5"
            style={{ background: "rgba(139,92,246,0.06)", border: "1px solid rgba(139,92,246,0.1)" }}
          >
            {(["signup", "login"] as const).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`flex-1 py-2 rounded-xl text-[12.5px] font-semibold transition-all duration-200 ${
                  mode === m
                    ? "text-violet-700"
                    : "text-slate-400 hover:text-slate-500"
                }`}
                style={
                  mode === m
                    ? { background: "rgba(139,92,246,0.25)", boxShadow: "0 0 0 1px rgba(139,92,246,0.3) inset" }
                    : {}
                }
              >
                {m === "signup" ? "Sign up" : "Log in"}
              </button>
            ))}
          </div>

          {/* Forms */}
          {mode === "signup" ? (
            <form onSubmit={handleSignup} className="flex flex-col gap-2">
              {[
                { type: "email", placeholder: "Email address", value: email, onChange: setEmail, required: true },
                { type: "password", placeholder: "Password", value: password, onChange: setPassword, required: true },
                { type: "text", placeholder: "Full name", value: fullName, onChange: setFullName, required: true },
                { type: "tel", placeholder: "Phone number (optional)", value: phoneNumber, onChange: setPhoneNumber, required: false },
                { type: "text", placeholder: "Account name (e.g. AIB Current)", value: accountName, onChange: setAccountName, required: true },
              ].map(({ type, placeholder, value, onChange, required }) => (
                <input
                  key={placeholder}
                  type={type}
                  placeholder={placeholder}
                  className={inputClass}
                  style={inputStyle}
                  value={value}
                  onChange={(e) => onChange(e.target.value)}
                  required={required}
                  onFocus={(e) => (e.currentTarget.style.border = "1px solid rgba(139,92,246,0.45)")}
                  onBlur={(e) => (e.currentTarget.style.border = "1px solid rgba(139,92,246,0.18)")}
                />
              ))}

              <select
                className={inputClass}
                style={{ ...inputStyle, cursor: "pointer" }}
                value={bank}
                onChange={(e) => setBank(e.target.value)}
              >
                <option value="aib" style={{ background: "#fff" }}>AIB</option>
                <option value="revolut" style={{ background: "#fff" }}>Revolut</option>
              </select>

              {/* File upload zone */}
              <label className="block cursor-pointer">
                <div
                  className="rounded-xl p-4 text-center transition-all duration-150"
                  style={{
                    border: file
                      ? "1.5px dashed rgba(139,92,246,0.6)"
                      : "1.5px dashed rgba(139,92,246,0.22)",
                    background: file
                      ? "rgba(109,40,217,0.12)"
                      : "rgba(109,40,217,0.05)",
                  }}
                >
                  {file ? (
                    <div className="flex items-center justify-center gap-2 text-violet-600">
                      <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-[12.5px] font-medium truncate max-w-[260px]">{file.name}</span>
                    </div>
                  ) : (
                    <>
                      <svg className="w-6 h-6 mx-auto mb-1" fill="none" viewBox="0 0 24 24" stroke="rgba(167,139,250,0.45)" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1M12 12V4m0 0L8 8m4-4l4 4" />
                      </svg>
                      <p className="text-[12px] text-slate-400">Click to upload your bank file</p>
                      <p className="text-[10.5px] mt-0.5 text-slate-300">CSV, XLSX, XLS, or HTML</p>
                    </>
                  )}
                </div>
                <input
                  type="file"
                  accept=".csv,.xlsx,.xls,.html"
                  className="hidden"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  required
                />
              </label>

              {error && (
                <div className="flex items-center gap-2 text-rose-300 text-[12px] px-3 py-2 rounded-xl" style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.2)" }}>
                  <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                  </svg>
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-[11px] rounded-xl font-semibold text-[13px] text-white flex items-center justify-center gap-2 transition-all duration-200 active:scale-[0.985] disabled:opacity-50 disabled:cursor-not-allowed mt-1"
                style={{ background: "#7c3aed", boxShadow: "0 0 20px rgba(139,92,246,0.3)" }}
                onMouseEnter={(e) => { if (!loading) (e.currentTarget as HTMLButtonElement).style.background = "#6d28d9"; }}
                onMouseLeave={(e) => { if (!loading) (e.currentTarget as HTMLButtonElement).style.background = "#7c3aed"; }}
              >
                {loading ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                    </svg>
                    Setting up your dashboard...
                  </>
                ) : "Sign up & analyse"}
              </button>

              {loading && (
                <p className="text-[11px] text-slate-400 text-center">
                  This may take 15–30 seconds while we run the analysis pipeline.
                </p>
              )}
            </form>
          ) : (
            <form onSubmit={handleLogin} className="flex flex-col gap-2">
              {[
                { type: "email", placeholder: "Email address", value: email, onChange: setEmail },
                { type: "password", placeholder: "Password", value: password, onChange: setPassword },
              ].map(({ type, placeholder, value, onChange }) => (
                <input
                  key={placeholder}
                  type={type}
                  placeholder={placeholder}
                  className={inputClass}
                  style={inputStyle}
                  value={value}
                  onChange={(e) => onChange(e.target.value)}
                  required
                  onFocus={(e) => (e.currentTarget.style.border = "1px solid rgba(139,92,246,0.45)")}
                  onBlur={(e) => (e.currentTarget.style.border = "1px solid rgba(139,92,246,0.18)")}
                />
              ))}

              {error && (
                <div className="flex items-center gap-2 text-rose-300 text-[12px] px-3 py-2 rounded-xl" style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.2)" }}>
                  <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                  </svg>
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-[11px] rounded-xl font-semibold text-[13px] text-white flex items-center justify-center gap-2 transition-all duration-200 active:scale-[0.985] disabled:opacity-50 disabled:cursor-not-allowed mt-1"
                style={{ background: "#7c3aed", boxShadow: "0 0 20px rgba(139,92,246,0.3)" }}
                onMouseEnter={(e) => { if (!loading) (e.currentTarget as HTMLButtonElement).style.background = "#6d28d9"; }}
                onMouseLeave={(e) => { if (!loading) (e.currentTarget as HTMLButtonElement).style.background = "#7c3aed"; }}
              >
                {loading ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                    </svg>
                    Logging in...
                  </>
                ) : "Log in"}
              </button>
            </form>
          )}

          <button
            className="mt-4 flex items-center justify-center gap-1 text-[11.5px] transition-colors duration-150"
            style={{ color: "rgba(139,92,246,0.5)" }}
            onClick={() => navigate("/")}
            onMouseEnter={(e) => (e.currentTarget.style.color = "rgba(109,40,217,0.9)")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "rgba(139,92,246,0.5)")}
          >
            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            Back to Plaid login
          </button>

          {/* Terms */}
          <div
            className="mt-4 pt-4 text-[10.5px] leading-relaxed space-y-1"
            style={{ borderTop: "1px solid rgba(139,92,246,0.1)", color: "rgba(100,80,140,0.5)" }}
          >
            <p className="font-semibold" style={{ color: "rgba(100,80,140,0.7)" }}>Terms & Data Notice</p>
            <p>This is a student project for demo purposes. Your data is stored to enable AI features. You can delete it anytime from the Dashboard.</p>
          </div>
        </div>
      </div>
    </div>
  );
}