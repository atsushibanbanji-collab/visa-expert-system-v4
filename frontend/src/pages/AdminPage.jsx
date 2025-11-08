import { useState } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import RulesManager from '../components/admin/RulesManager'
import QuestionsManager from '../components/admin/QuestionsManager'
import ValidationView from '../components/admin/ValidationView'

function AdminPage() {
  const location = useLocation()
  const currentPath = location.pathname

  return (
    <div>
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h1 className="text-2xl font-bold text-navy-900 mb-4">
          管理画面
        </h1>
        <p className="text-gray-600 mb-6">
          ルールと質問の管理、整合性チェックを行います
        </p>

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
