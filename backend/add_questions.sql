-- 導出可能な事実を質問として追加するSQL

-- 既存の質問を削除（重複を避けるため）
DELETE FROM questions WHERE fact_name IN (
    '会社がEビザの条件を満たします',
    '申請者がEビザの条件を満たします',
    '会社がEビザの投資の条件を満たします',
    '会社がEビザの貿易の条件を満たします',
    '申請者がEビザのマネージャー以上の条件を満たします',
    '申請者がEビザのスタッフの条件を満たします',
    'Blanket Lビザのマネージャーまたはスタッフの条件を満たします',
    'Bビザの申請ができます',
    'Bビザの申請条件を満たす（ESTAの認証は通る）',
    'Bビザの申請条件を満たす（ESTAの認証は通らない）'
);

-- 新しい質問を追加
INSERT INTO questions (fact_name, question_text, visa_type, priority, created_at, updated_at) VALUES
('会社がEビザの条件を満たします', '会社がEビザの条件を満たしますか？', 'E', 95, datetime('now'), datetime('now')),
('申請者がEビザの条件を満たします', '申請者がEビザの条件を満たしますか？', 'E', 85, datetime('now'), datetime('now')),
('会社がEビザの投資の条件を満たします', '会社がEビザの投資（E-2）の条件を満たしますか？', 'E', 90, datetime('now'), datetime('now')),
('会社がEビザの貿易の条件を満たします', '会社がEビザの貿易（E-1）の条件を満たしますか？', 'E', 90, datetime('now'), datetime('now')),
('申請者がEビザのマネージャー以上の条件を満たします', '申請者がEビザのマネージャー以上の条件を満たしますか？', 'E', 80, datetime('now'), datetime('now')),
('申請者がEビザのスタッフの条件を満たします', '申請者がEビザのスタッフ（専門職）の条件を満たしますか？', 'E', 80, datetime('now'), datetime('now')),
('Blanket Lビザのマネージャーまたはスタッフの条件を満たします', 'Blanket Lビザのマネージャーまたはスタッフの条件を満たしますか？', 'L', 85, datetime('now'), datetime('now')),
('Bビザの申請ができます', 'Bビザの申請ができますか？', 'B', 95, datetime('now'), datetime('now')),
('Bビザの申請条件を満たす（ESTAの認証は通る）', 'Bビザの申請条件を満たしますか？（ESTAの認証が通る場合）', 'B', 90, datetime('now'), datetime('now')),
('Bビザの申請条件を満たす（ESTAの認証は通らない）', 'Bビザの申請条件を満たしますか？（ESTAの認証が通らない場合）', 'B', 90, datetime('now'), datetime('now'));

-- 確認
SELECT COUNT(*) as added_count FROM questions WHERE fact_name IN (
    '会社がEビザの条件を満たします',
    '申請者がEビザの条件を満たします',
    '会社がEビザの投資の条件を満たします',
    '会社がEビザの貿易の条件を満たします',
    '申請者がEビザのマネージャー以上の条件を満たします',
    '申請者がEビザのスタッフの条件を満たします',
    'Blanket Lビザのマネージャーまたはスタッフの条件を満たします',
    'Bビザの申請ができます',
    'Bビザの申請条件を満たす（ESTAの認証は通る）',
    'Bビザの申請条件を満たす（ESTAの認証は通らない）'
);
