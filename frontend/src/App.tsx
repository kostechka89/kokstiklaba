import { useState } from 'react'
import axios from 'axios'

type FormState = {
  login: string
  password: string
}

type ApiState = {
  message: string
  error: string
}

const initialForm: FormState = { login: '', password: '' }
const initialApi: ApiState = { message: '', error: '' }

function App() {
  const [form, setForm] = useState<FormState>(initialForm)
  const [apiState, setApiState] = useState<ApiState>(initialApi)
  const [loading, setLoading] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setApiState(initialApi)

    try {
      const response = await axios.post('/api/register', form)
      setApiState({ message: response.data.message, error: '' })
      setForm(initialForm)
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Registration failed'
      setApiState({ message: '', error: message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="container">
      <h1>Register</h1>
      <form className="card" onSubmit={handleSubmit}>
        <label>
          Login
          <input
            name="login"
            type="text"
            value={form.login}
            onChange={handleChange}
            minLength={3}
            maxLength={32}
            required
          />
        </label>
        <label>
          Password
          <input
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            required
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? 'Submitting...' : 'Register'}
        </button>
        {apiState.message && <p className="success">{apiState.message}</p>}
        {apiState.error && <p className="error">{apiState.error}</p>}
      </form>
      <section className="info">
        <h2>Password requirements</h2>
        <ul>
          <li>At least 8 characters</li>
          <li>One uppercase, one lowercase, one number, one special character</li>
        </ul>
      </section>
    </main>
  )
}

export default App
