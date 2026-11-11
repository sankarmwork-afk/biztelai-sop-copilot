function ChatInput({ question, onQuestionChange, onSend }) {
  function handleSubmit(event) {
    event.preventDefault()
    const trimmedQuestion = question.trim()

    if (!trimmedQuestion) return

    onSend(trimmedQuestion)
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mx-auto flex w-full max-w-3xl gap-3 px-6 py-4"
    >
      <input
        type="text"
        value={question}
        onChange={(event) => onQuestionChange(event.target.value)}
        placeholder="Ask a question about your manufacturing SOPs..."
        aria-label="Your SOP question"
        className="min-w-0 flex-1 rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500 focus:border-blue-500"
      />

      <button
        type="submit"
        disabled={!question.trim()}
        className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
      >
        Send
      </button>
    </form>
  )
}

export default ChatInput
