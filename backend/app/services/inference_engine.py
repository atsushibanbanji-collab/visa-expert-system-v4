from typing import Dict, List, Optional, Set
from sqlalchemy.orm import Session
from app.models.models import Rule, Condition, Question


class InferenceEngine:
    """前向き推論エンジン（Forward Chaining）"""

    def __init__(self, db: Session, visa_type: str):
        self.db = db
        self.visa_type = visa_type
        self.facts: Dict[str, bool] = {}  # Known facts
        self.derived_facts: Set[str] = set()  # Facts derived from rules (not asked)
        self.asked_questions: Set[str] = set()  # Questions already asked to user
        self.fired_rules: List[str] = []  # Rules that have been applied

    def add_fact(self, fact_name: str, value: bool):
        """Add a fact to the knowledge base"""
        self.facts[fact_name] = value
        if fact_name not in self.asked_questions:
            self.asked_questions.add(fact_name)

    def remove_fact(self, fact_name: str):
        """Remove a fact and all derived facts that depend on it"""
        if fact_name in self.facts:
            del self.facts[fact_name]
        if fact_name in self.asked_questions:
            self.asked_questions.remove(fact_name)

        # Remove derived facts that may depend on this
        # This is a simplified approach - clear all derived facts
        self.derived_facts.clear()
        self.fired_rules.clear()

        # Re-derive facts from remaining known facts
        self.forward_chain()

    def forward_chain(self) -> Dict[str, bool]:
        """
        前向き推論を実行
        既知の事実から新しい事実を導出
        """
        changed = True
        while changed:
            changed = False
            rules = self._get_applicable_rules()

            for rule in rules:
                if rule.rule_id in self.fired_rules:
                    continue

                can_fire, all_conditions_known = self._can_fire_rule(rule)

                # OR条件：1つでも満たされたら即座に発火
                # AND条件：全ての条件が既知で満たされている時のみ発火
                should_fire = False
                if rule.operator == "OR":
                    should_fire = can_fire  # 1つでも満たされたら発火
                else:  # AND
                    should_fire = all_conditions_known and can_fire  # 全条件が既知かつ満たされている

                if should_fire:
                    # Fire the rule
                    self.facts[rule.conclusion] = rule.conclusion_value
                    self.derived_facts.add(rule.conclusion)
                    self.fired_rules.append(rule.rule_id)
                    changed = True

        return self.facts

    def _get_applicable_rules(self) -> List[Rule]:
        """Get rules for the current visa type"""
        return (
            self.db.query(Rule)
            .filter(Rule.visa_type == self.visa_type)
            .order_by(Rule.priority.desc())
            .all()
        )

    def _can_fire_rule(self, rule: Rule) -> tuple[bool, bool]:
        """
        Check if a rule can fire
        Returns: (can_fire, all_conditions_known)
        """
        if rule.operator == "AND":
            all_conditions_known = True
            can_fire = True

            for condition in rule.conditions:
                if condition.fact_name not in self.facts:
                    all_conditions_known = False
                    can_fire = False
                    break

                if self.facts[condition.fact_name] != condition.expected_value:
                    can_fire = False
                    break

            return can_fire, all_conditions_known

        else:  # OR
            all_conditions_known = all(
                condition.fact_name in self.facts for condition in rule.conditions
            )
            can_fire = any(
                condition.fact_name in self.facts
                and self.facts[condition.fact_name] == condition.expected_value
                for condition in rule.conditions
            )

            return can_fire, all_conditions_known

    def get_next_question(self) -> Optional[str]:
        """
        次に質問すべき事実を選択
        ルール単位で完全に検証してから次のルールに進む（深さ優先探索）
        導出可能な事実がある場合、その事実を導出するルールを先に完全評価
        発火不可能なルールはスキップする
        最終結論が不可能になったら診断を終了
        """
        rules = self._get_applicable_rules()

        # Get derivable facts (facts that are conclusions of rules)
        derivable_facts = set()
        for rule in rules:
            derivable_facts.add(rule.conclusion)

        # ルールを優先度順にソート（高い優先度から）
        sorted_rules = sorted(rules, key=lambda r: r.priority, reverse=True)

        # 最終結論のルール（最も優先度が高く、「での申請ができます」が含まれる）を特定
        final_conclusion_rule = None
        for rule in sorted_rules:
            if "での申請ができます" in rule.conclusion:
                final_conclusion_rule = rule
                break

        # 最終結論のルールが発火不可能になったら診断を終了
        if final_conclusion_rule and not self._is_rule_potentially_fireable(final_conclusion_rule):
            return None  # 診断終了

        # 現在評価中のルールから質問を取得（深さ優先探索）
        for rule in sorted_rules:
            if not self._is_rule_potentially_fireable(rule):
                continue

            # このルールの次の質問を取得（再帰的に導出可能な条件を解決）
            next_question = self._get_next_question_for_rule(rule, derivable_facts, rules)
            if next_question:
                return next_question

        # 全ての条件が判明している場合
        return None

    def _get_next_question_for_rule(self, rule: Rule, derivable_facts: Set[str], all_rules: List[Rule]) -> Optional[str]:
        """
        指定されたルールの次の質問を取得（深さ優先探索）
        導出可能な条件がある場合、その条件を導出するルールを先に評価

        Returns:
            次に質問すべきfact_name、またはNone（全条件が既知または導出済み）
        """
        for condition in rule.conditions:
            fact_name = condition.fact_name

            # 既に分かっている事実はスキップ
            if fact_name in self.facts:
                continue

            # 導出可能な事実の場合、それを導出するルールを先に評価
            if fact_name in derivable_facts:
                # この事実を導出する全てのルールを見つける（優先度順）
                deriving_rules = [r for r in all_rules if r.conclusion == fact_name]
                deriving_rules = sorted(deriving_rules, key=lambda r: r.priority, reverse=True)

                # 各導出ルールを順番に評価
                for deriving_rule in deriving_rules:
                    if self._is_rule_potentially_fireable(deriving_rule):
                        # 再帰的にそのルールの質問を取得
                        nested_question = self._get_next_question_for_rule(deriving_rule, derivable_facts, all_rules)
                        if nested_question:
                            return nested_question

                # 全ての導出ルールの質問がない場合（全条件が既知または全て発火不可能）、次の条件へ
                continue

            # 導出不可能な条件なので質問として返す
            return fact_name

        # このルールの全条件が既知または導出可能
        return None

    def _is_rule_potentially_fireable(self, rule: Rule) -> bool:
        """
        ルールがまだ発火可能かチェック
        AND: 1つでもFalseなら発火不可能
        OR: 1つでもTrueなら発火確定（残りの条件は不要）
        """
        if rule.operator == "AND":
            # ANDの場合、1つでも条件が満たされていなければ発火不可能
            for condition in rule.conditions:
                if condition.fact_name in self.facts:
                    if self.facts[condition.fact_name] != condition.expected_value:
                        return False  # 発火不可能
            return True  # まだ発火可能

        else:  # OR
            # ORの場合、1つでも条件が満たされていれば発火確定
            for condition in rule.conditions:
                if condition.fact_name in self.facts:
                    if self.facts[condition.fact_name] == condition.expected_value:
                        return False  # もう発火確定なので残りの質問不要
            return True  # まだどの条件も満たされていない

    def get_conclusions(self) -> List[str]:
        """Get all derived conclusions"""
        conclusions = []
        for fact_name, value in self.facts.items():
            if fact_name in self.derived_facts and value:
                conclusions.append(fact_name)
        return conclusions

    def is_consultation_finished(self) -> bool:
        """Check if consultation is finished (no more questions to ask)"""
        return self.get_next_question() is None

    def get_rule_visualization(self) -> Dict:
        """
        推論過程の可視化用データを生成
        """
        rules = self._get_applicable_rules()
        visualization_rules = []

        for rule in rules:
            conditions_viz = []
            has_not_satisfied = False
            has_satisfied = False
            all_known = True

            for condition in rule.conditions:
                # Determine condition status
                if condition.fact_name in self.facts:
                    expected = condition.expected_value
                    actual = self.facts[condition.fact_name]
                    status = "satisfied" if actual == expected else "not_satisfied"

                    if status == "satisfied":
                        has_satisfied = True
                    else:
                        has_not_satisfied = True
                else:
                    status = "unknown"
                    all_known = False

                # Check if this condition is derivable
                is_derivable = any(
                    r.conclusion == condition.fact_name for r in rules
                )

                conditions_viz.append({
                    "fact_name": condition.fact_name,
                    "status": status,
                    "is_derivable": is_derivable,
                })

            # Check if conclusion is derived
            conclusion_derived = rule.conclusion in self.facts and self.facts[rule.conclusion] == rule.conclusion_value

            # Determine if rule is still fireable
            is_fireable = True
            if rule.operator == "AND":
                # AND: 1つでもnot_satisfiedがあれば発火不可能
                if has_not_satisfied:
                    is_fireable = False
            else:  # OR
                # OR: 全ての既知の条件がnot_satisfiedで、かつ1つも満たされていない場合は発火不可能
                if all_known and not has_satisfied:
                    is_fireable = False

            visualization_rules.append({
                "rule_id": rule.rule_id,
                "conditions": conditions_viz,
                "operator": rule.operator,
                "conclusion": rule.conclusion,
                "conclusion_derived": conclusion_derived,
                "is_fired": rule.rule_id in self.fired_rules,
                "is_fireable": is_fireable,
            })

        return {
            "rules": visualization_rules,
            "fired_rules": self.fired_rules,
        }
