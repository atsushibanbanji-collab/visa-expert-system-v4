import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const RulesManager = () => {
  const navigate = useNavigate()
  const [rules, setRules] = useState([])
  const [selectedRule, setSelectedRule] = useState(null)
  const [isEditing, setIsEditing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [visaTypeFilter, setVisaTypeFilter] = useState('all')

  const [formData, setFormData] = useState({
    rule_id: '',
    visa_type: 'E',
    conclusion: '',
    conclusion_value: true,
    operator: 'AND',
    priority: 0,
    conditions: []
  })

  // セッションストレージから認証情報を取得
  const getAuth = () => {
    const auth = sessionStorage.getItem('adminAuth')
    if (!auth) {
      navigate('/login')
      return null
    }
    return auth
  }

  useEffect(() => {
    fetchRules()
  }, [visaTypeFilter])

  const fetchRules = async () => {
    const auth = getAuth()
    if (!auth) return

    setLoading(true)
    setError(null)
    try {
      const url = visaTypeFilter === 'all'
        ? `${API_BASE_URL}/admin/rules`
        : `${API_BASE_URL}/admin/rules?visa_type=${visaTypeFilter}`

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

      // データが配列であることを確認
      if (Array.isArray(data)) {
        setRules(data)
      } else {
        console.error('Expected array but got:', data)
        setError('データ形式が正しくありません')
        setRules([])
      }
    } catch (err) {
      console.error('Fetch rules error:', err)
      setError('ルールの取得に失敗しました: ' + err.message)
      setRules([])
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setSelectedRule(null)
    setIsEditing(true)
    setFormData({
      rule_id: '',
      visa_type: 'E',
      conclusion: '',
      conclusion_value: true,
      operator: 'AND',
      priority: 0,
      conditions: []
    })
  }

  const handleEdit = (rule) => {
    setSelectedRule(rule)
    setIsEditing(true)
    setFormData({
      rule_id: rule.rule_id,
      visa_type: rule.visa_type || 'E',
      conclusion: rule.conclusion,
      conclusion_value: rule.conclusion_value,
      operator: rule.operator,
      priority: rule.priority,
      conditions: rule.conditions || []
    })
  }

  const handleSave = async () => {
    const auth = getAuth()
    if (!auth) return

    setLoading(true)
    setError(null)
    try {
      const method = selectedRule ? 'PUT' : 'POST'
      const url = selectedRule
        ? `${API_BASE_URL}/admin/rules/${selectedRule.id}`
        : `${API_BASE_URL}/admin/rules`

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Basic ${auth}`
        },
        body: JSON.stringify(formData)
      })

      if (response.status === 401) {
        sessionStorage.removeItem('adminAuth')
        sessionStorage.removeItem('adminUsername')
        navigate('/login')
        return
      }

      if (response.ok) {
        setIsEditing(false)
        fetchRules()
      } else {
        const errorData = await response.json().catch(() => ({}))
        setError(`保存に失敗しました: ${errorData.detail || response.statusText}`)
      }
    } catch (err) {
      console.error('Save error:', err)
      setError('保存に失敗しました: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (ruleId) => {
    if (!confirm('このルールを削除しますか？')) return

    const auth = getAuth()
    if (!auth) return

    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/admin/rules/${ruleId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Basic ${auth}` }
      })

      if (response.status === 401) {
        sessionStorage.removeItem('adminAuth')
        sessionStorage.removeItem('adminUsername')
        navigate('/login')
        return
      }

      if (response.ok) {
        fetchRules()
      } else {
        const errorData = await response.json().catch(() => ({}))
        setError(`削除に失敗しました: ${errorData.detail || response.statusText}`)
      }
    } catch (err) {
      console.error('Delete error:', err)
      setError('削除に失敗しました: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const addCondition = () => {
    setFormData({
      ...formData,
      conditions: [...formData.conditions, { fact_name: '', expected_value: true }]
    })
  }

  const removeCondition = (index) => {
    const newConditions = formData.conditions.filter((_, i) => i !== index)
    setFormData({ ...formData, conditions: newConditions })
  }

  const updateCondition = (index, field, value) => {
    const newConditions = [...formData.conditions]
    newConditions[index][field] = value
    setFormData({ ...formData, conditions: newConditions })
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
            <h2 className="text-xl font-bold text-navy-900">ルール一覧</h2>
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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ビザ</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">結論</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">条件数</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">優先度</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {rules.map((rule) => (
                  <tr key={rule.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {rule.rule_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {rule.visa_type || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 max-w-md truncate">
                      {rule.conclusion}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {rule.conditions?.length || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {rule.priority}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleEdit(rule)}
                        className="text-navy-600 hover:text-navy-900 mr-4"
                      >
                        編集
                      </button>
                      <button
                        onClick={() => handleDelete(rule.id)}
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
            {selectedRule ? 'ルール編集' : 'ルール作成'}
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">ルールID</label>
              <input
                type="text"
                value={formData.rule_id}
                onChange={(e) => setFormData({ ...formData, rule_id: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                placeholder="rule_1"
              />
            </div>

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
              <label className="block text-sm font-medium text-gray-700 mb-2">結論</label>
              <input
                type="text"
                value={formData.conclusion}
                onChange={(e) => setFormData({ ...formData, conclusion: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                placeholder="Eビザでの申請ができます"
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">演算子</label>
                <select
                  value={formData.operator}
                  onChange={(e) => setFormData({ ...formData, operator: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2"
                >
                  <option value="AND">AND</option>
                  <option value="OR">OR</option>
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

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">結論値</label>
                <select
                  value={formData.conclusion_value}
                  onChange={(e) => setFormData({ ...formData, conclusion_value: e.target.value === 'true' })}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2"
                >
                  <option value="true">True</option>
                  <option value="false">False</option>
                </select>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium text-gray-700">条件</label>
                <button
                  onClick={addCondition}
                  className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm"
                >
                  条件を追加
                </button>
              </div>

              <div className="space-y-2">
                {formData.conditions.map((condition, index) => (
                  <div key={index} className="flex gap-2 items-center">
                    <input
                      type="text"
                      value={condition.fact_name}
                      onChange={(e) => updateCondition(index, 'fact_name', e.target.value)}
                      className="flex-1 border border-gray-300 rounded-lg px-4 py-2"
                      placeholder="事実名"
                    />
                    <select
                      value={condition.expected_value}
                      onChange={(e) => updateCondition(index, 'expected_value', e.target.value === 'true')}
                      className="border border-gray-300 rounded-lg px-4 py-2"
                    >
                      <option value="true">True</option>
                      <option value="false">False</option>
                    </select>
                    <button
                      onClick={() => removeCondition(index)}
                      className="bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded"
                    >
                      削除
                    </button>
                  </div>
                ))}
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

export default RulesManager
