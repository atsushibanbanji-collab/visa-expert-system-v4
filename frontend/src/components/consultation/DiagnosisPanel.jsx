const DiagnosisPanel = ({
  currentQuestion,
  onAnswer,
  onBack,
  onRestart,
  conclusions,
  unknownFacts,
  isFinished,
  questionHistory
}) => {
  const handleAnswer = (answer) => {
    if (currentQuestion) {
      onAnswer(currentQuestion, answer);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-4 h-full flex flex-col overflow-hidden">
      <div className="mb-3">
        <h1 className="text-xl font-bold text-navy-900">
          ビザ選定診断
        </h1>
      </div>

      {/* Progress indicator */}
      {questionHistory.length > 0 && (
        <div className="mb-3">
          <p className="text-xs text-gray-500 mb-1">
            質問 {questionHistory.length}
          </p>
          <div className="w-full bg-gray-200 rounded-full h-1.5">
            <div
              className="bg-navy-600 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${Math.min((questionHistory.length / 10) * 100, 100)}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Question area */}
      <div className="flex-1 mb-3 overflow-y-auto">
        {!isFinished && currentQuestion && (
          <div className="bg-navy-50 rounded-lg p-4 border-l-4 border-navy-600">
            <p className="text-base font-medium text-navy-900 mb-3">
              {currentQuestion}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => handleAnswer(true)}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-3 rounded-lg transition-colors duration-200 text-sm"
              >
                はい
              </button>
              <button
                onClick={() => handleAnswer(false)}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-3 rounded-lg transition-colors duration-200 text-sm"
              >
                いいえ
              </button>
              <button
                onClick={() => handleAnswer(null)}
                className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-3 rounded-lg transition-colors duration-200 text-sm"
              >
                分からない
              </button>
            </div>
          </div>
        )}

        {isFinished && (
          <div className="bg-green-50 rounded-lg p-4 border-l-4 border-green-600">
            <h2 className="text-lg font-bold text-green-900 mb-3">
              診断結果
            </h2>
            {conclusions.length > 0 ? (
              <div>
                <p className="text-sm text-gray-700 mb-2">
                  以下のビザで申請が可能です:
                </p>
                <ul className="space-y-2 mb-3">
                  {conclusions.map((conclusion, index) => (
                    <li
                      key={index}
                      className="bg-white rounded-lg p-3 shadow border-l-4 border-green-500"
                    >
                      <span className="text-base font-semibold text-navy-900">
                        {conclusion}
                      </span>
                    </li>
                  ))}
                </ul>
                {unknownFacts && unknownFacts.length > 0 && (
                  <div className="bg-yellow-50 rounded-lg p-3 border-l-4 border-yellow-500">
                    <p className="text-xs font-semibold text-yellow-900 mb-1">
                      ※ 以下の条件については「分からない」と回答されているため、これらが満たされている前提での結果です：
                    </p>
                    <ul className="list-disc list-inside space-y-0.5 text-xs text-yellow-800">
                      {unknownFacts.map((fact, index) => (
                        <li key={index}>{fact}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-gray-700">
                現在の条件では、申請可能なビザが見つかりませんでした。
              </p>
            )}
          </div>
        )}
      </div>

      {/* Navigation buttons */}
      <div className="flex gap-2">
        <button
          onClick={onBack}
          disabled={questionHistory.length <= 1}
          className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-2 px-3 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
        >
          前の質問に戻る
        </button>
        <button
          onClick={onRestart}
          className="flex-1 bg-navy-600 hover:bg-navy-700 text-white font-semibold py-2 px-3 rounded-lg transition-colors duration-200 text-sm"
        >
          最初から
        </button>
      </div>
    </div>
  );
};

export default DiagnosisPanel;
