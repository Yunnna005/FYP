import '../index.css'
import PlaidButton from "../componenets/PlaidButton";
import BloomLogo from "../assets/logo-only.png";
import UploadButton from "../componenets/Uploadbutton";

const icons = [
  // Credit card
  { 
    icon: <svg width="32" height="32" fill="none" viewBox="0 0 24 24"><rect x="2" y="6" width="20" height="14" rx="3" stroke="#c084fc" strokeWidth="1.5"/><path d="M2 10h20" stroke="#c084fc" strokeWidth="1.5"/><circle cx="6" cy="15" r="1" fill="#c084fc"/></svg>, 
    style: "top-[4%] left-[3%] w-16 h-16 bg-[#2a0f4f] -rotate-[8deg]", 
    delay: "0s" 
  },
  // Bar chart
  { 
    icon: <svg width="36" height="36" fill="none" viewBox="0 0 24 24"><rect x="3" y="11" width="4" height="10" rx="1" fill="#a855f7" opacity="0.85"/><rect x="10" y="6" width="4" height="15" rx="1" fill="#c084fc" opacity="0.9"/><rect x="17" y="2" width="4" height="19" rx="1" fill="#e0bbff"/></svg>, 
    style: "top-[55%] left-[4%] w-14 h-14 bg-[#2a0f4f] -rotate-[5deg]", 
    delay: "2s" 
  },
  // Dollar sign
  { 
    icon: <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><path d="M12 1v22M17 5H9.5a3.5 3.5 0 100 7h5a3.5 3.5 0 110 7H6" stroke="#c084fc" strokeWidth="1.5" strokeLinecap="round"/></svg>, 
    style: "top-[30%] left-[1%] w-16 h-16 bg-[#1f0a42] rotate-[12deg]", 
    delay: "0.6s" 
  },
  // Line chart
  { 
    icon: <svg width="36" height="36" fill="none" viewBox="0 0 24 24"><path d="M3 17l4-8 4 5 3-3 4 6" stroke="#d8b4fe" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>, 
    style: "bottom-[6%] left-[8%] w-12 h-12 bg-[#1f0a42] -rotate-[10deg]", 
    delay: "1.5s" 
  },
  // Wallet
  { 
    icon: <svg width="28" height="28" fill="none" viewBox="0 0 24 24"><path d="M20 7H4a2 2 0 00-2 2v6a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2z" stroke="#d8b4fe" strokeWidth="1.5"/><circle cx="12" cy="12" r="2" fill="#d8b4fe"/></svg>, 
    style: "top-[72%] left-[2%] w-14 h-14 bg-[#1a0638] rotate-[8deg]", 
    delay: "3s" 
  },
  // Multi-bar chart
  { 
    icon: <svg width="34" height="34" fill="none" viewBox="0 0 24 24"><path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" stroke="#c084fc" strokeWidth="1.5" strokeLinecap="round"/></svg>, 
    style: "top-[3%] right-[4%] w-16 h-16 bg-[#2a0f4f] rotate-[10deg]", 
    delay: "0.4s" 
  },
  // Coin/currency
  { 
    icon: <svg width="27" height="27" fill="none" viewBox="0 0 24 24"><path d="M12 8c-2.21 0-4 1.12-4 2.5S9.79 13 12 13s4 1.12 4 2.5-1.79 2.5-4 2.5M12 8v1m0 6v1m0-8V4m0 16v-3" stroke="#a855f7" strokeWidth="1.5" strokeLinecap="round"/></svg>, 
    style: "top-[16%] right-[2%] w-14 h-14 bg-[#1a0638] -rotate-[6deg]", 
    delay: "1.8s" 
  },
  // Shopping cart
  { 
    icon: <svg width="38" height="38" fill="none" viewBox="0 0 24 24"><path d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2 5h14" stroke="#e0bbff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>, 
    style: "top-[35%] right-[3%] w-20 h-20 bg-[#1f0a42] -rotate-[12deg]", 
    delay: "0.9s" 
  },
  // Lightning bolt
  { 
    icon: <svg width="29" height="29" fill="none" viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" stroke="#c084fc" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>, 
    style: "top-[57%] right-[1%] w-14 h-14 bg-[#2a0f4f] rotate-[7deg]", 
    delay: "2.4s" 
  },
  // Shield
  { 
    icon: <svg width="31" height="31" fill="none" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="#d8b4fe" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>, 
    style: "top-[74%] right-[5%] w-14 h-14 bg-[#1a0638] -rotate-[3deg]", 
    delay: "3.5s" 
  },
  // Receipt
  { 
    icon: <svg width="23" height="23" fill="none" viewBox="0 0 24 24"><path d="M7 10h10M7 14h6" stroke="#c084fc" strokeWidth="1.5" strokeLinecap="round"/><rect x="3" y="4" width="18" height="16" rx="3" stroke="#c084fc" strokeWidth="1.5"/></svg>, 
    style: "top-[8%] left-[22%] w-12 h-12 bg-[#200a40] rotate-[15deg]", 
    delay: "2.8s" 
  },
  // Coin circle
  { 
    icon: <svg width="31" height="31" fill="none" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" stroke="#a855f7" strokeWidth="1.5"/><path d="M15 9.354a4 4 0 100 5.292" stroke="#a855f7" strokeWidth="1.5" strokeLinecap="round"/></svg>, 
    style: "bottom-[5%] right-[3%] w-14 h-14 bg-[#1f0a42] rotate-[9deg]", 
    delay: "1s" 
  },
];

export default function Login() {

  return (
    <div className="h-screen flex items-center justify-center relative overflow-hidden bg-[#0a0118]">
 
      {/* Floating finance icons */}
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
        className="absolute w-[560px] h-[560px] rounded-full pointer-events-none z-0"
        style={{
          background: "radial-gradient(circle, rgba(167,139,250,0.2) 0%, transparent 65%)",
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
 
      {/* Outer card */}
      <div className="relative z-10 w-full max-w-[860px] mx-4">
        <div
          className="bg-[#160d2b] rounded-[2rem] border border-[#3b2a5f]/80 px-8 py-6 flex flex-col items-center backdrop-blur-xl"
          style={{
            boxShadow: `
              0 40px 100px -15px rgba(0,0,0,0.75),
              0 0 0 1px rgba(167,139,250,0.1) inset
            `,
          }}
        >
          {/* Logo */}
          <img
            src={BloomLogo}
            alt="Bloom"
            className="w-48 h-48 object-contain mb-1 drop-shadow-[0_8px_30px_rgba(167,139,250,0.35)]"
          />

          <p
            className="text-center text-[48px]"
            style={{
              fontFamily: "'Bagel Fat One', system-ui",
              fontWeight: 400,
              fontStyle: "normal",
              fontSize: "48px",
              color: "#c084fc",
              letterSpacing: "2px",
              textShadow: "0 0 40px rgba(192,132,252,0.5)",
            }}
          >
            BLOOM
          </p>
 
          {/* Tagline */}
          <p className="text-center text-[#b8b0d8] text-[16px] mb-5 leading-relaxed max-w-[400px]">
            AI-powered expenses tracker with banking integration
          </p>
 
          {/* Two-column cards */}
          <div className="grid grid-cols-2 gap-4 w-full">
            <PlaidButton />
            <UploadButton />
          </div>
 
          {/* Privacy note */}
          <div className="flex items-center gap-1.5 mt-4">
            <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" fill="none" viewBox="0 0 24 24" stroke="#5a4a85" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            <p className="text-[10.5px] text-[#5a4a85]">
              Your data is private and secure · delete it anytime from the Dashboard
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}