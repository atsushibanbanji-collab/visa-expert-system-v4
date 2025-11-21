const VisaTypeSelection = ({ onSelectVisaType }) => {
  const visaTypes = [
    {
      type: 'E',
      title: 'Eビザ（投資・貿易ビザ）',
      description: '日米間の投資や貿易を行う企業の従業員が対象'
    },
    {
      type: 'L',
      title: 'Lビザ（企業内転勤ビザ）',
      description: 'グループ会社間の異動（マネージャーまたはスペシャリスト）'
    },
    {
      type: 'B',
      title: 'Bビザ（商用・観光ビザ）',
      description: '短期の商用活動、会議、研修などが対象'
    }
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-8 max-w-4xl mx-auto">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-navy-900 mb-3">
          ビザ選定エキスパートシステム
        </h1>
        <p className="text-gray-600 text-lg">
          判定したいビザタイプを選択してください
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {visaTypes.map((visa) => (
          <button
            key={visa.type}
            onClick={() => onSelectVisaType(visa.type)}
            className="group bg-gradient-to-br from-navy-50 to-white border-2 border-navy-200 hover:border-navy-600 hover:shadow-xl rounded-xl p-6 text-left transition-all duration-200 transform hover:scale-105 flex flex-col min-h-[200px]"
          >
            <h3 className="text-lg font-bold text-navy-900 mb-3 group-hover:text-navy-600 whitespace-nowrap">
              {visa.title}
            </h3>
            <p className="text-gray-600 text-sm leading-relaxed flex-1">
              {visa.description}
            </p>
            <div className="mt-4 text-navy-600 font-semibold text-sm flex items-center">
              診断を開始
              <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
            </div>
          </button>
        ))}
      </div>

      <div className="mt-8">
        <button
          onClick={() => onSelectVisaType('ALL')}
          className="w-full bg-gradient-to-r from-navy-600 to-navy-800 hover:from-navy-700 hover:to-navy-900 text-white font-bold py-6 px-8 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
        >
          <div className="flex items-center justify-center">
            <span className="text-xl">全てのビザタイプを一度に診断</span>
            <span className="ml-3 text-2xl">→</span>
          </div>
          <p className="text-sm text-navy-100 mt-2">
            E、L、Bビザを順番に診断し、最適なビザを見つけます
          </p>
        </button>
      </div>

      <div className="mt-8 bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
        <p className="text-sm text-blue-800">
          <strong>ヒント:</strong> 各ビザタイプに応じた質問が表示されます。適切なビザを選択することで、効率的な診断が可能になります。
        </p>
      </div>
    </div>
  );
};

export default VisaTypeSelection;
