import { useState } from 'react'
import VisaTypeSelection from '../components/consultation/VisaTypeSelection'
import DiagnosisPanel from '../components/consultation/DiagnosisPanel'
import VisualizationPanel from '../components/consultation/VisualizationPanel'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

function ConsultationPage() {
  const [selectedVisaType, setSelectedVisaType] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [isDerivable, setIsDerivable] = useState(true)
  const [conclusions, setConclusions] = useState([])
  const [unknownFacts, setUnknownFacts] = useState([])
  const [isFinished, setIsFinished] = useState(false)
  const [insufficientInfo, setInsufficientInfo] = useState(false)
  const [missingCriticalInfo, setMissingCriticalInfo] = useState([])
  const [uncertainFactsLogic, setUncertainFactsLogic] = useState({})
  const [visualizationData, setVisualizationData] = useState(null)
  const [questionHistory, setQuestionHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [currentVisaType, setCurrentVisaType] = useState(null)
  const [allVisaMode, setAllVisaMode] = useState(false)
  const [allConclusions, setAllConclusions] = useState({})

  const startConsultation = async (visaType) => {
    setLoading(true)
    setError(null)
    setSelectedVisaType(visaType)
    try {
      const response = await fetch(`${API_BASE_URL}/consultation/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ visa_type: visaType }),
      })
      const data = await response.json()
      setCurrentQuestion(data.next_question)
      setIsDerivable(data.is_derivable !== undefined ? data.is_derivable : true)
      setQuestionHistory(data.next_question ? [data.next_question] : [])
      setConclusions([])
      setUnknownFacts(data.unknown_facts || [])
      setMissingCriticalInfo(data.missing_critical_info || [])
      setIsFinished(false)
      setCurrentVisaType(data.current_visa_type || null)
      setAllVisaMode(data.all_visa_mode || false)
      setAllConclusions(data.all_conclusions || {})
      await fetchVisualization()
    } catch (err) {
      setError('診断の開始に失敗しました: ' + err.message)
      console.error('Error starting consultation:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchVisualization = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/consultation/visualization`)
      const data = await response.json()
      setVisualizationData(data)
    } catch (err) {
      console.error('Error fetching visualization:', err)
    }
  }

  const handleAnswer = async (question, answer) => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/consultation/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, answer }),
      })
      const data = await response.json()

      setCurrentQuestion(data.next_question)
      setIsDerivable(data.is_derivable !== undefined ? data.is_derivable : true)
      setConclusions(data.conclusions)
      setUnknownFacts(data.unknown_facts || [])
      setMissingCriticalInfo(data.missing_critical_info || [])
      setUncertainFactsLogic(data.uncertain_facts_logic || {})
      setIsFinished(data.is_finished)
      setInsufficientInfo(data.insufficient_info || false)
      setCurrentVisaType(data.current_visa_type || null)
      setAllVisaMode(data.all_visa_mode || false)
      setAllConclusions(data.all_conclusions || {})

      if (data.next_question && !questionHistory.includes(data.next_question)) {
        setQuestionHistory([...questionHistory, data.next_question])
      }

      await fetchVisualization()
    } catch (err) {
      setError('回答の送信に失敗しました: ' + err.message)
      console.error('Error answering question:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleBack = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/consultation/back`, {
        method: 'POST',
      })
      const data = await response.json()

      if (data.current_question) {
        setCurrentQuestion(data.current_question)
        // Only remove from history if there are more than 1 questions
        if (questionHistory.length > 1) {
          setQuestionHistory(questionHistory.slice(0, -1))
        }
        setIsFinished(false)
        setInsufficientInfo(false)
        setConclusions([])
        setUnknownFacts([])
        setMissingCriticalInfo([])
        setUncertainFactsLogic({})
      }

      await fetchVisualization()
    } catch (err) {
      setError('前の質問に戻れませんでした: ' + err.message)
      console.error('Error going back:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleRestart = () => {
    setSelectedVisaType(null)
    setCurrentQuestion(null)
    setQuestionHistory([])
    setConclusions([])
    setUnknownFacts([])
    setMissingCriticalInfo([])
    setUncertainFactsLogic({})
    setIsFinished(false)
    setInsufficientInfo(false)
    setVisualizationData(null)
    setError(null)
    setCurrentVisaType(null)
    setAllVisaMode(false)
    setAllConclusions({})
  }

  return (
    <div>
      {error && (
        <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <strong className="font-bold">エラー: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {!selectedVisaType ? (
        <div className="flex items-center justify-center min-h-[calc(100vh-300px)]">
          <VisaTypeSelection onSelectVisaType={startConsultation} />
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-250px)] overflow-hidden">
          <div className="h-full overflow-hidden">
            {loading && questionHistory.length === 0 ? (
              <div className="bg-white rounded-lg shadow-lg p-8 h-full flex items-center justify-center">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-navy-900 mx-auto mb-4"></div>
                  <p className="text-gray-600">読み込み中...</p>
                </div>
              </div>
            ) : (
              <DiagnosisPanel
                currentQuestion={currentQuestion}
                isDerivable={isDerivable}
                onAnswer={handleAnswer}
                onBack={handleBack}
                onRestart={handleRestart}
                conclusions={conclusions}
                unknownFacts={unknownFacts}
                isFinished={isFinished}
                insufficientInfo={insufficientInfo}
                missingCriticalInfo={missingCriticalInfo}
                uncertainFactsLogic={uncertainFactsLogic}
                questionHistory={questionHistory}
                loading={loading}
                currentVisaType={currentVisaType}
                allVisaMode={allVisaMode}
                allConclusions={allConclusions}
              />
            )}
          </div>

          <div className="h-full overflow-hidden">
            <VisualizationPanel
              visualizationData={visualizationData}
              currentQuestion={currentQuestion}
            />
          </div>
        </div>
      )}
    </div>
  )
}

export default ConsultationPage
