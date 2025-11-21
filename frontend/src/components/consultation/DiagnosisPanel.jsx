const DiagnosisPanel = ({
  currentQuestion,
  isDerivable,
  onAnswer,
  onBack,
  onRestart,
  conclusions,
  unknownFacts,
  isFinished,
  insufficientInfo,
  missingCriticalInfo,
  uncertainFactsLogic,
  questionHistory,
  loading,
  currentVisaType,
  allVisaMode,
  allConclusions
}) => {
  const handleAnswer = (answer) => {
    if (currentQuestion) {
      onAnswer(currentQuestion, answer);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 h-full flex flex-col overflow-hidden">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-navy-900">
          ビザ選定診断
        </h1>
        {allVisaMode && currentVisaType && (
          <div className="mt-2 bg-navy-100 text-navy-800 px-3 py-2 rounded-lg text-sm font-semibold">
            現在診断中: {currentVisaType}ビザ
          </div>
        )}
      </div>

      {/* Progress indicator */}
      {questionHistory.length > 0 && (
        <div className="mb-4">
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
      <div className="flex-1 mb-2 overflow-y-auto">
        {!isFinished && currentQuestion && (
          <div className="bg-navy-50 rounded-lg p-5 border-l-4 border-navy-600">
            <p className="text-base font-medium text-navy-900 mb-3">
              {currentQuestion}
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => handleAnswer(true)}
                disabled={loading}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-2.5 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                はい
              </button>
              <button
                onClick={() => handleAnswer(false)}
                disabled={loading}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-2.5 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                いいえ
              </button>
              <button
                onClick={() => handleAnswer(null)}
                disabled={loading}
                className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2.5 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                分からない
              </button>
            </div>
          </div>
        )}

        {isFinished && (
          <div>
            {allVisaMode && allConclusions && Object.keys(allConclusions).length > 0 ? (
              <div className="bg-green-50 rounded-lg p-4 border-l-4 border-green-600">
                <h2 className="text-lg font-bold text-green-900 mb-3">
                  診断結果（全ビザタイプ）
                </h2>
                <div className="space-y-4">
                  {Object.entries(allConclusions).map(([visaType, visaConclusions]) => (
                    <div key={visaType} className="bg-white rounded-lg p-3 shadow border-l-4 border-navy-500">
                      <h3 className="text-base font-bold text-navy-900 mb-2">
                        {visaType}ビザ
                      </h3>
                      {visaConclusions && visaConclusions.length > 0 ? (
                        <ul className="space-y-1">
                          {visaConclusions.map((conclusion, index) => (
                            <li key={index} className="text-sm text-gray-700 flex items-start">
                              <span className="text-green-600 mr-2">✓</span>
                              {conclusion}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-sm text-gray-500 italic">
                          このビザタイプでは申請できません
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ) : insufficientInfo ? (
              <div className="bg-yellow-50 rounded-lg p-4 border-l-4 border-yellow-600">
                <h2 className="text-lg font-bold text-yellow-900 mb-3">
                  診断できませんでした
                </h2>
                <p className="text-sm text-gray-700 mb-3">
                  情報が不足しているため、診断を完了できませんでした。
                </p>
                {missingCriticalInfo && missingCriticalInfo.length > 0 && (
                  <div className="bg-red-100 rounded-lg p-3 border-l-4 border-red-500">
                    <p className="text-xs font-semibold text-red-900 mb-1">
                      以下の条件について「分からない」と回答されています：
                    </p>
                    <ul className="list-disc list-inside space-y-0.5 text-xs text-red-800">
                      {missingCriticalInfo.map((fact, index) => (
                        <li key={index}>{fact}</li>
                      ))}
                    </ul>
                    <p className="text-xs text-red-700 mt-2">
                      これらの情報を確認してから再度診断してください。
                    </p>
                  </div>
                )}
              </div>
            ) : (
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
                    {(() => {
                      console.log('[DiagnosisPanel] missingCriticalInfo:', missingCriticalInfo);
                      console.log('[DiagnosisPanel] uncertainFactsLogic:', uncertainFactsLogic);
                      console.log('[DiagnosisPanel] isFinished:', isFinished);
                      console.log('[DiagnosisPanel] insufficientInfo:', insufficientInfo);
                      console.log('[DiagnosisPanel] conclusions:', conclusions);
                      return null;
                    })()}
                    {uncertainFactsLogic && uncertainFactsLogic.groups && uncertainFactsLogic.groups.length > 0 && (
                      <div className="bg-yellow-50 rounded-lg p-3 border-l-4 border-yellow-500">
                        <p className="text-xs font-semibold text-yellow-900 mb-2">
                          ※ 以下の条件については「分からない」と回答されているため、これらが満たされている前提での結果です：
                        </p>
                        <div className="space-y-2">
                          {uncertainFactsLogic.groups.map((group, groupIndex) => (
                            <div key={groupIndex} className="bg-white rounded p-2 border border-yellow-300">
                              <p className="text-xs font-semibold text-yellow-900 mb-1">
                                {group.conclusion}
                              </p>
                              <div className="text-xs text-yellow-800">
                                {group.uncertain_conditions.map((condition, condIndex) => (
                                  <div key={condIndex}>
                                    <span className="ml-2">• {condition}</span>
                                    {condIndex < group.uncertain_conditions.length - 1 && (
                                      <span className="ml-2 font-bold text-yellow-900">
                                        {group.operator === 'AND' ? 'かつ' : 'または'}
                                      </span>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
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
        )}
      </div>

      {/* Navigation buttons */}
      <div className="flex gap-3">
        <button
          onClick={onBack}
          disabled={questionHistory.length <= 1 || loading}
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
