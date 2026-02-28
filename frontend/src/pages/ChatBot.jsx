import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { useAuth } from '../context/AuthContext'

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिंदी' },
  { code: 'mr', label: 'मराठी' },
]

const QUICK_PROMPTS = [
  'मला धक्का दिला platform वर पडलो',
  'Someone stole my phone on the train',
  'मुझे compensation चाहिए, train से गिरा',
  'Ladies compartment mein ek aadmi ghus aaya',
  'ट्रेन रोज़ late आती है, कहाँ complain करूँ?',
]

export default function ChatBot() {
  const { user } = useAuth()
  const [language, setLanguage] = useState(user?.language_pref || 'en')
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => { scrollToBottom() }, [messages])

  const sendMessage = async (text) => {
    if (!text.trim()) return
    const userMsg = { role: 'user', content: text }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch('/api/bot/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, message: text, language }),
      })
      const data = await res.json()

      if (!res.ok) throw new Error(data.detail || 'Bot error')

      const botMsg = {
        role: 'bot',
        content: data.response,
        options: data.options || null,
        complaint_draft: data.complaint_draft,
        authority: data.authority,
        compensation: data.compensation,
        cpgrams_ref: data.cpgrams_ref,
        follow_up_date: data.follow_up_date,
      }
      setMessages(prev => [...prev, botMsg])
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', content: `Error: ${err.message}`, error: true }])
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    sendMessage(input)
  }

  return (
    <div className="flex gap-4 h-[calc(100vh-140px)]">
      {/* Sidebar */}
      <div className="w-72 flex-shrink-0 bg-white rounded-xl shadow-sm p-4 flex flex-col gap-4 overflow-y-auto">
        {/* User Info */}
        <div className="bg-blue-50 rounded-lg p-3">
          <div className="text-xs font-semibold text-blue-800 mb-2">Your Profile</div>
          <div className="text-xs text-blue-700 space-y-1">
            <div><span className="font-medium">Name:</span> {user?.name}</div>
            {user?.phone && (
              <div><span className="font-medium">Phone:</span> {user.phone}</div>
            )}
          </div>
        </div>

        {/* Language Selector */}
        <div>
          <label className="block text-xs font-semibold text-gray-500 mb-1">Language</label>
          <div className="flex gap-1">
            {LANGUAGES.map(l => (
              <button
                key={l.code}
                onClick={() => setLanguage(l.code)}
                className={`flex-1 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  language === l.code
                    ? 'bg-[#1e3a5f] text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {l.label}
              </button>
            ))}
          </div>
        </div>

        {/* Quick Prompts */}
        <div>
          <label className="block text-xs font-semibold text-gray-500 mb-2">Quick Prompts</label>
          <div className="flex flex-col gap-1.5">
            {QUICK_PROMPTS.map((prompt, i) => (
              <button
                key={i}
                onClick={() => sendMessage(prompt)}
                disabled={loading}
                className="text-left text-xs bg-gray-50 hover:bg-orange-50 hover:text-[#ff6b35] rounded-lg px-3 py-2 transition-colors border border-gray-100 disabled:opacity-50"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col bg-white rounded-xl shadow-sm">
        {/* Chat Header */}
        <div className="px-5 py-3 border-b border-gray-100 flex items-center gap-3">
          <div className="w-8 h-8 bg-[#1e3a5f] rounded-full flex items-center justify-center text-white text-sm">
            JS
          </div>
          <div>
            <div className="font-semibold text-sm">Jan Suraksha Bot</div>
            <div className="text-[10px] text-gray-400">Legal Aid for Railway Passengers | GraphRAG + LangGraph</div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-400 mt-20">
              <div className="text-4xl mb-3">🛡️</div>
              <div className="font-semibold">Jan Suraksha Bot</div>
              <div className="text-xs mt-1">Describe your incident in any language. I'll help with legal rights, complaint filing & compensation.</div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
                msg.role === 'user'
                  ? 'bg-[#1e3a5f] text-white rounded-br-md'
                  : msg.error
                    ? 'bg-red-50 text-red-700 rounded-bl-md border border-red-200'
                    : 'bg-gray-50 text-gray-800 rounded-bl-md border border-gray-100'
              }`}>
                {msg.role === 'bot' ? (
                  <div className="space-y-3">
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>

                    {/* Action option buttons (Turn 1) */}
                    {msg.options && msg.options.length > 0 && (
                      <div className="mt-3 flex flex-col gap-2">
                        {msg.options.map((opt, idx) => (
                          <button
                            key={opt.id}
                            onClick={() => sendMessage(String(idx + 1))}
                            disabled={loading}
                            className="text-left bg-white border-2 border-gray-200 rounded-xl px-4 py-3 hover:border-[#ff6b35] hover:bg-orange-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
                          >
                            <div className="font-semibold text-sm text-[#1e3a5f] group-hover:text-[#ff6b35] transition-colors">
                              {idx + 1}. {opt.label}
                            </div>
                            <div className="text-xs text-gray-500 mt-0.5">{opt.description}</div>
                          </button>
                        ))}
                      </div>
                    )}

                    {/* Metadata pills */}
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {msg.authority && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-blue-100 text-blue-800">
                          Authority: {msg.authority}
                        </span>
                      )}
                      {msg.compensation && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-green-100 text-green-800">
                          {msg.compensation}
                        </span>
                      )}
                      {msg.cpgrams_ref && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-orange-100 text-orange-800">
                          CPGRAMS: {msg.cpgrams_ref}
                        </span>
                      )}
                      {msg.follow_up_date && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-purple-100 text-purple-800">
                          Follow up: {msg.follow_up_date}
                        </span>
                      )}
                    </div>

                    {/* Complaint Draft — Download PDF */}
                    {msg.complaint_draft && (
                      <button
                        onClick={() => {
                          const w = window.open('', '_blank')
                          w.document.write(`<!DOCTYPE html><html><head><title>Complaint - Jan Suraksha</title><style>
                            @media print { body { margin: 0; } @page { margin: 1.5cm; } }
                            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.7; padding: 40px; max-width: 800px; margin: 0 auto; color: #1a1a1a; }
                            h2 { text-align: center; border-bottom: 2px solid #1e3a5f; padding-bottom: 10px; color: #1e3a5f; }
                            .meta { font-size: 12px; color: #666; text-align: right; margin-bottom: 20px; }
                            pre { white-space: pre-wrap; font-family: inherit; font-size: 14px; }
                            .footer { margin-top: 40px; font-size: 11px; color: #999; text-align: center; border-top: 1px solid #ddd; padding-top: 10px; }
                          </style></head><body>
                            <h2>Jan Suraksha — Complaint Document</h2>
                            <div class="meta">Generated: ${new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}${msg.cpgrams_ref ? ` | Ref: ${msg.cpgrams_ref}` : ''}</div>
                            <pre>${msg.complaint_draft.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
                            <div class="footer">Generated by Jan Suraksha Bot — RailFLOW Platform</div>
                          </body></html>`)
                          w.document.close()
                          setTimeout(() => w.print(), 300)
                        }}
                        className="mt-2 w-full flex items-center justify-center gap-2 bg-[#1e3a5f] text-white rounded-lg px-4 py-2.5 text-xs font-medium hover:bg-[#2a4f7f] transition-colors"
                      >
                        <span>📄</span> Download Complaint PDF
                      </button>
                    )}
                  </div>
                ) : (
                  msg.content
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-50 rounded-2xl rounded-bl-md px-4 py-3 border border-gray-100">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                  Analyzing incident & retrieving legal context...
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="p-3 border-t border-gray-100">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Describe your incident (English / Hindi / Marathi)..."
              disabled={loading}
              className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-[#ff6b35] focus:ring-1 focus:ring-[#ff6b35] disabled:bg-gray-50"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-[#ff6b35] text-white px-5 py-2.5 rounded-xl text-sm font-medium hover:bg-[#e55a2b] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
