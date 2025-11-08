import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function LoginPage() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    // 認証情報をBase64エンコード
    const auth = btoa(`${username}:${password}`)

    // 認証テスト用にAPIを呼び出し
    const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

    try {
      const response = await fetch(`${API_BASE_URL}/admin/rules?visa_type=E`, {
        headers: { 'Authorization': `Basic ${auth}` }
      })

      if (response.ok) {
        // 認証成功 - 認証情報を保存
        sessionStorage.setItem('adminAuth', auth)
        sessionStorage.setItem('adminUsername', username)
        navigate('/admin/rules')
      } else if (response.status === 401) {
        setError('ユーザー名またはパスワードが正しくありません')
      } else {
        setError('ログインに失敗しました')
      }
    } catch (err) {
      setError('サーバーに接続できません: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-navy-50 to-navy-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-lg">
        <div>
          <h2 className="text-center text-3xl font-bold text-navy-900">
            管理画面ログイン
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            ビザ選定エキスパートシステム v4
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleLogin}>
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                ユーザー名
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 rounded-lg placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-navy-500 focus:border-navy-500"
                placeholder="admin"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                パスワード
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 rounded-lg placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-navy-500 focus:border-navy-500"
                placeholder="パスワードを入力"
              />
            </div>
          </div>

          <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded">
            <p className="font-medium mb-1">パスワードの確認方法:</p>
            <ol className="list-decimal list-inside space-y-1">
              <li>Renderダッシュボードにログイン</li>
              <li>visa-expert-backend-v4サービスを選択</li>
              <li>Environment タブを開く</li>
              <li>ADMIN_PASSWORD の値を確認</li>
            </ol>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-navy-600 hover:bg-navy-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-navy-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'ログイン中...' : 'ログイン'}
            </button>
          </div>

          <div className="text-center">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="text-sm text-navy-600 hover:text-navy-500"
            >
              ← トップページに戻る
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default LoginPage
