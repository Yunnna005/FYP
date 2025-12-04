import { useEffect, useState } from "react";
import { usePlaidLink } from "react-plaid-link";
import { useNavigate } from "react-router-dom";

export default function Card(){
    const [linkToken, setLinkToken] = useState(null);
    const navigate = useNavigate();

      useEffect(() => {
    fetch("http://localhost:8000/link/token/create", {
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => setLinkToken(data.link_token));
  }, []);

  const { open, ready } = usePlaidLink({
    token: linkToken,
    onSuccess: (public_token) => {
      fetch("http://localhost:8000/item/public_token/exchange", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ public_token }),
      })
        .then((res) => res.json())
        .then((data) => console.log("access_token:", data.access_token));

        navigate("/dashboard");
    },
  });

    return <div className="card card-border bg-base-200 w-96">
  <div className="card-body items-center text-center">
    <h2 className="card-title">Connect your card</h2>
    <p>Track your expenses easily and securely.</p>
    <div className="card-actions justify-center">
      <button  onClick={() => open()} disabled={!ready} className="btn btn-outline btn-info">Connect</button>
    </div>
  </div>
</div>
}