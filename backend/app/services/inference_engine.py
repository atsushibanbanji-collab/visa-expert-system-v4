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

                if all_conditions_known and can_fire:
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
        ルールの優先度順に、条件を順番に質問していく
        導出可能な事実は質問しない
        """
        rules = self._get_applicable_rules()

        # Get derivable facts (facts that are conclusions of rules)
        derivable_facts = set()
        for rule in rules:
            derivable_facts.add(rule.conclusion)

        # ルールを優先度順にソート（高い優先度から）
        sorted_rules = sorted(rules, key=lambda r: r.priority, reverse=True)

        # 各ルールの条件を順番にチェック
        for rule in sorted_rules:
            for condition in rule.conditions:
                fact_name = condition.fact_name

                # 既に分かっている事実はスキップ
                if fact_name in self.facts:
                    continue

                # 導出可能な事実はスキップ
                if fact_name in derivable_facts:
                    continue

                # この事実を質問として返す
                return fact_name

        # 全ての条件が判明している場合
        return None

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
            for condition in rule.conditions:
                # Determine condition status
                if condition.fact_name in self.facts:
                    expected = condition.expected_value
                    actual = self.facts[condition.fact_name]
                    status = "satisfied" if actual == expected else "not_satisfied"
                else:
                    status = "unknown"

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

            visualization_rules.append({
                "rule_id": rule.rule_id,
                "conditions": conditions_viz,
                "operator": rule.operator,
                "conclusion": rule.conclusion,
                "conclusion_derived": conclusion_derived,
                "is_fired": rule.rule_id in self.fired_rules,
            })

        return {
            "rules": visualization_rules,
            "fired_rules": self.fired_rules,
        }
