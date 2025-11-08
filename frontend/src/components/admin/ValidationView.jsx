import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const ValidationView = () => {
  const navigate = useNavigate()
  const [visaType, setVisaType] = useState('E')
  const [validationResult, setValidationResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const getAuth = () => {
    const auth = sessionStorage.getItem('adminAuth')
    if (!auth) {
      navigate('/login')
      return null
    }
    return auth
  }

  const runValidation = async () => {
    const auth = getAuth()
    if (!auth) return

    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/admin/validate/${visaType}`, {
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
      setValidationResult(data)
    } catch (err) {
      console.error('Validation error:', err)
      setError('検証に失敗しました: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'error':
        return 'bg-red-50 border-red-500 text-red-900'
      case 'warning':
        return 'bg-yellow-50 border-yellow-500 text-yellow-900'
      default:
        return 'bg-gray-50 border-gray-500 text-gray-900'
    }
  }

  const getValidationTypeLabel = (type) => {
    switch (type) {
      case 'contradiction':
        return '矛盾'
      case 'unreachable':
        return '到達不可能'
      case 'circular':
        return '循環参照'
      default:
        return type
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold text-navy-900 mb-6">整合性チェック</h2>

      {error && (
        <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="mb-6">
        <div className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              検証するビザタイプを選択
            </label>
            <select
              value={visaType}
              onChange={(e) => setVisaType(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2"
            >
              <option value="E">Eビザ</option>
              <option value="L">Lビザ</option>
              <option value="B">Bビザ</option>
              <option value="H-1B">H-1Bビザ</option>
              <option value="J-1">J-1ビザ</option>
            </select>
          </div>
          <button
            onClick={runValidation}
            disabled={loading}
            className="bg-navy-600 hover:bg-navy-700 text-white px-6 py-2 rounded-lg disabled:opacity-50"
          >
            {loading ? '検証中...' : '検証を実行'}
          </button>
        </div>
      </div>

      {validationResult && (
        <div>
          <div className="mb-6">
            {validationResult.is_valid ? (
              <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-green-800">
                      検証成功: ルールに問題は見つかりませんでした
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-red-800">
                      検証失敗: {validationResult.issues.length} 件の問題が見つかりました
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {validationResult.issues && validationResult.issues.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">検出された問題</h3>
              <div className="space-y-4">
                {validationResult.issues.map((issue, index) => (
                  <div
                    key={index}
                    className={`border-l-4 p-4 rounded ${getSeverityColor(issue.severity)}`}
                  >
                    <div className="flex items-start">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-800 text-white mr-2">
                            {getValidationTypeLabel(issue.validation_type)}
                          </span>
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-200 text-gray-800">
                            {issue.severity}
                          </span>
                        </div>
                        <p className="text-sm font-medium mb-2">{issue.message}</p>
                        {issue.details && Object.keys(issue.details).length > 0 && (
                          <div className="mt-2 text-xs">
                            <details className="cursor-pointer">
                              <summary className="font-semibold">詳細を表示</summary>
                              <pre className="mt-2 p-2 bg-white bg-opacity-50 rounded overflow-x-auto">
                                {JSON.stringify(issue.details, null, 2)}
                              </pre>
                            </details>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-6 text-sm text-gray-500">
            検証実施日時: {new Date(validationResult.checked_at).toLocaleString('ja-JP')}
          </div>
        </div>
      )}

      {!validationResult && !loading && (
        <div className="text-center py-12 text-gray-500">
          <p>ビザタイプを選択して「検証を実行」ボタンをクリックしてください</p>
        </div>
      )}
    </div>
  )
}

export default ValidationView
