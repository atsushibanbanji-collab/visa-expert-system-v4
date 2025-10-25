const DiagnosisPanel = ({
  currentQuestion,
  onAnswer,
  onBack,
  onRestart,
  conclusions,
  isFinished,
  questionHistory
}) => {
  const handleAnswer = (answer) => {
    if (currentQuestion) {
      onAnswer(currentQuestion, answer);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-8 h-full max-h-[calc(100vh-250px)] flex flex-col overflow-hidden">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-navy-900 mb-2">
          ビザ選定診断
        </h1>
        <p className="text-gray-600">
          以下の質問に答えて、適切なビザを診断します
        </p>
      </div>

      {/* Progress indicator */}
      {questionHistory.length > 0 && (
        <div className="mb-6">
          <p className="text-sm text-gray-500 mb-2">
            質問 {questionHistory.length}
          </p>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-navy-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${Math.min((questionHistory.length / 10) * 100, 100)}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Question area */}
      <div className="flex-1 mb-6 overflow-y-auto">
        {!isFinished && currentQuestion && (
          <div className="bg-navy-50 rounded-lg p-6 border-l-4 border-navy-600">
            <p className="text-lg font-medium text-navy-900 mb-4">
              {currentQuestion}
            </p>
            <div className="flex gap-4">
              <button
                onClick={() => handleAnswer(true)}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
              >
                はい
              </button>
              <button
                onClick={() => handleAnswer(false)}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
              >
                いいえ
              </button>
            </div>
          </div>
        )}

        {isFinished && (
          <div className="bg-green-50 rounded-lg p-6 border-l-4 border-green-600">
            <h2 className="text-2xl font-bold text-green-900 mb-4">
              診断結果
            </h2>
            {conclusions.length > 0 ? (
              <div>
                <p className="text-gray-700 mb-4">
                  以下のビザで申請が可能です:
                </p>
                <ul className="space-y-2">
                  {conclusions.map((conclusion, index) => (
                    <li
                      key={index}
                      className="bg-white rounded-lg p-4 shadow border-l-4 border-green-500"
                    >
                      <span className="text-lg font-semibold text-navy-900">
                        {conclusion}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <p className="text-gray-700">
                現在の条件では、申請可能なビザが見つかりませんでした。
              </p>
            )}
          </div>
        )}
      </div>

      {/* Navigation buttons */}
      <div className="flex gap-4">
        <button
          onClick={onBack}
          disabled={questionHistory.length <= 1}
          className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-6 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          前の質問に戻る
        </button>
        <button
          onClick={onRestart}
          className="flex-1 bg-navy-600 hover:bg-navy-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
        >
          最初から
        </button>
      </div>
    </div>
  );
};

export default DiagnosisPanel;
