import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";

// ── CONFIG ────────────────────────────────────────────────────────
const ANON_HASH = () => Math.random().toString(36).slice(2, 14);
const userHash = ANON_HASH();

// ── STATIONS ─────────────────────────────────────────────────────
const ALL_STATIONS = [
  "Virar","Nala Sopara","Vasai Road","Bhayander","Mira Road","Dahisar",
  "Borivali","Kandivali","Malad","Goregaon","Jogeshwari","Andheri",
  "Vile Parle","Santacruz","Khar Road","Bandra","Mahim","Matunga Road",
  "Dadar","Lower Parel","Mahalaxmi","Mumbai Central","Grant Road","Churchgate",
  "Kasara","Karjat","Kalyan","Dombivli","Thane","Mulund","Bhandup",
  "Vikhroli","Ghatkopar","Kurla","Sion","Matunga","Byculla","CST",
  "Panvel","Vashi","Belapur"
];

// ── ICONS ────────────────────────────────────────────────────────
const IconSearch  = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>;
const IconTrain   = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><rect x="4" y="3" width="16" height="13" rx="2"/><path d="M8 19h8M12 16v3M4 10h16"/></svg>;
const IconBot     = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><path d="M12 2a5 5 0 0 1 5 5v2H7V7a5 5 0 0 1 5-5z"/><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="9" cy="16" r="1" fill="currentColor"/><circle cx="15" cy="16" r="1" fill="currentColor"/></svg>;
const IconSwap    = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><path d="M7 16V4m0 0L3 8m4-4 4 4M17 8v12m0 0 4-4m-4 4-4-4"/></svg>;
const IconClock   = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>;
const IconSend    = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>;
const IconInfo    = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>;
const IconX       = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>;
const IconCheck   = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5"><polyline points="20 6 9 16 4 11"/></svg>;

// ── BADGE COMPONENT ──────────────────────────────────────────────
function CrowdBadge({ badge, label, animate = false }) {
  const config = {
    RED:    { bg: "bg-red-500",    text: "text-white", dot: "bg-red-300",    ring: "ring-red-200" },
    YELLOW: { bg: "bg-amber-400",  text: "text-white", dot: "bg-amber-200",  ring: "ring-amber-100" },
    GREEN:  { bg: "bg-emerald-500",text: "text-white", dot: "bg-emerald-300",ring: "ring-emerald-100" },
  }[badge] || { bg: "bg-gray-400", text: "text-white", dot: "bg-gray-200", ring: "ring-gray-100" };

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${config.bg} ${config.text} ring-2 ${config.ring} ${animate ? "animate-pulse" : ""}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`}></span>
      {label}
    </span>
  );
}

// ── STATION AUTOCOMPLETE ─────────────────────────────────────────
function StationInput({ label, value, onChange, placeholder }) {
  const [open, setOpen] = useState(false);
  const [filtered, setFiltered] = useState([]);
  const ref = useRef();

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleInput = (v) => {
    onChange(v);
    if (v.length >= 2) {
      setFiltered(ALL_STATIONS.filter(s => s.toLowerCase().startsWith(v.toLowerCase())).slice(0, 6));
      setOpen(true);
    } else {
      setOpen(false);
    }
  };

  return (
    <div className="relative" ref={ref}>
      <label className="text-[10px] text-blue-300 font-semibold uppercase tracking-widest pl-1">{label}</label>
      <input
        value={value}
        onChange={e => handleInput(e.target.value)}
        onFocus={() => value.length >= 2 && setOpen(true)}
        placeholder={placeholder}
        className="w-full bg-blue-800/60 text-white placeholder-blue-400 text-sm font-medium px-3 py-2.5 rounded-lg border border-blue-600/50 focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400 mt-1"
      />
      {open && filtered.length > 0 && (
        <div className="absolute z-50 top-full mt-1 left-0 right-0 bg-blue-900 border border-blue-600 rounded-lg shadow-xl overflow-hidden">
          {filtered.map(s => (
            <button key={s} onClick={() => { onChange(s); setOpen(false); }}
              className="w-full text-left px-3 py-2 text-sm text-white hover:bg-blue-700 transition-colors border-b border-blue-800/50 last:border-0">
              {s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// ── TRAIN CARD ───────────────────────────────────────────────────
function TrainCard({ train, onTap, isRecommended }) {
  const lineColor = { WR: "bg-blue-600", CR: "bg-orange-500", HR: "bg-green-600" }[train.line] || "bg-gray-500";
  const badgeBorder = { RED: "border-l-red-500", YELLOW: "border-l-amber-400", GREEN: "border-l-emerald-500" }[train.badge];

  return (
    <button
      onClick={() => onTap(train)}
      className={`w-full text-left bg-white rounded-xl shadow-sm border border-gray-100 p-4 transition-all active:scale-98 hover:shadow-md relative overflow-hidden border-l-4 ${badgeBorder} ${isRecommended ? "ring-2 ring-blue-500 ring-offset-1" : ""}`}
    >
      {isRecommended && (
        <div className="absolute top-0 right-0 bg-blue-500 text-white text-[9px] font-bold px-2 py-0.5 rounded-bl-lg">
          RECOMMENDED
        </div>
      )}
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-[9px] text-white font-bold px-1.5 py-0.5 rounded ${lineColor}`}>
              {train.line}
            </span>
            <span className="text-xs text-gray-400 font-medium">{train.train_type}</span>
            {train.report_count > 0 && (
              <span className="text-[9px] text-gray-400 flex items-center gap-0.5">
                <IconInfo /> {train.report_count} reports
              </span>
            )}
          </div>
          <div className="text-base font-bold text-gray-900">{train.train_name}</div>
          <div className="text-xs text-gray-500 mt-0.5">Train #{train.train_number}</div>
        </div>
        <div className="text-right shrink-0">
          <div className="text-2xl font-black text-gray-900 tabular-nums">{train.depart}</div>
          <div className="text-[10px] text-gray-400">Plt {train.platform}</div>
        </div>
      </div>
      <div className="flex items-center justify-between mt-3 pt-2.5 border-t border-gray-100">
        <div className="flex-1 min-w-0 pr-3">
          <p className="text-xs text-gray-500 leading-relaxed truncate">{train.reason}</p>
        </div>
        <CrowdBadge badge={train.badge} label={train.badge_label} />
      </div>
    </button>
  );
}

// ── CROWD PROMPT SHEET ───────────────────────────────────────────
function CrowdPromptSheet({ train, onClose }) {
  const [step, setStep] = useState(1);
  const [submitted, setSubmitted] = useState(false);
  const [updatedBadge, setUpdatedBadge] = useState(null);
  const [helpCount, setHelpCount] = useState(null);

  const handleBoarding = (yes) => {
    if (!yes) { onClose(); return; }
    setStep(2);
  };

  const handleCrowdLevel = async (level) => {
    setSubmitted(true);
    try {
      const res = await fetch("/api/trains/report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          train_number: train.train_number,
          train_name: train.train_name,
          line: train.line,
          origin: train.origin,
          destination: train.destination,
          crowd_level: level,
          user_hash: userHash,
        }),
      });
      const data = await res.json();
      setUpdatedBadge(data.updated_badge);
      setHelpCount(data.message);
    } catch {
      setHelpCount("Thanks for reporting!");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full bg-white rounded-t-2xl shadow-2xl p-6 pb-10 animate-slide-up">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
          <IconX />
        </button>

        {/* Train summary */}
        <div className="flex items-center gap-3 mb-5 pb-4 border-b border-gray-100">
          <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600">
            <IconTrain />
          </div>
          <div>
            <div className="font-bold text-gray-900">{train.train_name}</div>
            <div className="text-xs text-gray-500">{train.origin} → {train.destination} · {train.depart} · Plt {train.platform}</div>
          </div>
          <div className="ml-auto">
            <CrowdBadge badge={updatedBadge || train.badge} label={train.badge_label} animate={!!updatedBadge} />
          </div>
        </div>

        {/* Step 1 — Boarding? */}
        {step === 1 && (
          <div>
            <p className="text-base font-semibold text-gray-900 mb-1">Are you boarding this train right now?</p>
            <p className="text-xs text-gray-400 mb-5">Your feedback helps commuters on this route in real time.</p>
            <div className="flex gap-3">
              <button onClick={() => handleBoarding(true)}
                className="flex-1 bg-blue-600 text-white font-semibold py-3 rounded-xl text-sm hover:bg-blue-700 transition-colors">
                Yes, I'm boarding
              </button>
              <button onClick={() => handleBoarding(false)}
                className="flex-1 bg-gray-100 text-gray-600 font-semibold py-3 rounded-xl text-sm hover:bg-gray-200 transition-colors">
                Just planning
              </button>
            </div>
          </div>
        )}

        {/* Step 2 — How crowded? */}
        {step === 2 && !submitted && (
          <div>
            <p className="text-base font-semibold text-gray-900 mb-1">How crowded is it?</p>
            <p className="text-xs text-gray-400 mb-5">Takes 1 second. Helps the next person decide.</p>
            <div className="flex flex-col gap-2.5">
              {[
                { level: "RED",    label: "Very crowded",  sub: "Dangerous, avoid if possible", bg: "bg-red-50 border-red-200 hover:bg-red-100" },
                { level: "YELLOW", label: "Moderate",      sub: "Can board, a bit of jostling",  bg: "bg-amber-50 border-amber-200 hover:bg-amber-100" },
                { level: "GREEN",  label: "Comfortable",   sub: "Plenty of space",               bg: "bg-emerald-50 border-emerald-200 hover:bg-emerald-100" },
              ].map(({ level, label, sub, bg }) => (
                <button key={level} onClick={() => handleCrowdLevel(level)}
                  className={`flex items-center gap-3 p-3.5 rounded-xl border-2 text-left transition-all ${bg}`}>
                  <CrowdBadge badge={level} label={level} />
                  <div>
                    <div className="text-sm font-semibold text-gray-900">{label}</div>
                    <div className="text-xs text-gray-500">{sub}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 3 — Thank you */}
        {submitted && (
          <div className="text-center py-4">
            <div className="w-14 h-14 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-3 text-emerald-600">
              <IconCheck />
            </div>
            <p className="font-bold text-gray-900 text-base mb-1">Reported!</p>
            <p className="text-sm text-gray-500">{helpCount}</p>
            {updatedBadge && (
              <div className="mt-3 flex items-center justify-center gap-2 text-xs text-gray-500">
                Badge updated to <CrowdBadge badge={updatedBadge} label={updatedBadge} />
              </div>
            )}
            <button onClick={onClose} className="mt-5 w-full bg-blue-600 text-white font-semibold py-3 rounded-xl text-sm">
              Back to results
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// ── SIGNAL DETAIL CARDS ──────────────────────────────────────────
function SignalCard({ icon, title, value, sub, color }) {
  return (
    <div className={`flex-1 rounded-xl p-3 border ${color}`}>
      <div className="text-lg mb-1">{icon}</div>
      <div className="text-[10px] text-gray-500 uppercase font-bold tracking-wide">{title}</div>
      <div className="text-sm font-bold text-gray-900 mt-0.5">{value}</div>
      {sub && <div className="text-[10px] text-gray-400 mt-0.5 leading-tight">{sub}</div>}
    </div>
  );
}

// ── MAIN APP ─────────────────────────────────────────────────────
export default function App() {
  const [tab, setTab] = useState("trains");
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [datetime, setDatetime] = useState(() => new Date().toISOString().slice(0, 16));
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [selectedTrain, setSelectedTrain] = useState(null);
  const [detailTrain, setDetailTrain] = useState(null);
  const [error, setError] = useState("");

  // Bot state
  const [botMessages, setBotMessages] = useState([
    { role: "assistant", content: "Namaste! I'm Jan Suraksha Bot. If you faced a problem on a Mumbai local — overcrowding, harassment, injury, delay — I'll help you file a formal complaint and claim compensation. Tell me what happened." }
  ]);
  const [botInput, setBotInput] = useState("");
  const [botLoading, setBotLoading] = useState(false);
  const botRef = useRef();

  const swapStations = () => {
    const tmp = origin;
    setOrigin(destination);
    setDestination(tmp);
  };

  const handleSearch = async () => {
    if (!origin || !destination) { setError("Please enter both origin and destination."); return; }
    if (origin === destination) { setError("Origin and destination cannot be the same."); return; }
    setError("");
    setLoading(true);
    setResults(null);
    setDetailTrain(null);

    try {
      const res = await fetch("/api/trains/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          origin,
          destination,
          datetime_str: new Date(datetime).toISOString().slice(0, 19),
        }),
      });
      const data = await res.json();
      setResults(data);
    } catch {
      setResults(getMockResults(origin, destination));
    } finally {
      setLoading(false);
    }
  };

  const sendBotMessage = async () => {
    if (!botInput.trim()) return;
    const msg = botInput.trim();
    setBotInput("");
    setBotMessages(prev => [...prev, { role: "user", content: msg }]);
    setBotLoading(true);

    try {
      const res = await fetch("/api/bot/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "railflow_user",
          message: msg,
          language: "en",
        }),
      });
      const data = await res.json();
      const botMsg = {
        role: "assistant",
        content: data.response || "Processing your complaint...",
        options: data.options || null,
        complaint_draft: data.complaint_draft,
        authority: data.authority,
        compensation: data.compensation,
      };
      setBotMessages(prev => [...prev, botMsg]);
    } catch {
      setBotMessages(prev => [...prev, {
        role: "assistant",
        content: "I'm connecting to the grievance system. Please describe the incident — train number, station, and what happened."
      }]);
    } finally {
      setBotLoading(false);
      setTimeout(() => botRef.current?.scrollIntoView({ behavior: "smooth" }), 100);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 max-w-sm mx-auto relative">

      {/* ── HEADER ── */}
      <div className="bg-gradient-to-b from-blue-700 to-blue-800 pt-10 pb-4 px-4 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-white/20 flex items-center justify-center">
                <span className="text-white font-black text-xs">m</span>
              </div>
              <span className="text-white font-black text-lg tracking-tight">Indicator</span>
              <span className="text-blue-300 text-xs font-semibold bg-blue-600/60 px-1.5 py-0.5 rounded">AI</span>
            </div>
            <p className="text-blue-300 text-[10px] mt-0.5">Mumbai Local · Powered by RailFlow</p>
          </div>
          <div className="text-right">
            <div className="text-white text-xs font-semibold">
              {new Date().toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short" })}
            </div>
            <div className="text-blue-300 text-[10px]">
              {new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
            </div>
          </div>
        </div>

        {tab === "trains" && (
          <div className="space-y-3">
            <div className="flex gap-2 items-end">
              <div className="flex-1 space-y-2">
                <StationInput label="From" value={origin} onChange={setOrigin} placeholder="Borivali, Virar..." />
                <StationInput label="To" value={destination} onChange={setDestination} placeholder="Churchgate, CST..." />
              </div>
              <button onClick={swapStations}
                className="mb-0.5 w-9 h-9 rounded-lg bg-blue-600/60 border border-blue-500 flex items-center justify-center text-blue-200 hover:bg-blue-600 transition-colors">
                <IconSwap />
              </button>
            </div>
            <div className="flex gap-2">
              <div className="flex-1">
                <label className="text-[10px] text-blue-300 font-semibold uppercase tracking-widest pl-1">When</label>
                <div className="relative mt-1">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2 text-blue-400"><IconClock /></div>
                  <input type="datetime-local" value={datetime} onChange={e => setDatetime(e.target.value)}
                    className="w-full bg-blue-800/60 text-white text-sm font-medium pl-9 pr-3 py-2.5 rounded-lg border border-blue-600/50 focus:outline-none focus:border-blue-400" />
                </div>
              </div>
              <div className="flex items-end">
                <button onClick={handleSearch} disabled={loading}
                  className="h-10 px-5 bg-white text-blue-700 font-bold text-sm rounded-lg shadow hover:shadow-md active:scale-95 transition-all disabled:opacity-60 flex items-center gap-2">
                  {loading ? (
                    <span className="w-4 h-4 border-2 border-blue-600/30 border-t-blue-600 rounded-full animate-spin" />
                  ) : <IconSearch />}
                  Search
                </button>
              </div>
            </div>
            {error && <p className="text-red-300 text-xs pl-1">{error}</p>}
          </div>
        )}

        {tab === "bot" && (
          <div className="pt-2">
            <p className="text-white font-bold text-base">Jan Suraksha Bot</p>
            <p className="text-blue-300 text-xs mt-0.5">File complaints · Claim compensation · Know your rights</p>
          </div>
        )}
      </div>

      {/* ── BODY ── */}
      <div className="pb-24">
        {tab === "trains" && (
          <div>
            {/* Results */}
            {results && !detailTrain && (
              <div className="px-3 pt-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="text-xs font-bold text-gray-900">{results.origin} → {results.destination}</p>
                    <p className="text-[10px] text-gray-400 capitalize">
                      {results.day_type} · {results.trains?.length || 0} trains found
                      {results.total_route_reports > 0 && ` · ${results.total_route_reports} crowd reports`}
                    </p>
                  </div>
                  <div className="flex gap-1.5 text-[9px] text-gray-500">
                    <span>🟢 Safe</span> <span>🟡 Caution</span> <span>🔴 Avoid</span>
                  </div>
                </div>

                {results.trains?.length > 0 ? (
                  <div className="space-y-2.5">
                    {results.trains.map((train, i) => (
                      <TrainCard key={train.train_number} train={train} isRecommended={i === 0}
                        onTap={(t) => { setSelectedTrain(t); setDetailTrain(null); }} />
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-400">
                    <div className="text-4xl mb-2">🚂</div>
                    <p className="text-sm font-medium">No trains found</p>
                    <p className="text-xs mt-1">Try adjusting your route or time</p>
                  </div>
                )}

                <div className="mt-4 bg-blue-50 border border-blue-100 rounded-xl p-3 flex gap-2.5">
                  <span className="text-blue-500 shrink-0 mt-0.5"><IconInfo /></span>
                  <p className="text-xs text-blue-700 leading-relaxed">
                    <strong>How badges work:</strong> Crowd scores combine crowd trend patterns, weather, and historical reports from commuters like you. Tap any train to report your experience.
                  </p>
                </div>
              </div>
            )}

            {/* Train Detail */}
            {detailTrain && (
              <div className="px-3 pt-4">
                <button onClick={() => setDetailTrain(null)} className="flex items-center gap-1 text-blue-600 text-sm font-semibold mb-4">
                  ← Back to results
                </button>
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                  <div className={`p-4 border-l-4 ${{ RED: "border-red-500 bg-red-50", YELLOW: "border-amber-400 bg-amber-50", GREEN: "border-emerald-500 bg-emerald-50" }[detailTrain.badge]}`}>
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="text-xl font-black text-gray-900">{detailTrain.train_name}</div>
                        <div className="text-xs text-gray-500 mt-0.5">#{detailTrain.train_number} · {detailTrain.train_type} · {detailTrain.line}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-black text-gray-900">{detailTrain.depart}</div>
                        <div className="text-xs text-gray-400">Platform {detailTrain.platform}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 mt-3">
                      <CrowdBadge badge={detailTrain.badge} label={detailTrain.badge_label} />
                      <span className="text-xs text-gray-600">Crowd Score: {detailTrain.badge_score}/100</span>
                    </div>
                    <p className="text-sm text-gray-700 mt-2 leading-relaxed">{detailTrain.reason}</p>
                  </div>
                  <div className="p-4">
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-3">What drove this score</p>
                    <div className="flex gap-2">
                      <SignalCard icon="📊" title="Reports" color="bg-gray-50 border-gray-200"
                        value={detailTrain.signals?.historical?.total > 0 ? `${detailTrain.signals.historical.total} reports` : "No data yet"}
                        sub={detailTrain.signals?.historical?.description} />
                      <SignalCard icon="📈" title="Trend" color="bg-gray-50 border-gray-200"
                        value={detailTrain.signals?.crowd_trend?.trend ? detailTrain.signals.crowd_trend.trend.charAt(0).toUpperCase() + detailTrain.signals.crowd_trend.trend.slice(1) : "Stable"}
                        sub={detailTrain.signals?.crowd_trend?.description} />
                      <SignalCard icon="🌧" title="Weather" color="bg-gray-50 border-gray-200"
                        value={detailTrain.signals?.weather?.condition || "Clear"}
                        sub={detailTrain.signals?.weather?.description} />
                    </div>
                  </div>
                  <div className="px-4 pb-4">
                    <button onClick={() => { setSelectedTrain(detailTrain); setDetailTrain(null); }}
                      className="w-full bg-blue-600 text-white font-bold py-3 rounded-xl text-sm hover:bg-blue-700 transition-colors">
                      Report crowd for this train
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Empty state */}
            {!results && !loading && (
              <div className="px-4 pt-8 text-center">
                <div className="text-5xl mb-3">🚉</div>
                <p className="text-base font-bold text-gray-700">Smart Train Search</p>
                <p className="text-sm text-gray-400 mt-1 leading-relaxed">
                  Find trains with real-time crowd intelligence.<br/>
                  Powered by commuter reports + crowd trends.
                </p>
                <div className="mt-6 grid grid-cols-3 gap-2 text-center">
                  {[
                    { emoji: "🟢", text: "Avoid crush" },
                    { emoji: "📊", text: "Live data" },
                    { emoji: "🤝", text: "Community" },
                  ].map(({ emoji, text }) => (
                    <div key={text} className="bg-white rounded-xl p-3 border border-gray-100 shadow-sm">
                      <div className="text-2xl mb-1">{emoji}</div>
                      <div className="text-xs font-semibold text-gray-600">{text}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── BOT TAB ── */}
        {tab === "bot" && (
          <div className="flex flex-col h-[calc(100vh-200px)]">
            <div className="flex-1 overflow-y-auto px-3 py-4 space-y-3">
              {botMessages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  {msg.role === "assistant" && (
                    <div className="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center mr-2 shrink-0 mt-0.5 text-blue-600">
                      <IconBot />
                    </div>
                  )}
                  <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white rounded-tr-sm"
                      : "bg-white text-gray-800 border border-gray-100 shadow-sm rounded-tl-sm"
                  }`}>
                    {msg.role === "assistant" ? (
                      <div className="space-y-2">
                        <div className="prose prose-sm max-w-none">
                          <ReactMarkdown>{msg.content}</ReactMarkdown>
                        </div>
                        {msg.options && msg.options.length > 0 && (
                          <div className="mt-2 flex flex-col gap-1.5">
                            {msg.options.map((opt, idx) => (
                              <button key={opt.id || idx}
                                onClick={() => { setBotInput(String(idx + 1)); sendBotMessage(); }}
                                className="text-left bg-blue-50 border border-blue-200 rounded-lg px-3 py-2 text-xs hover:bg-blue-100 transition-colors">
                                <span className="font-semibold">{idx + 1}. {opt.label}</span>
                                {opt.description && <span className="text-gray-500 ml-1">— {opt.description}</span>}
                              </button>
                            ))}
                          </div>
                        )}
                        {msg.complaint_draft && (
                          <details className="mt-2 bg-gray-50 rounded-lg border border-gray-200">
                            <summary className="px-3 py-2 text-xs font-semibold text-gray-600 cursor-pointer">View Complaint Draft</summary>
                            <div className="px-3 py-2 text-xs whitespace-pre-wrap border-t border-gray-100">{msg.complaint_draft}</div>
                          </details>
                        )}
                        <div className="flex flex-wrap gap-1">
                          {msg.authority && <span className="text-[10px] bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">Authority: {msg.authority}</span>}
                          {msg.compensation && <span className="text-[10px] bg-green-100 text-green-700 px-2 py-0.5 rounded-full">{msg.compensation}</span>}
                        </div>
                      </div>
                    ) : msg.content}
                  </div>
                </div>
              ))}
              {botLoading && (
                <div className="flex justify-start">
                  <div className="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center mr-2 text-blue-600"><IconBot /></div>
                  <div className="bg-white border border-gray-100 shadow-sm rounded-2xl rounded-tl-sm px-4 py-3">
                    <span className="flex gap-1">
                      {[0,1,2].map(i => <span key={i} className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: `${i*0.15}s` }} />)}
                    </span>
                  </div>
                </div>
              )}
              <div ref={botRef} />
            </div>
            <div className="px-3 pb-4 bg-gray-50 border-t border-gray-200 pt-3">
              {results?.origin && (
                <div className="flex items-center gap-1.5 text-[10px] text-blue-600 bg-blue-50 rounded-lg px-2.5 py-1.5 mb-2 border border-blue-100">
                  <IconTrain /> Context: {results.origin} → {results.destination} loaded
                </div>
              )}
              <div className="flex gap-2">
                <input value={botInput} onChange={e => setBotInput(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && !e.shiftKey && sendBotMessage()}
                  placeholder="Describe your incident..."
                  className="flex-1 bg-white border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400" />
                <button onClick={sendBotMessage}
                  className="w-10 h-10 bg-blue-600 text-white rounded-xl flex items-center justify-center hover:bg-blue-700 transition-colors">
                  <IconSend />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ── BOTTOM NAV ── */}
      <div className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-sm bg-white border-t border-gray-200 flex shadow-lg z-40">
        {[
          { id: "trains", label: "Trains",   icon: <IconTrain /> },
          { id: "bot",    label: "Suraksha", icon: <IconBot /> },
        ].map(({ id, label, icon }) => (
          <button key={id} onClick={() => setTab(id)}
            className={`flex-1 flex flex-col items-center justify-center py-3 gap-1 transition-colors ${
              tab === id ? "text-blue-600" : "text-gray-400"
            }`}>
            {icon}
            <span className="text-[10px] font-semibold">{label}</span>
            {tab === id && <span className="absolute bottom-1 w-5 h-0.5 bg-blue-600 rounded-full" />}
          </button>
        ))}
      </div>

      {/* ── CROWD PROMPT OVERLAY ── */}
      {selectedTrain && (
        <CrowdPromptSheet train={selectedTrain} onClose={() => setSelectedTrain(null)} />
      )}

      <style>{`
        @keyframes slide-up {
          from { transform: translateY(100%); }
          to { transform: translateY(0); }
        }
        .animate-slide-up { animation: slide-up 0.3s cubic-bezier(0.32, 0.72, 0, 1); }
        input[type="datetime-local"]::-webkit-calendar-picker-indicator { filter: invert(1) opacity(0.5); }
      `}</style>
    </div>
  );
}

// ── MOCK DATA (fallback when backend offline) ────────────────────
function getMockResults(origin, destination) {
  const isWR = ["Virar","Borivali","Andheri","Goregaon","Malad","Bandra","Churchgate"].some(s =>
    origin.includes(s) || destination.includes(s)
  );
  return {
    origin, destination, day_type: "weekday", total_route_reports: 47,
    trains: [
      {
        train_number: "90011", train_name: "Borivali Fast", train_type: "FAST",
        line: isWR ? "WR" : "CR", origin, destination,
        depart: "08:12", platform: 3,
        badge: "GREEN", badge_label: "Safe", badge_color: "#22C55E", badge_score: 28,
        reason: "Usually comfortable at this hour — 31 of 37 past reports say spacious.",
        report_count: 37,
        signals: {
          historical: { score: 22, total: 37, description: "Usually comfortable — 84% of 37 reports say spacious", confidence: "high" },
          crowd_trend: { score: 10, trend: "improving", description: "Less crowded lately — only 12% packed vs 22% usual" },
          weather: { condition: "clear", score: 0, description: "Clear — no weather impact" }
        }
      },
      {
        train_number: "90013", train_name: "Virar Fast", train_type: "FAST",
        line: isWR ? "WR" : "CR", origin, destination,
        depart: "08:05", platform: 1,
        badge: "RED", badge_label: "Avoid", badge_color: "#EF4444", badge_score: 87,
        reason: "Monday surge + 14-min gap before this train — absorbs previous crowd.",
        report_count: 52,
        signals: {
          historical: { score: 92, total: 52, description: "Historically very crowded — 71% of 52 reports say packed", confidence: "high" },
          crowd_trend: { score: 85, trend: "spiking", description: "Crowd surge detected — 82% packed this week vs 61% average" },
          weather: { condition: "clear", score: 0, description: "Clear — no weather impact" }
        }
      },
      {
        train_number: "90015", train_name: "Virar Fast", train_type: "FAST",
        line: isWR ? "WR" : "CR", origin, destination,
        depart: "08:18", platform: 2,
        badge: "YELLOW", badge_label: "Caution", badge_color: "#F59E0B", badge_score: 55,
        reason: "Moderate on this slot — crowd normalises slightly after 8:10.",
        report_count: 28,
        signals: {
          historical: { score: 58, total: 28, description: "Moderately crowded based on 28 past reports", confidence: "medium" },
          crowd_trend: { score: 30, trend: "stable", description: "Normal pattern — 8 reports this week match baseline" },
          weather: { condition: "clear", score: 0, description: "Clear — no weather impact" }
        }
      },
    ]
  };
}
