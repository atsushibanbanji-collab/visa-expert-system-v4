from typing import List, Set, Dict
from sqlalchemy.orm import Session
from app.models.models import Rule, Condition, ValidationResult
from app.models.schemas import ValidationIssue, ValidationResponse
from datetime import datetime


class ValidationService:
    """整合性チェックサービス"""

    def __init__(self, db: Session):
        self.db = db

    def validate_rules(self, visa_type: str) -> ValidationResponse:
        """ルールの整合性をチェック"""
        issues = []

        # Get rules for visa type
        rules = self.db.query(Rule).filter(Rule.visa_type == visa_type).all()

        # Check for contradictions
        issues.extend(self._check_contradictions(rules))

        # Check for unreachable rules
        issues.extend(self._check_unreachable_rules(rules))

        # Check for circular dependencies
        issues.extend(self._check_circular_dependencies(rules))

        # Save validation results
        for issue in issues:
            result = ValidationResult(
                visa_type=visa_type,
                validation_type=issue.validation_type,
                severity=issue.severity,
                message=issue.message,
                details=issue.details,
            )
            self.db.add(result)

        self.db.commit()

        is_valid = not any(issue.severity == "error" for issue in issues)

        return ValidationResponse(
            is_valid=is_valid,
            issues=issues,
            checked_at=datetime.utcnow(),
        )

    def _check_contradictions(self, rules: List[Rule]) -> List[ValidationIssue]:
        """矛盾の検出：同じ条件から異なる結論が導出される"""
        issues = []

        # Group rules by their conditions
        condition_groups: Dict[str, List[Rule]] = {}

        for rule in rules:
            # Create a hashable key from conditions
            conditions_key = self._get_conditions_key(rule)
            if conditions_key not in condition_groups:
                condition_groups[conditions_key] = []
            condition_groups[conditions_key].append(rule)

        # Check for rules with same conditions but different conclusions
        for conditions_key, rule_group in condition_groups.items():
            if len(rule_group) > 1:
                conclusions = set((r.conclusion, r.conclusion_value) for r in rule_group)
                if len(conclusions) > 1:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            validation_type="contradiction",
                            message=f"矛盾: 同じ条件から異なる結論が導出されます",
                            details={
                                "rules": [r.rule_id for r in rule_group],
                                "conclusions": [
                                    f"{r.conclusion}={r.conclusion_value}" for r in rule_group
                                ],
                            },
                        )
                    )

        return issues

    def _check_unreachable_rules(self, rules: List[Rule]) -> List[ValidationIssue]:
        """到達不可能なルールの検出"""
        issues = []

        # Get all derivable facts (conclusions)
        derivable_facts = set(r.conclusion for r in rules)

        # Get all facts that can be asked (appear in conditions but not derivable)
        all_condition_facts = set()
        for rule in rules:
            for condition in rule.conditions:
                all_condition_facts.add(condition.fact_name)

        askable_facts = all_condition_facts - derivable_facts

        # Check if each rule's conditions can be satisfied
        for rule in rules:
            required_facts = set(c.fact_name for c in rule.conditions)

            # Check if all required facts are either askable or derivable
            unreachable_facts = required_facts - askable_facts - derivable_facts

            if unreachable_facts:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        validation_type="unreachable",
                        message=f"到達不可能: ルール {rule.rule_id} の条件に到達できない事実があります",
                        details={
                            "rule_id": rule.rule_id,
                            "unreachable_facts": list(unreachable_facts),
                        },
                    )
                )

        return issues

    def _check_circular_dependencies(self, rules: List[Rule]) -> List[ValidationIssue]:
        """循環参照の検出"""
        issues = []

        # Build dependency graph: conclusion -> conditions
        dependency_graph: Dict[str, Set[str]] = {}

        for rule in rules:
            conclusion = rule.conclusion
            if conclusion not in dependency_graph:
                dependency_graph[conclusion] = set()

            for condition in rule.conditions:
                dependency_graph[conclusion].add(condition.fact_name)

        # Check for cycles using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            if node in dependency_graph:
                for neighbor in dependency_graph[node]:
                    if neighbor not in visited:
                        if has_cycle(neighbor, path[:]):
                            return True
                    elif neighbor in rec_stack:
                        # Found cycle
                        cycle_start = path.index(neighbor)
                        cycle = path[cycle_start:] + [neighbor]
                        issues.append(
                            ValidationIssue(
                                severity="error",
                                validation_type="circular",
                                message=f"循環参照: {' -> '.join(cycle)}",
                                details={"cycle": cycle},
                            )
                        )
                        return True

            rec_stack.remove(node)
            return False

        for node in dependency_graph:
            if node not in visited:
                has_cycle(node, [])

        return issues

    def _get_conditions_key(self, rule: Rule) -> str:
        """Create a hashable key from rule conditions"""
        conditions = sorted(
            [(c.fact_name, c.expected_value) for c in rule.conditions]
        )
        return f"{rule.operator}:{str(conditions)}"
