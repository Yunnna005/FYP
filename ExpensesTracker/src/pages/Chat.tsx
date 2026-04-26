import { useState, useRef, useEffect } from 'react';
import Template from '../templates/Template';
import { Navigate } from 'react-router-dom';
import BloomLogo from '../assets/logo-dark-removebg-preview.png';
import Avatar from '../assets/logo-dark-only-removebg-preview.png';
 
interface Message {
  role: 'user' | 'assistant';
  content: string;
  local?: string;
  gemini?: string;
}
 
const SUGGESTIONS = [
  "What did I spend most on last month?",
  "Show me my biggest transactions",
  "How is my cashflow trending?",
  "Which category costs me the most?",
];
 
export default function Chat() {
  const userId = localStorage.getItem("user_id");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
 
  if (!userId) return <Navigate to="/" replace />;
 
  // eslint-disable-next-line react-hooks/rules-of-hooks
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);
 
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    sendMessage(input);
  }
 
  async function sendMessage(text: string) {
    if (!text.trim()) return;
    const userMsg: Message = { role: 'user', content: text };
    setMessages((m) => [...m, userMsg]);
    setInput('');
    setLoading(true);
    try {
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, question: text }),
      });
      const data = await res.json();
      setMessages((m) => [
        ...m,
        {
          role: 'assistant',
          content: '',
          local: data.answer_local,
          gemini: data.answer_gemini,
        },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' },
      ]);
    } finally {
      setLoading(false);
    }
  }
 
  const isEmpty = messages.length === 0;
 
  return (
    <Template>
      <div
        className="flex flex-col h-screen"
        style={{ background: "#f5f3ff" }}
      >
        {/* Radial glow */}
        <div
          className="absolute pointer-events-none z-0"
          style={{
            width: "600px",
            height: "600px",
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 70%)",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
          }}
        />
 
        {/* Message area */}
        <div className="flex-1 overflow-y-auto px-6 py-6 relative">
 
          {/* Empty state — logo watermark + suggestions */}
          {isEmpty && (
            <div className="flex flex-col items-center justify-center h-full gap-6">
              <div className="flex flex-col items-center opacity-5">
                <img
                  src={BloomLogo}
                  alt="Bloom"
                  className="absolute w-94 h-94 object-contain z-1"
                  style={{ filter: "drop-shadow(0 0 28px rgba(167,139,250,0.4))" }}
                />
              </div>
 
              {/* Suggestion chips */}
              <div className="flex flex-wrap gap-2 justify-center max-w-lg">
                <p className="text-[24px] text-violet-900 text-center max-w-[460px] leading-relaxed" 
                style={{
                  fontFamily: "'Bagel Fat One', system-ui",
                  fontWeight: 100,
                  fontStyle: "normal"
                  }}>
                  Ask me anything about your finances
                </p>
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => sendMessage(s)}
                    className="text-[12px] font-medium text-violet-800/80 px-4 py-2 rounded-full border border-violet-900/40 hover:border-violet-200/60 hover:text-violet-700 hover:bg-violet-100/60"
                    style={{ background: "rgba(219, 204, 243, 0.26)" }}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
 
          {/* Messages */}
          {!isEmpty && (
            <div className="flex flex-col gap-4 max-w-2xl mx-auto">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex items-end gap-2.5 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                >
                  {/* Avatar */}
                  {msg.role === 'assistant' && (
                    <div
                      className="w-7 h-7 rounded-full flex-shrink-0 flex items-center justify-center"
                      style={{ background: "rgba(109,40,217,0.25)", border: "1px solid rgba(139,92,246,0.3)" }}
                    >
                      <img src={Avatar} alt="Bloom" className="w-5 h-5 object-contain" />
                    </div>
                  )}
 
                  {/* Bubble */}
                  <div
                    className={`px-4 py-3 rounded-2xl text-[13.5px] leading-relaxed max-w-[75%] ${
                      msg.role === 'user'
                        ? 'rounded-br-sm text-white'
                        : 'rounded-bl-sm text-[#3b3049]'
                    }`}
                    style={
                      msg.role === 'user'
                        ? {
                            background: "#7c3aed",
                            boxShadow: "0 4px 16px rgba(124,58,237,0.35)",
                          }
                        : {
                            background: "rgba(255,255,255,0.85)",
                            border: "1px solid rgba(139,92,246,0.15)",
                            color: "#3b3049",
                          }
                    }
                  >
                    {msg.role === 'assistant' && msg.local != null ? (
                      <>
                        <p className="font-semibold text-violet-700 mb-1 text-[12px] uppercase tracking-wide">LLM</p>
                        <p className="whitespace-pre-wrap">{msg.local}</p>
                        <hr className="my-3 border-violet-200/60" />
                        <p className="font-semibold text-blue-600 mb-1 text-[12px] uppercase tracking-wide">Gemini</p>
                        <p className="whitespace-pre-wrap">{msg.gemini}</p>
                      </>
                    ) : (
                      msg.content
                    )}
                  </div>
                </div>
              ))}
 
              {/* Loading bubble */}
              {loading && (
                <div className="flex items-end gap-2.5">
                  <div
                    className="w-7 h-7 rounded-full flex-shrink-0 flex items-center justify-center"
                    style={{ background: "rgba(109,40,217,0.25)", border: "1px solid rgba(139,92,246,0.3)" }}
                  >
                    <img src={BloomLogo} alt="Bloom" className="w-5 h-5 object-contain" />
                  </div>
                  <div
                    className="px-4 py-3 rounded-2xl rounded-bl-sm flex items-center gap-1.5"
                    style={{
                      background: "rgba(255,255,255,0.85)",
                      border: "1px solid rgba(139,92,246,0.15)",
                    }}
                  >
                    {[0, 1, 2].map((i) => (
                      <span
                        key={i}
                        className="w-1.5 h-1.5 rounded-full bg-violet-400"
                        style={{
                          animation: "bounce 1.2s ease-in-out infinite",
                          animationDelay: `${i * 0.2}s`,
                        }}
                      />
                    ))}
                  </div>
                </div>
              )}
 
              <div ref={bottomRef} />
            </div>
          )}
        </div>
 
        {/* Input bar */}
        <div
          className="relative px-6 pb-6 pt-3"
          style={{ borderTop: "1px solid rgba(139,92,246,0.12)", background: "#f5f3ff" }}
        >
          <style>{`
            @keyframes bounce {
              0%, 100% { transform: translateY(0); opacity: 0.5; }
              50% { transform: translateY(-4px); opacity: 1; }
            }
          `}</style>
          <form
            onSubmit={handleSubmit}
            className="flex gap-3 max-w-2xl mx-auto"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your finances…"
              disabled={loading}
              className="flex-1 px-4 py-3 rounded-2xl text-[13.5px] text-slate-700 placeholder-violet-400/50 outline-none transition-all duration-150 disabled:opacity-50"
              style={{
                background: "white",
                border: "1px solid rgba(139,92,246,0.25)",
                boxShadow: "0 1px 4px rgba(139,92,246,0.06)",
              }}
              onFocus={(e) => (e.currentTarget.style.border = "1px solid rgba(139,92,246,0.5)")}
              onBlur={(e) => (e.currentTarget.style.border = "1px solid rgba(139,92,246,0.25)")}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="w-11 h-11 rounded-2xl flex items-center justify-center flex-shrink-0 transition-all duration-150 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed"
              style={{
                background: "#7c3aed",
                boxShadow: input.trim() ? "0 0 20px rgba(124,58,237,0.4)" : "none",
              }}
              onMouseEnter={(e) => { if (!loading) (e.currentTarget as HTMLButtonElement).style.background = "#6d28d9"; }}
              onMouseLeave={(e) => { if (!loading) (e.currentTarget as HTMLButtonElement).style.background = "#7c3aed"; }}
            >
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="white" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </Template>
  );
}