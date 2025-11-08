import { useState } from 'react'
import { Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom'
import RulesManager from '../components/admin/RulesManager'
import QuestionsManager from '../components/admin/QuestionsManager'
import ValidationView from '../components/admin/ValidationView'

function AdminPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const currentPath = location.pathname
  const username = sessionStorage.getItem('adminUsername') || 'admin'

  const handleLogout = () => {
    sessionStorage.removeItem('adminAuth')
    sessionStorage.removeItem('adminUsername')
    navigate('/login')
  }

  return (
    <div>
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-2xl font-bold text-navy-900">
              管理画面
            </h1>
            <p className="text-gray-600 mt-2">
              ルールと質問の管理、整合性チェックを行います
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600 mb-2">
              ログイン中: <span className="font-medium">{username}</span>
            </p>
            <button
              onClick={handleLogout}
              className="text-sm text-red-600 hover:text-red-700 font-medium"
            >
              ログアウト
            </button>
          </div>
        </div>

        {/* Navigation tabs */}
        <nav className="border-b border-gray-200">
          <div className="flex gap-4">
            <Link
              to="/admin/rules"
              className={`pb-3 px-2 border-b-2 font-medium text-sm transition-colors ${
                currentPath.includes('/rules')
                  ? 'border-navy-600 text-navy-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              ルール管理
            </Link>
            <Link
              to="/admin/questions"
              className={`pb-3 px-2 border-b-2 font-medium text-sm transition-colors ${
                currentPath.includes('/questions')
                  ? 'border-navy-600 text-navy-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              質問管理
            </Link>
            <Link
              to="/admin/validation"
              className={`pb-3 px-2 border-b-2 font-medium text-sm transition-colors ${
                currentPath.includes('/validation')
                  ? 'border-navy-600 text-navy-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              整合性チェック
            </Link>
          </div>
        </nav>
      </div>

      {/* Content area */}
      <div>
        <Routes>
          <Route index element={<RulesManager />} />
          <Route path="rules" element={<RulesManager />} />
          <Route path="questions" element={<QuestionsManager />} />
          <Route path="validation" element={<ValidationView />} />
        </Routes>
      </div>
    </div>
  )
}

export default AdminPage
