import { useEffect, useState } from "react";
import { usePlaidLink } from "react-plaid-link";
import { useNavigate } from "react-router-dom";

export default function Card() {
  const [linkToken, setLinkToken] = useState(null);
  const [loading, setLoading] = useState(false); 
  const navigate = useNavigate();

  useEffect(() => {
    fetch("/api/link/token/create", {
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => setLinkToken(data.link_token));
  }, []);

  const { open, ready } = usePlaidLink({
    token: linkToken,
    onSuccess: (public_token) => {
      setLoading(true);
      (async () => {
        try {
          // Exchange public token
          await fetch("/api/item/public_token/exchange", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ public_token }),
          });

          // Get email/phone from Plaid identity
          const idRes = await fetch("/api/identity/login");
          const { email, phone } = await idRes.json();

          // Look up the user_id in your DB
          const userRes = await fetch(
            `/api/account/user?email=${encodeURIComponent(email)}&phone=${encodeURIComponent(phone)}`
          );
          const user = await userRes.json();

          if (user?.user_id) {
            localStorage.setItem("user_id", user.user_id);
            localStorage.setItem("login_method", "plaid");
          }         

          navigate("/dashboard");
        } finally {
          setLoading(false);
        }
      })();
    },
  });

    return (
    <div
      className="relative flex flex-col items-center rounded-[22px] border border-violet-500/20 px-6 py-5 w-full"
      style={{
        background: "#160d2b",
        boxShadow: "0 24px 64px rgba(0,0,0,0.4), 0 0 0 1px rgba(167,139,250,0.08) inset",
      }}
    >
      {/* Icon ring */}
      <div
        className="w-12 h-12 rounded-full flex items-center justify-center mb-3 border border-violet-500/25"
        style={{ background: "rgba(109,40,217,0.15)" }}
      >
        <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="#a78bfa" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 21.0001H21M4 18.0001H20M6 18.0001V13.0001M10 18.0001V13.0001M14 18.0001V13.0001M18 18.0001V13.0001M12 7.00695L12.0074 7.00022M21 10.0001L14.126 3.88986C13.3737 3.2212 12.9976 2.88688 12.5732 2.75991C12.1992 2.64806 11.8008 2.64806 11.4268 2.75991C11.0024 2.88688 10.6263 3.2212 9.87404 3.88986L3 10.0001H21Z" />
        </svg>
      </div>
 
      <h2 className="text-[#e9e3ff] font-semibold text-[15px] mb-1.5 tracking-tight">
        Connect your bank
      </h2>
      <p className="text-[#9b8cc8] text-[12px] text-center leading-relaxed mb-4 max-w-[200px]">
        Link your account securely via Plaid to track expenses automatically.
      </p>
 
      {/* Feature icons */}
      <div className="flex gap-4 mb-4">
        {[
          { label: "Secure", icon: <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /> },
          { label: "Instant", icon: <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" /> },
          { label: "Live data", icon: <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10" /> },
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
        onClick={() => open()}
        disabled={!ready || loading}
        className="w-full py-[11px] rounded-xl font-semibold text-[13px] text-white flex items-center justify-center gap-2 transition-all duration-200 active:scale-[0.985] disabled:opacity-50 disabled:cursor-not-allowed"
        style={{
          background: loading ? "#5b21b6" : "#7c3aed",
          boxShadow: "0 0 20px rgba(139,92,246,0.3)",
        }}
        onMouseEnter={(e) => { if (!loading) (e.currentTarget as HTMLButtonElement).style.background = "#6d28d9"; }}
        onMouseLeave={(e) => { if (!loading) (e.currentTarget as HTMLButtonElement).style.background = "#7c3aed"; }}
      >
        {loading ? (
          <>
            <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
            </svg>
            Connecting...
          </>
        ) : (
          <>
            <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="white" strokeWidth={2}>
              <rect x="2" y="6" width="20" height="14" rx="3" stroke="white" strokeWidth={2} fill="none" />
              <path d="M2 10h20" stroke="white" strokeWidth={2} />
            </svg>
            Connect with Plaid
          </>
        )}
      </button>
 
      {/* Trust note */}
      <div className="flex items-center gap-1 mt-2.5">
        <svg width="10" height="10" fill="none" viewBox="0 0 24 24" stroke="#5a4a85" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <span className="text-[10px] text-[#5a4a85]">256-bit encrypted · read-only access</span>
      </div>
    </div>
  );
}