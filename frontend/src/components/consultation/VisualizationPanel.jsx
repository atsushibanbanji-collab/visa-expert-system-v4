import { useRef, useEffect } from 'react';

const VisualizationPanel = ({ visualizationData, currentQuestion }) => {
  const currentRuleRef = useRef(null);

  useEffect(() => {
    if (currentRuleRef.current) {
      currentRuleRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      });
    }
  }, [currentQuestion]);

  const getConditionColor = (status, isDerivable) => {
    if (status === 'satisfied') return 'bg-green-100 text-green-800 border-green-300';
    if (status === 'not_satisfied') return 'bg-red-100 text-red-800 border-red-300';
    if (isDerivable) return 'bg-purple-100 text-purple-800 border-purple-300';
    return 'bg-gray-100 text-gray-600 border-gray-300';
  };

  const getConclusionColor = (derived) => {
    return derived
      ? 'bg-blue-100 text-blue-800 border-blue-300'
      : 'bg-gray-100 text-gray-600 border-gray-300';
  };

  if (!visualizationData || !visualizationData.rules) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 h-full">
        <h2 className="text-2xl font-bold text-navy-900 mb-4">
          推論過程の可視化
        </h2>
        <p className="text-gray-600">診断を開始すると、ここに推論過程が表示されます。</p>
      </div>
    );
  }

  const { rules, fired_rules } = visualizationData;

  const relevantRules = rules.filter(rule => {
    if (rule.is_fired) return true;
    const hasEvaluatedCondition = rule.conditions.some(
      condition => condition.status !== 'unknown'
    );
    const relatedToCurrentQuestion = currentQuestion && rule.conditions.some(
      condition => condition.fact_name === currentQuestion
    );
    return hasEvaluatedCondition || relatedToCurrentQuestion;
  });

  const getRuleState = (rule) => {
    if (rule.is_fired) return 'fired';

    // 発火不可能なルールを先にチェック
    if (!rule.is_fireable) return 'unfireable';

    if (currentQuestion && rule.conditions.some(c => c.fact_name === currentQuestion)) {
      return 'current';
    }
    const hasEvaluatedCondition = rule.conditions.some(
      condition => condition.status !== 'unknown'
    );
    if (hasEvaluatedCondition) return 'evaluating';
    return 'pending';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 flex flex-col h-full max-h-[calc(100vh-250px)]">
      <div className="flex-shrink-0 mb-4">
        <h2 className="text-2xl font-bold text-navy-900 mb-4">
          推論過程の可視化
        </h2>

        {fired_rules && fired_rules.length > 0 && (
          <div className="bg-blue-50 rounded-lg p-3 mb-4 border-l-4 border-blue-600">
            <h3 className="text-xs font-semibold text-blue-900 mb-1">
              発火したルール: {fired_rules.length}
            </h3>
            <p className="text-xs text-blue-700">
              {fired_rules.join(', ')}
            </p>
          </div>
        )}

        <div className="text-xs text-gray-600 mb-2">
          表示中のルール: {relevantRules.length} / {rules.length}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto pr-2">
        <div className="space-y-3">
          {relevantRules.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>質問に回答すると、関連するルールがここに表示されます。</p>
            </div>
          ) : (
            relevantRules.map((rule) => {
              const ruleState = getRuleState(rule);
              const stateStyles = {
                fired: 'border-blue-500 bg-blue-50',
                current: 'border-yellow-400 bg-yellow-50',
                evaluating: 'border-orange-300 bg-orange-50',
                unfireable: 'border-red-300 bg-red-50 opacity-60',
                pending: 'border-gray-200 bg-white'
              };
              const badgeStyles = {
                fired: 'bg-blue-600 text-white',
                current: 'bg-yellow-500 text-white',
                evaluating: 'bg-orange-400 text-white',
                unfireable: 'bg-red-600 text-white',
                pending: 'bg-gray-400 text-white'
              };
              const badgeText = {
                fired: '発火済み',
                current: '今の質問に関係',
                evaluating: '推論中',
                unfireable: '発火不可能',
                pending: '未評価'
              };

              return (
                <div
                  key={rule.rule_id}
                  ref={ruleState === 'current' ? currentRuleRef : null}
                  className={`border-2 rounded-lg p-4 ${stateStyles[ruleState]}`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-bold text-navy-900">
                      {rule.rule_id}
                    </h3>
                    <span className={`text-xs px-2 py-1 rounded-full ${badgeStyles[ruleState]}`}>
                      {badgeText[ruleState]}
                    </span>
                  </div>

                  <div className="mb-3">
                    <p className="text-xs font-semibold text-gray-700 mb-2">
                      IF (条件 - {rule.operator}):
                    </p>
                    <div className="space-y-1">
                      {rule.conditions.map((condition, condIndex) => (
                        <div key={condIndex}>
                          <div
                            className={`text-xs p-2 rounded border ${getConditionColor(
                              condition.status,
                              condition.is_derivable
                            )}`}
                          >
                            {condition.fact_name}
                            {condition.is_derivable && (
                              <span className="ml-2 text-purple-600 font-semibold">
                                (導出可能)
                              </span>
                            )}
                          </div>
                          {condIndex < rule.conditions.length - 1 && (
                            <div className="text-xs text-gray-500 py-1 px-2">
                              {rule.operator}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <p className="text-xs font-semibold text-gray-700 mb-2">
                      THEN (結論):
                    </p>
                    <div
                      className={`text-xs p-2 rounded border ${getConclusionColor(
                        rule.conclusion_derived
                      )}`}
                    >
                      {rule.conclusion}
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

export default VisualizationPanel;
