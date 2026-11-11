const questions = [
  "What is the recommended coolant concentration for TX-200?",
  "What does alarm AL-104 mean?",
  "Who can remove a lockout lock?",
  "What is the BH-220 OD tolerance?",
]

function SuggestedQuestions({ onQuestionSelect }) {
  return (
    <section className="mx-auto mt-10 max-w-3xl px-6">
      <h3 className="mb-4 text-sm font-semibold text-slate-400">
        SUGGESTED QUESTIONS
      </h3>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {questions.map((question, index) => (
          <button
            key={index}
            onClick={() => onQuestionSelect(question)}
            className="rounded-xl border border-slate-700 bg-slate-800 p-4 text-left text-sm text-slate-200 transition hover:border-blue-500 hover:bg-slate-700"
          >
            {question}
          </button>
        ))}
      </div>
    </section>
  )
}

export default SuggestedQuestions