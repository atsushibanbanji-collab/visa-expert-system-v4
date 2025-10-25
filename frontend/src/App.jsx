import { Routes, Route, Link, useLocation } from 'react-router-dom'
import ConsultationPage from './pages/ConsultationPage'
import AdminPage from './pages/AdminPage'

function App() {
  const location = useLocation()
  const isAdminPage = location.pathname.startsWith('/admin')

  return (
    <div className="min-h-screen bg-gradient-to-br from-navy-50 via-gray-50 to-navy-100">
      {/* Header */}
      <header className="bg-navy-900 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold">ビザ選定エキスパートシステム</h1>
              <p className="text-navy-200 mt-2">
                オブジェクト指向設計による推論エンジン v4.0
              </p>
            </div>
            <nav className="flex gap-4">
              <Link
                to="/"
                className={`px-4 py-2 rounded-lg transition-colors ${
                  !isAdminPage
                    ? 'bg-white text-navy-900'
                    : 'bg-navy-800 text-white hover:bg-navy-700'
                }`}
              >
                診断
              </Link>
              <Link
                to="/admin"
                className={`px-4 py-2 rounded-lg transition-colors ${
                  isAdminPage
                    ? 'bg-white text-navy-900'
                    : 'bg-navy-800 text-white hover:bg-navy-700'
                }`}
              >
                管理画面
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<ConsultationPage />} />
          <Route path="/admin/*" element={<AdminPage />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="bg-navy-900 text-white mt-8">
        <div className="max-w-7xl mx-auto px-4 py-4 text-center text-sm text-navy-200">
          2025 Visa Expert System v4 - Built with React & FastAPI
        </div>
      </footer>
    </div>
  )
}

export default App
