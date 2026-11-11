function MessageList({ messages }) {
  if (!messages.length) return null

  return (
    <section
      className="mx-auto flex w-full max-w-3xl flex-col gap-5 px-6 py-8"
      aria-live="polite"
      aria-label="Chat messages"
    >
      {messages.map((message) => (
        <article
          key={message.id}
          className={
            message.role === 'user'
              ? 'ml-auto max-w-xl rounded-2xl bg-blue-600 px-4 py-3 text-sm leading-6 text-white'
              : 'mr-auto w-full max-w-2xl rounded-2xl border border-slate-700 bg-slate-800 px-5 py-4 text-sm leading-6 text-slate-200'
          }
        >
          {message.role === 'assistant' && (
            <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-emerald-400">
              SOP Copilot
            </p>
          )}

          <p className="whitespace-pre-wrap">{message.content}</p>

          {message.sources?.length > 0 && (
            <div className="mt-4 border-t border-slate-700 pt-3">
              <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
                Sources
              </h3>
              <ul className="space-y-2">
                {message.sources.map((source, index) => (
                  <li
                    key={`${source.document}-${source.page}-${index}`}
                    className="rounded-lg bg-slate-900 px-3 py-2 text-xs text-slate-300"
                  >
                    <p className="break-words font-medium text-slate-200">
                      {source.document}
                    </p>
                    <p className="mt-1 text-slate-400">
                      Revision {source.revision} · Page {source.page}
                    </p>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </article>
      ))}
    </section>
  )
}

export default MessageList
