import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const QuestionsManager = () => {
  const navigate = useNavigate()
  const [questions, setQuestions] = useState([])
  const [selectedQuestion, setSelectedQuestion] = useState(null)
  const [isEditing, setIsEditing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [visaTypeFilter, setVisaTypeFilter] = useState('all')

  const [formData, setFormData] = useState({
    fact_name: '',
    question_text: '',
    visa_type: 'E',
    priority: 0
  })

  const getAuth = () => {
    const auth = sessionStorage.getItem('adminAuth')
    if (!auth) {
      navigate('/login')
      return null
    }
    return auth
  }

  useEffect(() => {
    fetchQuestions()
  }, [visaTypeFilter])

  const fetchQuestions = async () => {
    const auth = getAuth()
    if (!auth) return

    setLoading(true)
    setError(null)
    try {
      const url = visaTypeFilter === 'all'
        ? `${API_BASE_URL}/admin/questions`
        : `${API_BASE_URL}/admin/questions?visa_type=${visaTypeFilter}`

      const response = await fetch(url, {
        headers: { 'Authorization': `Basic ${auth}` }
      })

      if (response.status === 401) {
        sessionStorage.removeItem('adminAuth')
        sessionStorage.removeItem('adminUsername')
        navigate('/login')
        return
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      if (Array.isArray(data)) {
        setQuestions(data)
      } else {
        setError('データ形式が正しくありません')
        setQuestions([])
      }
    } catch (err) {
      console.error('Fetch questions error:', err)
      setError('質問の取得に失敗しました: ' + err.message)
      setQuestions([])
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setSelectedQuestion(null)
    setIsEditing(true)
    setFormData({
      fact_name: '',
      question_text: '',
      visa_type: 'E',
      priority: 0
    })
  }

  const handleEdit = (question) => {
    setSelectedQuestion(question)
    setIsEditing(true)
    setFormData({
      fact_name: question.fact_name,
      question_text: question.question_text,
      visa_type: question.visa_type || 'E',
      priority: question.priority
    })
  }

  const handleSave = async () => {
    setLoading(true)
    try {
      const method = selectedQuestion ? 'PUT' : 'POST'
      const url = selectedQuestion
        ? `${API_BASE_URL}/admin/questions/${selectedQuestion.id}`
        : `${API_BASE_URL}/admin/questions`

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Basic ${auth}`
        },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        setIsEditing(false)
        fetchQuestions()
      } else {
        setError('保存に失敗しました')
      }
    } catch (err) {
      setError('保存に失敗しました: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (questionId) => {
    if (!confirm('この質問を削除しますか？')) return

    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/admin/questions/${questionId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Basic ${auth}` }
      })

      if (response.ok) {
        fetchQuestions()
      } else {
        setError('削除に失敗しました')
      }
    } catch (err) {
      setError('削除に失敗しました')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {error && (
        <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {!isEditing ? (
        <div>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-navy-900">質問一覧</h2>
            <div className="flex gap-4">
              <select
                value={visaTypeFilter}
                onChange={(e) => setVisaTypeFilter(e.target.value)}
                className="border border-gray-300 rounded-lg px-4 py-2"
              >
                <option value="all">すべてのビザタイプ</option>
                <option value="E">Eビザ</option>
                <option value="L">Lビザ</option>
                <option value="B">Bビザ</option>
                <option value="H-1B">H-1Bビザ</option>
                <option value="J-1">J-1ビザ</option>
              </select>
              <button
                onClick={handleCreate}
                className="bg-navy-600 hover:bg-navy-700 text-white px-4 py-2 rounded-lg"
              >
                新規作成
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">事実名</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ビザ</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">質問文</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">優先度</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {questions.map((question) => (
                  <tr key={question.id}>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900 max-w-xs truncate">
                      {question.fact_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {question.visa_type || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 max-w-md truncate">
                      {question.question_text}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {question.priority}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleEdit(question)}
                        className="text-navy-600 hover:text-navy-900 mr-4"
                      >
                        編集
                      </button>
                      <button
                        onClick={() => handleDelete(question.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        削除
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div>
          <h2 className="text-xl font-bold text-navy-900 mb-6">
            {selectedQuestion ? '質問編集' : '質問作成'}
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">事実名（Fact Name）</label>
              <input
                type="text"
                value={formData.fact_name}
                onChange={(e) => setFormData({ ...formData, fact_name: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                placeholder="申請者と会社の国籍が同じです"
                disabled={selectedQuestion !== null}
              />
              {selectedQuestion && (
                <p className="text-sm text-gray-500 mt-1">事実名は編集できません</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">質問文</label>
              <textarea
                value={formData.question_text}
                onChange={(e) => setFormData({ ...formData, question_text: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                rows="3"
                placeholder="申請者と会社の国籍が同じです"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">ビザタイプ</label>
                <select
                  value={formData.visa_type}
                  onChange={(e) => setFormData({ ...formData, visa_type: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2"
                >
                  <option value="E">Eビザ</option>
                  <option value="L">Lビザ</option>
                  <option value="B">Bビザ</option>
                  <option value="H-1B">H-1Bビザ</option>
                  <option value="J-1">J-1ビザ</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">優先度</label>
                <input
                  type="number"
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2"
                />
              </div>
            </div>

            <div className="flex gap-4 pt-4">
              <button
                onClick={handleSave}
                disabled={loading}
                className="bg-navy-600 hover:bg-navy-700 text-white px-6 py-2 rounded-lg disabled:opacity-50"
              >
                保存
              </button>
              <button
                onClick={() => setIsEditing(false)}
                className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-2 rounded-lg"
              >
                キャンセル
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default QuestionsManager
