function Sidebar() {
  return (
    <aside className="flex h-screen w-72 flex-col border-r border-slate-800 bg-slate-950 px-6 py-7 text-slate-100">
      <div className="mb-10">
        <h2 className="text-xl font-bold tracking-tight">Manufacturing AI</h2>
        <p className="mt-1 text-xs text-slate-400">SOP KNOWLEDGE ASSISTANT</p>
      </div>

      <section className="mb-10">
        <h3 className="mb-4 text-xs font-semibold uppercase tracking-widest text-slate-400">
          SOP Documents
        </h3>
        <ul className="space-y-3 text-sm text-slate-300">
          <li className="rounded-lg bg-slate-900 px-3 py-2">Preventive Maintenance</li>
          <li className="rounded-lg bg-slate-900 px-3 py-2">Incoming Material Inspection</li>
          <li className="rounded-lg bg-slate-900 px-3 py-2">Lockout Tagout Procedure</li>
        </ul>
      </section>

      <section className="mt-auto rounded-xl border border-slate-800 bg-slate-900 p-4">
        <h3 className="mb-4 text-xs font-semibold uppercase tracking-widest text-slate-400">
          System Status
        </h3>
        <p className="mb-2 flex items-center gap-2 text-sm text-slate-300">
          <span className="h-2 w-2 rounded-full bg-emerald-400" />
          AI Assistant Online
        </p>
        <p className="flex items-center gap-2 text-sm text-slate-300">
          <span className="h-2 w-2 rounded-full bg-emerald-400" />
          Document Database Ready
        </p>
      </section>
    </aside>
  )
}

export default Sidebar