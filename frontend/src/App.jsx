import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { fetchCurrentUser } from './api/client.js'
import Home from './pages/Home.jsx'
import NewsDetail from './pages/NewsDetail.jsx'
import Login from './pages/Login.jsx'
import './styles/app.css'

export default function App() {
  const [user, setUser] = useState(null)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const accessToken = params.get('access_token')
    if (accessToken) {
      localStorage.setItem('access_token', accessToken)
      window.history.replaceState({}, document.title, '/')
    }
    fetchCurrentUser().then(setUser).catch(() => setUser(null))
  }, [])

  const logout = () => {
    localStorage.removeItem('access_token')
    setUser(null)
  }

  return (
    <BrowserRouter>
      <header className="header">
        <Link to="/">Новости</Link>
        {user ? (
          <div className="user">
            <span>{user.name}</span>
            <button type="button" onClick={logout}>Выйти</button>
          </div>
        ) : (
          <Link to="/login">Войти</Link>
        )}
      </header>
      <main className="container">
        <Routes>
          <Route path="/" element={<Home currentUser={user} />} />
          <Route path="/news/:id" element={<NewsDetail currentUser={user} />} />
          <Route path="/login" element={<Login onLogin={setUser} />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}
