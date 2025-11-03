from typing import Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session, joinedload
from app.models.models import Rule, Condition, Question


class InferenceEngine:
    """後向き推論エンジン（Backward Chaining）- ゴール指向推論"""

    def __init__(self, db: Session, visa_type: str):
        self.db = db
        self.visa_type = visa_type
        self.facts: Dict[str, bool] = {}  # Known facts
        self.derived_facts: Set[str] = set()  # Facts derived from rules (not asked)
        self.asked_questions: Set[str] = set()  # Questions already asked to user
        self.fired_rules: List[str] = []  # Rules that have been applied
        self.unknown_facts: Set[str] = set()  # Facts answered as "分からない"
        self.goal = f"{visa_type}ビザでの申請ができます"  # Final goal
        self.all_rules = None  # Cache for all rules
        self.rules_by_conclusion = {}  # Cache: conclusion -> rules

    def add_fact(self, fact_name: str, value: bool):
        """Add a fact to the knowledge base"""
        self.facts[fact_name] = value
        if fact_name not in self.asked_questions:
            self.asked_questions.add(fact_name)

    def add_unknown_fact(self, fact_name: str):
        """Mark a fact as unknown (user answered '分からない')"""
        self.unknown_facts.add(fact_name)
        if fact_name not in self.asked_questions:
            self.asked_questions.add(fact_name)

    def remove_fact(self, fact_name: str):
        """Remove a fact and all derived facts that depend on it"""
        if fact_name in self.facts:
            del self.facts[fact_name]
        if fact_name in self.asked_questions:
            self.asked_questions.remove(fact_name)
        if fact_name in self.unknown_facts:
            self.unknown_facts.remove(fact_name)

        # Remove derived facts that may depend on this
        # This is a simplified approach - clear all derived facts
        self.derived_facts.clear()
        self.fired_rules.clear()

        # Clear caches (for backward chaining)
        self.all_rules = None
        self.rules_by_conclusion.clear()

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
        """Get rules for the current visa type (cached)"""
        if self.all_rules is None:
            self.all_rules = (
                self.db.query(Rule)
                .options(joinedload(Rule.conditions))  # Eager load conditions
                .filter(Rule.visa_type == self.visa_type)
                .order_by(Rule.priority.desc())
                .all()
            )
            # Build conclusion -> rules cache
            for rule in self.all_rules:
                if rule.conclusion not in self.rules_by_conclusion:
                    self.rules_by_conclusion[rule.conclusion] = []
                self.rules_by_conclusion[rule.conclusion].append(rule)
        return self.all_rules

    def _get_rules_with_conclusion(self, conclusion: str) -> List[Rule]:
        """Get all rules that have the given conclusion"""
        if not self.rules_by_conclusion:
            self._get_applicable_rules()  # Initialize cache
        return self.rules_by_conclusion.get(conclusion, [])

    def _can_fire_rule(self, rule: Rule) -> Tuple[bool, bool]:
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
        バックワードチェイニング: ゴールから逆算して次に必要な質問を見つける

        基本原理:
        1. ゴールを達成するために必要なルールを見つける
        2. そのルールの条件を満たすために必要な事実を探す
        3. 事実が導出可能なら、再帰的にその事実をゴールとして探索
        4. 導出不可能なら、ユーザーに質問
        """
        return self._find_question_for_goal(self.goal)

    def _find_question_for_goal(self, goal: str, visited: Set[str] = None) -> Optional[str]:
        """
        指定されたゴールを達成するために必要な質問を探す（再帰的）

        Args:
            goal: 達成したいゴール（結論）
            visited: 循環参照を避けるための訪問済みゴールセット

        Returns:
            次に質問すべきfact_name、またはNone
        """
        if visited is None:
            visited = set()

        # 循環参照を避ける
        if goal in visited:
            return None
        visited.add(goal)

        # 既にゴールが達成されている場合
        if goal in self.facts:
            return None

        # このゴールを達成するためのルールを取得（優先度順）
        rules = self._get_rules_with_conclusion(goal)
        if not rules:
            # このゴールを達成するルールがない（導出不可能）
            return None

        for rule in rules:
            # 既にこのルールが発火している
            if rule.rule_id in self.fired_rules:
                continue

            # このルールが発火不可能かチェック
            if self._is_rule_impossible(rule):
                continue

            # このルールの条件を満たすために必要な質問を探す
            question = self._find_question_for_rule(rule, visited.copy())
            if question:
                return question

        # このゴールを達成するための質問が見つからない
        return None

    def _find_question_for_rule(self, rule: Rule, visited: Set[str]) -> Optional[str]:
        """
        指定されたルールを発火させるために必要な質問を探す

        Args:
            rule: 評価するルール
            visited: 循環参照を避けるための訪問済みゴールセット

        Returns:
            次に質問すべきfact_name、またはNone
        """
        for condition in rule.conditions:
            fact_name = condition.fact_name

            # 既に分かっている事実（「はい」「いいえ」で回答済み）
            if fact_name in self.facts:
                continue

            # 「わからない」で保留中（導出を試みる）
            if fact_name in self.unknown_facts:
                continue

            # この条件は他のルールで導出可能か？
            if self._is_derivable(fact_name):
                # 再帰的に、この条件をゴールとして質問を探す
                question = self._find_question_for_goal(fact_name, visited)
                if question:
                    return question
                # 導出できない場合は次の条件へ
                continue

            # 導出不可能なので、直接質問する
            return fact_name

        # このルールの全条件が既知または導出不可能
        return None

    def _is_derivable(self, fact_name: str) -> bool:
        """指定された事実が他のルールの結論として導出可能か"""
        return len(self._get_rules_with_conclusion(fact_name)) > 0

    def _is_rule_impossible(self, rule: Rule) -> bool:
        """
        ルールが発火不可能か判定（ANDルールで1つでもFalse、ORルールで全てFalse）
        """
        if rule.operator == "AND":
            # ANDの場合、1つでも条件がFalseなら発火不可能
            for condition in rule.conditions:
                if condition.fact_name in self.facts:
                    if self.facts[condition.fact_name] != condition.expected_value:
                        return True
            return False
        else:  # OR
            # ORの場合、全ての既知条件がFalseなら発火不可能
            has_known_condition = False
            for condition in rule.conditions:
                if condition.fact_name in self.facts:
                    has_known_condition = True
                    if self.facts[condition.fact_name] == condition.expected_value:
                        return False  # 1つでも満たされているので発火可能
            # 全ての既知条件が不一致、かつ未知の条件がない場合のみ不可能
            if has_known_condition:
                # 未知の条件があるかチェック
                has_unknown = any(c.fact_name not in self.facts for c in rule.conditions)
                return not has_unknown
            return False


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
