import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { apiFetch } from '../api/client.js'

export default function NewsDetail({ currentUser }) {
  const { id } = useParams()
  const navigate = useNavigate()
  const [news, setNews] = useState(null)
  const [comments, setComments] = useState([])
  const [text, setText] = useState('')
  const [error, setError] = useState('')
  const [editTitle, setEditTitle] = useState('')
  const [editContent, setEditContent] = useState('')

  useEffect(() => {
    apiFetch(`/news/${id}`)
      .then((data) => {
        setNews(data)
        setEditTitle(data.title)
        setEditContent(data.content?.text || '')
      })
      .catch((err) => setError(err.message))
    apiFetch(`/comments/?news_id=${id}`)
      .then(setComments)
      .catch(() => {})
  }, [id])

  const submitComment = async (event) => {
    event.preventDefault()
    try {
      const comment = await apiFetch('/comments/', {
        method: 'POST',
        body: JSON.stringify({ text, news_id: Number(id) }),
      })
      setComments((prev) => [...prev, comment])
      setText('')
    } catch (err) {
      setError(err.message)
    }
  }

  const canEditNews = currentUser && (currentUser.is_admin || currentUser.id === news?.author_id)
  const canComment = Boolean(currentUser)

  const updateNews = async (event) => {
    event.preventDefault()
    try {
      const updated = await apiFetch(`/news/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ title: editTitle, content: { text: editContent } }),
      })
      setNews(updated)
    } catch (err) {
      setError(err.message)
    }
  }

  const deleteNews = async () => {
    try {
      await apiFetch(`/news/${id}`, { method: 'DELETE' })
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
  }

  const deleteComment = async (commentId) => {
    try {
      await apiFetch(`/comments/${commentId}`, { method: 'DELETE' })
      setComments((prev) => prev.filter((item) => item.id !== commentId))
    } catch (err) {
      setError(err.message)
    }
  }

  if (!news) {
    return <p>Загрузка...</p>
  }

  return (
    <section>
      <h1>{news.title}</h1>
      <p className="meta">{new Date(news.published_at).toLocaleString()}</p>
      <pre className="content">{JSON.stringify(news.content, null, 2)}</pre>
      {canEditNews && (
        <form onSubmit={updateNews} className="form">
          <input value={editTitle} onChange={(e) => setEditTitle(e.target.value)} />
          <textarea value={editContent} onChange={(e) => setEditContent(e.target.value)} />
          <button type="submit">Сохранить</button>
          <button type="button" onClick={deleteNews}>Удалить</button>
        </form>
      )}
      <h2>Комментарии</h2>
      <ul className="list">
        {comments.map((comment) => (
          <li key={comment.id}>
            {comment.text}
            {currentUser && (currentUser.is_admin || currentUser.id === comment.author_id) && (
              <button type="button" onClick={() => deleteComment(comment.id)}>Удалить</button>
            )}
          </li>
        ))}
      </ul>
      {canComment && (
        <form onSubmit={submitComment} className="form">
          <textarea value={text} onChange={(e) => setText(e.target.value)} />
          <button type="submit">Отправить</button>
        </form>
      )}
      {error && <p className="error">{error}</p>}
    </section>
  )
}
