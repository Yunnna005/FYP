import { Link, useNavigate, useLocation } from 'react-router-dom';
 
const navItems = [
  {
    label: "Dashboard",
    to: "/dashboard",
    icon: (
      <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
        <rect x="3" y="3" width="7" height="7" rx="1.5" />
        <rect x="14" y="3" width="7" height="7" rx="1.5" />
        <rect x="3" y="14" width="7" height="7" rx="1.5" />
        <rect x="14" y="14" width="7" height="7" rx="1.5" />
      </svg>
    ),
  },
  {
    label: "Chat",
    to: "/chat",
    icon: (
      <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    ),
  },
];
 
export default function NavBar() {
  const navigate = useNavigate();
  const location = useLocation();
 
  function handleLogout() {
    localStorage.removeItem("user_id");
    localStorage.removeItem("login_method");
    navigate("/");
  }
 
  return (
    <div
      className="fixed top-0 left-0 h-screen w-64 flex flex-col z-20"
      style={{
        background: "#0f0720",
        borderRight: "1px solid rgba(139,92,246,0.15)",
        boxShadow: "4px 0 24px rgba(0,0,0,0.3)",
      }}
    >
      {/* Subtle top glow */}
      <div
        className="absolute top-0 left-0 w-full h-40 pointer-events-none"
        style={{
          background: "radial-gradient(ellipse at 50% -20%, rgba(139,92,246,0.25) 0%, transparent 70%)",
        }}
      />
 
      {/* Logo area */}
      <div className="relative px-5 pt-7 pb-6 flex flex-col items-center border-b border-violet-500/10">
        <h1 className="text-[24px] font-bold text-violet-200 tracking-tight leading-snug text-center">
          Expenses Tracker
        </h1>
      </div>
 
      {/* Nav links */}
      <nav className="relative flex flex-col gap-1 px-3 pt-5 flex-1">
        {navItems.map(({ label, to, icon }) => {
          const isActive = location.pathname === to;
          return (
            <Link
              key={to}
              to={to}
              className={`flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? "text-white"
                  : "text-violet-300/60 hover:text-violet-200 hover:bg-violet-500/10"
              }`}
              style={
                isActive
                  ? {
                      background: "rgba(139,92,246,0.18)",
                      boxShadow: "0 0 0 1px rgba(139,92,246,0.25) inset",
                    }
                  : {}
              }
            >
              {/* Active indicator bar */}
              {isActive && (
                <span
                  className="absolute left-0 w-[3px] h-8 rounded-r-full bg-violet-400"
                  style={{ marginLeft: 0 }}
                />
              )}
              <span className={isActive ? "text-violet-300" : ""}>{icon}</span>
              {label}
            </Link>
          );
        })}
      </nav>
 
      {/* Bottom: logout */}
      <div className="relative px-3 pb-6 border-t border-violet-500/10 pt-4">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium text-rose-400/70 hover:text-rose-300 hover:bg-rose-500/10 transition-all duration-200"
        >
          <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          Log out
        </button>
      </div>
    </div>
  );
}