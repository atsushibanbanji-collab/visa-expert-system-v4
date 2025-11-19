    def get_missing_critical_info(self) -> List[str]:
        """
        診断が完了できない場合の不足している重要情報を取得
        
        導出可能な中間結論は除外し、基本的な事実のみを返す

        Returns:
            不足している重要情報のリスト（fact_name）
        """
        missing_info = []

        # unknown_factsの中から、導出不可能な事実のみを抽出
        for fact_name in self.unknown_facts:
            # 導出可能な事実（中間結論）は除外
            if not self._is_derivable(fact_name):
                if fact_name not in missing_info:
                    missing_info.append(fact_name)

        return missing_info
