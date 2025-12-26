import { useState } from 'react'
import { apiFetch } from '../api/client.js'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')

  const onSubmit = async (event) => {
    event.preventDefault()
    try {
      const data = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      localStorage.setItem('access_token', data.access_token)
      setMessage('Успешно')
    } catch (err) {
      setMessage(err.message)
    }
  }

  return (
    <section>
      <h1>Авторизация</h1>
      <form onSubmit={onSubmit} className="form">
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Пароль"
        />
        <button type="submit">Войти</button>
      </form>
      {message && <p className="meta">{message}</p>}
    </section>
  )
}
