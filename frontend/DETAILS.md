# Фронтенд: полный обзор и исходный код

## Технологии и языки
- **React 18 + TypeScript (Vite)** — логика формы регистрации и работа с API (`src/App.tsx`, `src/main.tsx`).
- **CSS (Vanilla)** — стилизация формы и страницы (`src/styles.css`).
- **Axios** — HTTP-клиент для отправки POST-запроса `/api/register`.

## Структура форм и компонентов
- **`App` (главный компонент)** — отображает форму регистрации (`login`, `password`), отправляет данные в API, выводит сообщения об успехе или ошибке, показывает требования к паролю.
- **`main.tsx`** — точка входа, монтирует `App` в DOM через `ReactDOM.createRoot`.

## Полный код файлов

### `src/App.tsx`
```tsx
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
```

### `src/main.tsx`
```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### `src/styles.css`
```css
:root {
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color: #0f172a;
  background-color: #f8fafc;
}

body {
  margin: 0;
  background: #f1f5f9;
}

main.container {
  max-width: 480px;
  margin: 48px auto;
  padding: 16px;
}

h1 {
  text-align: center;
}

.card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

label {
  display: flex;
  flex-direction: column;
  font-weight: 600;
  color: #0f172a;
  gap: 6px;
}

input {
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 1rem;
}

button {
  padding: 12px;
  background: linear-gradient(120deg, #2563eb, #4f46e5);
  color: #fff;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
  transition: transform 0.1s ease;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

button:not(:disabled):active {
  transform: translateY(1px);
}

.success {
  color: #15803d;
  margin: 0;
}

.error {
  color: #dc2626;
  margin: 0;
}

.info {
  margin-top: 16px;
  background: #e0f2fe;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid #bae6fd;
}
```

## Как работает форма
1. Пользователь вводит `login` и `password` (все ограничения по длине и обязательность заданы в `<input>`).
2. Отправка формы вызывает `handleSubmit`, который делает `POST /api/register` с телом `{ login, password }`.
3. Успех → сообщение из API выводится в блоке `.success`, поля очищаются.
4. Ошибка → текст из `error.response.data.detail` (или дефолтный) отображается в `.error`.
```
