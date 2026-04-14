import { useState } from "react";
import { useNavigate } from "react-router-dom";
// Drop Bloom.svg into src/assets/ — Vite handles SVG imports natively
import BloomLogo from "../assets/Bloom.svg";

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
      setError("Network error" + err);
    } finally {
      setLoading(false);
    }
  }

  const inputClass =
    "w-full px-4 py-3 rounded-xl border border-gray-100 bg-gray-50 text-gray-800 text-sm placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-violet-300 focus:border-transparent focus:bg-white transition-all duration-150";

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-[#f5f3ff] py-8">
      {/* Ambient blobs */}
      <div
        className="absolute top-[-100px] left-[-100px] w-[420px] h-[420px] rounded-full pointer-events-none"
        style={{ background: "radial-gradient(circle, #ede9fe 0%, transparent 70%)", opacity: 0.7 }}
      />
      <div
        className="absolute bottom-[-80px] right-[-80px] w-[380px] h-[380px] rounded-full pointer-events-none"
        style={{ background: "radial-gradient(circle, #c4b5fd 0%, transparent 70%)", opacity: 0.5 }}
      />

      <div className="relative z-10 w-full max-w-md mx-4">
        <div className="bg-white rounded-3xl shadow-2xl shadow-violet-200/60 px-8 py-8 flex flex-col">

          {/* Header with your real logo */}
          <div className="flex flex-col items-center mb-6">
            <img
              src={BloomLogo}
              alt="Bloom — Your AI Assistant"
              className="w-16 h-16 object-contain mb-1"
            />
            <p className="text-[10px] font-semibold tracking-[0.18em] text-violet-300 uppercase">
              Upload your transactions
            </p>
          </div>

          {/* Tab toggle */}
          <div className="flex bg-gray-50 rounded-2xl p-1 mb-6 border border-gray-100">
            <button
              className={`flex-1 py-2 rounded-xl text-sm font-semibold transition-all duration-200 ${
                mode === "signup"
                  ? "bg-white text-violet-700 shadow-sm"
                  : "text-gray-400 hover:text-gray-500"
              }`}
              onClick={() => setMode("signup")}
            >
              Sign up
            </button>
            <button
              className={`flex-1 py-2 rounded-xl text-sm font-semibold transition-all duration-200 ${
                mode === "login"
                  ? "bg-white text-violet-700 shadow-sm"
                  : "text-gray-400 hover:text-gray-500"
              }`}
              onClick={() => setMode("login")}
            >
              Log in
            </button>
          </div>

          {mode === "signup" ? (
            <form onSubmit={handleSignup} className="space-y-3">
              <input type="email" placeholder="Email address" className={inputClass}
                value={email} onChange={(e) => setEmail(e.target.value)} required />
              <input type="password" placeholder="Password" className={inputClass}
                value={password} onChange={(e) => setPassword(e.target.value)} required />
              <input type="text" placeholder="Full name" className={inputClass}
                value={fullName} onChange={(e) => setFullName(e.target.value)} required />
              <input type="tel" placeholder="Phone number (optional)" className={inputClass}
                value={phoneNumber} onChange={(e) => setPhoneNumber(e.target.value)} />
              <input type="text" placeholder="Account name (e.g. AIB Current)" className={inputClass}
                value={accountName} onChange={(e) => setAccountName(e.target.value)} required />

              <select
                className={inputClass}
                value={bank}
                onChange={(e) => setBank(e.target.value)}
              >
                <option value="aib">AIB</option>
                <option value="revolut">Revolut</option>
              </select>

              {/* Styled file upload zone */}
              <label className="block cursor-pointer">
                <div
                  className={`border-2 border-dashed rounded-xl p-4 text-center transition-all duration-150 ${
                    file
                      ? "border-violet-300 bg-violet-50"
                      : "border-gray-200 bg-gray-50 hover:border-violet-200 hover:bg-violet-50/30"
                  }`}
                >
                  {file ? (
                    <div className="flex items-center justify-center gap-2 text-violet-600">
                      <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-sm font-medium truncate max-w-[260px]">{file.name}</span>
                    </div>
                  ) : (
                    <div className="text-gray-300">
                      <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 mx-auto mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1M12 12V4m0 0L8 8m4-4l4 4" />
                      </svg>
                      <p className="text-sm text-gray-400">Click to upload your bank file</p>
                      <p className="text-xs mt-0.5 text-gray-300">CSV, XLSX, XLS, or HTML</p>
                    </div>
                  )}
                </div>
                <input
                  type="file"
                  accept=".csv,.xlsx,.xls,.html,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/csv,text/html"
                  className="hidden"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  required
                />
              </label>

              {error && (
                <div className="flex items-center gap-2 text-red-500 bg-red-50 rounded-xl px-3 py-2 text-sm">
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                  </svg>
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-2xl bg-violet-600 hover:bg-violet-700 active:scale-[0.98] text-white font-semibold text-sm transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                    </svg>
                    Setting up your dashboard...
                  </>
                ) : (
                  "Sign up & analyse"
                )}
              </button>

              {loading && (
                <p className="text-xs text-gray-300 text-center">
                  This may take 15–30 seconds while we run the analysis pipeline.
                </p>
              )}
            </form>
          ) : (
            <form onSubmit={handleLogin} className="space-y-3">
              <input type="email" placeholder="Email address" className={inputClass}
                value={email} onChange={(e) => setEmail(e.target.value)} required />
              <input type="password" placeholder="Password" className={inputClass}
                value={password} onChange={(e) => setPassword(e.target.value)} required />

              {error && (
                <div className="flex items-center gap-2 text-red-500 bg-red-50 rounded-xl px-3 py-2 text-sm">
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                  </svg>
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-2xl bg-violet-600 hover:bg-violet-700 active:scale-[0.98] text-white font-semibold text-sm transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                    </svg>
                    Logging in...
                  </>
                ) : (
                  "Log in"
                )}
              </button>
            </form>
          )}

          {/* Back */}
          <button
            className="mt-5 flex items-center justify-center gap-1 text-xs text-gray-300 hover:text-violet-500 transition-colors duration-150"
            onClick={() => navigate("/")}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            Back to Plaid login
          </button>

          {/* Terms */}
          <div className="mt-5 text-xs text-gray-300 border-t border-gray-50 pt-4 space-y-1">
            <p className="font-semibold text-gray-400">Terms & Data Notice</p>
            <p>This is a student project for demo purposes. By using this app you acknowledge:</p>
            <ul className="list-disc list-inside space-y-0.5 mt-1">
              <li>You upload data at your own responsibility.</li>
              <li>Your data is stored to enable analysis and AI features.</li>
              <li>You can delete all your data anytime from the Dashboard.</li>
              <li>Please do not upload data you wouldn't be comfortable sharing.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
