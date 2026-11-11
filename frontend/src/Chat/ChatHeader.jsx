function ChatHeader() {
  return (
    <header className="flex items-center justify-between border-b border-slate-800 px-8 py-5">
      <div>
        <h1 className="text-xl font-semibold text-white">
          Manufacturing SOP AI Copilot
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Your intelligent manufacturing knowledge assistant
        </p>
      </div>

      <div className="flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-2">
        <span className="h-2 w-2 rounded-full bg-emerald-400" />
        <span className="text-sm text-emerald-400">AI Online</span>
      </div>
    </header>
  )
}

export default ChatHeader