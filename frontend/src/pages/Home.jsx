import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch } from '../api/client.js'

export default function Home({ currentUser }) {
  const [news, setNews] = useState([])
  const [error, setError] = useState('')
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')

  useEffect(() => {
    apiFetch('/news/')
      .then(setNews)
      .catch((err) => setError(err.message))
  }, [])

  const canCreate = currentUser?.is_admin || currentUser?.is_verified_author

  const createNews = async (event) => {
    event.preventDefault()
    try {
      const data = await apiFetch('/news/', {
        method: 'POST',
        body: JSON.stringify({ title, content: { text: content } }),
      })
      setNews((prev) => [data, ...prev])
      setTitle('')
      setContent('')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <section>
      <h1>Новости</h1>
      {error && <p className="error">{error}</p>}
      {canCreate && (
        <form onSubmit={createNews} className="form">
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Заголовок" />
          <textarea value={content} onChange={(e) => setContent(e.target.value)} placeholder="Контент" />
          <button type="submit">Создать новость</button>
        </form>
      )}
      <ul className="list">
        {news.map((item) => (
          <li key={item.id}>
            <Link to={`/news/${item.id}`}>{item.title}</Link>
            <span className="meta">{new Date(item.published_at).toLocaleString()}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}
