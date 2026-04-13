import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function UploadAuth() {
  const [mode, setMode] = useState<"signup" | "login">("signup");
  const navigate = useNavigate();

  // Shared
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Signup-only
  const [fullName, setFullName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [accountName, setAccountName] = useState("");
  const [bank, setBank] = useState("aib");
  const [file, setFile] = useState<File | null>(null);

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (!file) {
      setError("Please select a CSV file");
      return;
    }

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
        navigate("/dashboard");
      } else {
        setError(data.detail || "Login failed");
      }
    } catch (err) {
      setError("Network error"+ err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="hero min-h-screen bg-gradient-to-r from-[#dfe2fe] via-[#b1cbfa] to-[#8e98f5]">
      <div className="hero-content text-center p-8 bg-base-100 rounded-lg shadow-lg w-full max-w-lg">
        <div className="w-full">
          <h1 className="mb-1 text-4xl font-bold">Expenses Tracker</h1>
          <p className="mb-6 text-sm">Upload your bank transactions to try the app</p>

          <div className="tabs tabs-boxed mb-4">
            <a className={`tab ${mode === "signup" ? "tab-active" : ""}`} onClick={() => setMode("signup")}>
              Sign up
            </a>
            <a className={`tab ${mode === "login" ? "tab-active" : ""}`} onClick={() => setMode("login")}>
              Log in
            </a>
          </div>

          {mode === "signup" ? (
            <form onSubmit={handleSignup} className="space-y-3 text-left">
              <input type="email" placeholder="Email" className="input input-bordered w-full"
                value={email} onChange={(e) => setEmail(e.target.value)} required />
              <input type="password" placeholder="Password" className="input input-bordered w-full"
                value={password} onChange={(e) => setPassword(e.target.value)} required />
              <input type="text" placeholder="Full name" className="input input-bordered w-full"
                value={fullName} onChange={(e) => setFullName(e.target.value)} required />
              <input type="tel" placeholder="Phone number (optional)" className="input input-bordered w-full"
                value={phoneNumber} onChange={(e) => setPhoneNumber(e.target.value)} />
              <input type="text" placeholder="Account name (e.g. AIB Current)" className="input input-bordered w-full"
                value={accountName} onChange={(e) => setAccountName(e.target.value)} required />
              <select className="select select-bordered w-full"
                value={bank} onChange={(e) => setBank(e.target.value)}>
                <option value="aib">AIB</option>
                <option value="revolut">Revolut</option>
              </select>
              <input type="file" accept=".csv,.html,.csv.html" className="file-input file-input-bordered w-full"
                onChange={(e) => setFile(e.target.files?.[0] || null)} required />

              {error && <p className="text-red-500 text-sm">{error}</p>}
              <button type="submit" className="btn btn-primary w-full" disabled={loading}>
                {loading ? "Setting up your dashboard..." : "Sign up & analyse"}
              </button>
              {loading && (
                <p className="text-xs text-gray-500 text-center">
                  This may take 15-30 seconds while we run the analysis pipeline.
                </p>
              )}
            </form>
          ) : (
            <form onSubmit={handleLogin} className="space-y-3 text-left">
              <input type="email" placeholder="Email" className="input input-bordered w-full"
                value={email} onChange={(e) => setEmail(e.target.value)} required />
              <input type="password" placeholder="Password" className="input input-bordered w-full"
                value={password} onChange={(e) => setPassword(e.target.value)} required />
              {error && <p className="text-red-500 text-sm">{error}</p>}
              <button type="submit" className="btn btn-primary w-full" disabled={loading}>
                {loading ? "Logging in..." : "Log in"}
              </button>
            </form>
          )}

          <button className="btn btn-ghost btn-sm mt-4" onClick={() => navigate("/")}>
            ← Back to Plaid login
          </button>
        </div>
      </div>
    </div>
  );
}