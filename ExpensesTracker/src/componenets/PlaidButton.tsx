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
          }

          navigate("/dashboard");
        } finally {
          setLoading(false);
        }
      })();
    },
  });

  return (
    <div className="relative">
      {/* Card UI */}
      <div className="card card-border bg-base-200 w-96">
        <div className="card-body items-center text-center">
          <h2 className="card-title">Connect your card</h2>
          <p>Track your expenses easily and securely.</p>
          <div className="card-actions justify-center">
            <button
              onClick={() => open()}
              disabled={!ready || loading} 
              className="btn btn-outline btn-info"
            >
              Connect
            </button>
          </div>
        </div>
      </div>

      {/* Loading overlay */}
      {loading && (
        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <span className="text-white text-lg">Connecting your account...</span>
        </div>
      )}
    </div>
  );
}
