import { useState } from 'react'
import Sidebar from './Sidebar/Sidebar'
import ChatHeader from './Chat/ChatHeader'
import Welcome from './Chat/Welcome'
import SuggestedQuestions from './Chat/SuggestedQuestions'
import ChatInput from './Chat/ChatInput'
import MessageList from './Chat/MessageList'

const API_URL = 'http://192.168.1.5:8000'

function App() {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  function handleQuestionSelect(selected) {
    setQuestion(selected)
  }

  async function handleSend(message) {
    if (isLoading) return

    setMessages((currentMessages) => [
      ...currentMessages,
      { id: `${Date.now()}-user`, role: 'user', content: message },
    ])
    setQuestion('')
    setError('')
    setIsLoading(true)

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: message }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'The server could not answer your question.')
      }

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: `${Date.now()}-assistant`,
          role: 'assistant',
          content: data.answer,
          sources: data.sources || [],
        },
      ])
    } catch (requestError) {
      setError(requestError.message || 'Unable to contact the AI service.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen w-full overflow-x-hidden bg-slate-900">
      <div className="hidden md:block">
        <Sidebar />
      </div>

      <main className="flex min-w-0 w-full flex-1 flex-col">
        <ChatHeader />

        <div className="flex-1">
          {messages.length === 0 && (
            <>
              <Welcome />
              <SuggestedQuestions onQuestionSelect={handleQuestionSelect} />
            </>
          )}

          <MessageList messages={messages} />

          {isLoading && (
            <p className="mx-auto max-w-3xl px-6 py-3 text-sm text-slate-400" role="status">
              Searching SOP documents and preparing an answer...
            </p>
          )}

          {error && (
            <p className="mx-auto max-w-3xl px-6 py-3 text-sm text-red-400" role="alert">
              {error}
            </p>
          )}
        </div>

        <ChatInput
          question={question}
          onQuestionChange={setQuestion}
          onSend={handleSend}
        />
      </main>
    </div>
  )
}

export default App