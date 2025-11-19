from typing import Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session, joinedload
from app.models.models import Rule, Condition, Question
import copy


class InferenceEngine:
    """後向き推論エンジン（Backward Chaining）- ゴール指向推論"""

    def __init__(self, db: Session, visa_type: str):
        self.db = db
        self.visa_type = visa_type
        self.facts: Dict[str, bool] = {}  # Known facts (confirmed)
        self.uncertain_facts: Dict[str, bool] = {}  # Facts set from "わからない" (not confirmed)
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

    def add_uncertain_fact(self, fact_name: str, value: bool):
        """Add an uncertain fact (from '分からない' answer)"""
        self.uncertain_facts[fact_name] = value
        self.unknown_facts.add(fact_name)
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
        Check if a rule can fire (using only confirmed facts, not uncertain)
        Returns: (can_fire, all_conditions_known)
        """
        if rule.operator == "AND":
            all_conditions_known = True
            can_fire = True

            for condition in rule.conditions:
                # Only use confirmed facts (not uncertain_facts)
                if condition.fact_name not in self.facts:
                    all_conditions_known = False
                    can_fire = False
                    break

                if self.facts[condition.fact_name] != condition.expected_value:
                    can_fire = False
                    break

            return can_fire, all_conditions_known

        else:  # OR
            # Check if all conditions are known (in facts)
            all_conditions_known = all(
                condition.fact_name in self.facts for condition in rule.conditions
            )
            # Can only fire if at least one confirmed fact satisfies the condition
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

        # 重要：このゴール自体が高優先度の質問かチェック
        # 導出可能でも、優先度が高ければ直接質問する
        if goal not in self.asked_questions:
            goal_priority = self._get_question_priority(goal)
            if goal_priority >= 80:
                # 高優先度の導出可能な質問は直接聞く
                return goal

        # 代替パスを評価：未評価でないルールを優先
        available_rules = []
        uncertain_rules = []

        for rule in rules:
            # 既にこのルールが発火している
            if rule.rule_id in self.fired_rules:
                continue

            # このルールが発火不可能かチェック
            if self._is_rule_impossible(rule):
                continue

            # このルールが「わからない」条件を含むかチェック
            if self._has_unknown_conditions(rule):
                uncertain_rules.append(rule)
            else:
                available_rules.append(rule)

        # まず「わからない」条件を含まないルールを試す（代替パス）
        for rule in available_rules:
            question = self._find_question_for_rule(rule, visited.copy())
            if question:
                return question

        # 代替パスがない場合、「わからない」条件を含むルールも試す
        for rule in uncertain_rules:
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

            # 既に分かっている事実（「はい」「いいえ」で回答済み、確定）
            if fact_name in self.facts:
                continue

            # 「わからない」で不確実な事実として記録されている場合
            if fact_name in self.uncertain_facts:
                # AND条件の場合はスキップ（他の条件も聞く必要がある）
                if rule.operator == "AND":
                    continue
                # OR条件の場合は次の選択肢も聞く（確定した事実がないため）
                # → continueせずに次のループへ
                continue

            # 「わからない」で保留中（導出可能な質問の場合）→ 詳細質問に進む
            if fact_name in self.unknown_facts:
                # この条件が導出可能なら、詳細な質問を探す
                if self._is_derivable(fact_name):
                    question = self._find_question_for_goal(fact_name, visited)
                    if question:
                        return question
                # 導出できない場合は次の条件へ
                continue

            # この条件は他のルールで導出可能か？
            if self._is_derivable(fact_name):
                # 導出可能な事実の質問優先度をチェック
                question_priority = self._get_question_priority(fact_name)

                # 高優先度（80以上）の質問は直接聞く（まだ質問していない場合）
                if question_priority >= 80 and fact_name not in self.asked_questions:
                    return fact_name

                # 低優先度の場合は、再帰的に詳細な質問を探す
                question = self._find_question_for_goal(fact_name, visited)
                if question:
                    return question
                # 詳細質問が見つからない場合は、次の条件へ進む
                # （このルールの他の条件が満たされていない可能性があるため）
                continue

            # 導出不可能なので、直接質問する
            return fact_name

        # このルールの全条件が既知または導出不可能
        return None

    def _is_derivable(self, fact_name: str) -> bool:
        """指定された事実が他のルールの結論として導出可能か"""
        return len(self._get_rules_with_conclusion(fact_name)) > 0

    def _get_question_priority(self, fact_name: str) -> int:
        """
        質問の優先度を取得

        Args:
            fact_name: 質問のfact_name

        Returns:
            優先度（数値が大きいほど優先度が高い）、デフォルトは0
        """
        question = self.db.query(Question).filter(Question.fact_name == fact_name).first()
        return question.priority if question else 0

    def _has_unknown_conditions(self, rule: Rule) -> bool:
        """ルールが「わからない」と回答された条件を含むかチェック"""
        for condition in rule.conditions:
            if condition.fact_name in self.unknown_facts:
                return True
        return False

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
        """Get final visa application conclusions only (not intermediate facts)"""
        conclusions = []
        for fact_name, value in self.facts.items():
            if fact_name in self.derived_facts and value:
                # Only return final conclusions (visa application results)
                # These end with "ビザでの申請ができます" or "ビザの申請ができます"
                if "申請ができます" in fact_name or "申請が可能です" in fact_name:
                    conclusions.append(fact_name)
        return conclusions

    def is_consultation_finished(self) -> bool:
        """Check if consultation is finished (no more questions to ask)"""
        return self.get_next_question() is None

    def finalize_diagnosis(self):
        """
        診断終了時に不確実な事実を確定させて最終判定
        uncertain_factsの内容をfactsに移してforward_chainを実行
        """
        if not self.uncertain_facts:
            return

        # uncertain_factsをfactsに移す
        for fact_name, value in self.uncertain_facts.items():
            if fact_name not in self.facts:  # 既に確定している場合は上書きしない
                self.facts[fact_name] = value

        # 最終的なforward_chainを実行
        self.forward_chain()

    def get_missing_critical_info(self) -> List[str]:
        """
        診断が完了できない場合の不足している重要情報を取得

        導出可能な中間結論は除外し、基本的な事実のみを返す

        Returns:
            不足している重要情報のリスト（fact_name）
        """
        missing_info = []

        # unknown_factsの中から、導出不可能な事実のみを抽出
        print(f"DEBUG: unknown_facts = {self.unknown_facts}")
        for fact_name in self.unknown_facts:
            # 導出可能な事実（中間結論）は除外
            is_derivable = self._is_derivable(fact_name)
            print(f"DEBUG: {fact_name} -> is_derivable={is_derivable}")
            if not is_derivable:
                if fact_name not in missing_info:
                    missing_info.append(fact_name)

        print(f"DEBUG: missing_info result = {missing_info}")
        return missing_info

    def _can_derive_from_alternative(self, fact_name: str) -> bool:
        """
        指定された事実を代替パスで導出できるかチェック

        Args:
            fact_name: チェックする事実名

        Returns:
            代替パスで導出可能ならTrue
        """
        # この事実を結論とするルールがあるか
        rules = self._get_rules_with_conclusion(fact_name)

        for rule in rules:
            # このルールが発火可能かチェック
            if self._is_rule_impossible(rule):
                continue

            # このルールが「わからない」条件を含まないかチェック
            has_unknown = False
            all_known = True

            for condition in rule.conditions:
                if condition.fact_name in self.unknown_facts:
                    has_unknown = True
                if condition.fact_name not in self.facts:
                    all_known = False

            # 「わからない」条件がなく、まだ未確定の条件があれば代替可能
            if not has_unknown and not all_known:
                return True

        return False

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
                elif condition.fact_name in self.unknown_facts:
                    # 「わからない」と回答された条件
                    status = "uncertain"
                    all_known = False
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

    def save_snapshot(self) -> dict:
        """
        現在のエンジンの状態のスナップショットを保存

        Returns:
            状態のスナップショット (dict)
        """
        return {
            "facts": copy.deepcopy(self.facts),
            "uncertain_facts": copy.deepcopy(self.uncertain_facts),
            "derived_facts": copy.deepcopy(self.derived_facts),
            "asked_questions": copy.deepcopy(self.asked_questions),
            "fired_rules": copy.deepcopy(self.fired_rules),
            "unknown_facts": copy.deepcopy(self.unknown_facts),
        }

    def restore_snapshot(self, snapshot: dict):
        """
        保存した状態のスナップショットからエンジンの状態を復元

        Args:
            snapshot: save_snapshot()で保存したスナップショット
        """
        self.facts = copy.deepcopy(snapshot.get("facts", {}))
        self.uncertain_facts = copy.deepcopy(snapshot.get("uncertain_facts", {}))
        self.derived_facts = copy.deepcopy(snapshot.get("derived_facts", set()))
        self.asked_questions = copy.deepcopy(snapshot.get("asked_questions", set()))
        self.fired_rules = copy.deepcopy(snapshot.get("fired_rules", []))
        self.unknown_facts = copy.deepcopy(snapshot.get("unknown_facts", set()))
