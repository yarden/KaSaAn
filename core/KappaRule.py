#!/usr/bin/env python3

from .KappaEntity import KappaEntity
from .KappaAgent import KappaAgent, KappaToken
from .KappaComplex import KappaComplex
from .KappaError import RuleParseError
import re
from typing import List


class KappaRule(KappaEntity):
    """Class to represent a Kappa Rule, WIP."""
    def __init__(self, raw_expression: str):
        self._name: str
        self._pattern: str
        self._rate_pri: str
        self._rate_uni: str
        self._agent_expression: str
        self._token_expression: str
        self._agents: List[KappaAgent]
        self._tokens: List[KappaToken]
        self._kappa_expression: str

        # remove spaces, breaks, comments
        digested_rule = re.sub('\s+|\t+|\n+', ' ', raw_expression)  # Remove line breaks, tabs, multi-spaces
        digested_rule = re.sub('/\*[^*/]*\*/', '', digested_rule)   # Remove in-line comment
        digested_rule = digested_rule.split('//')[0]                # Remove trailing comment, leading/trialing spaces
        digested_rule = digested_rule.strip()

        # extract rule name, Kappa pattern, rates
        rule_components = re.match("('.+')?\s*(.+)\s*@\s*([^{]+)\s*(?:{([^}]+)})?", digested_rule)
        self._name = rule_components.group(1).strip() if rule_components.group(1) else None
        self._pattern = rule_components.group(2).strip() if rule_components.group(2) else None
        self._rate_pri = rule_components.group(3).strip() if rule_components.group(3) else None
        self._rate_uni = rule_components.group(4).strip() if rule_components.group(4) else None
        if not self._pattern:
            raise RuleParseError('No rule expression found in <' + digested_rule + '>')
        if not self._rate_pri:
            raise RuleParseError('No primary rate found in <' + digested_rule + '>')

        # extract & process entities: agents & tokens
        agents_and_tokens = re.match('([^|]+)?\s*\|?\s*(.+)?', self._pattern)
        self._agent_expression = agents_and_tokens.group(1).strip() if agents_and_tokens.group(1) else None
        self._token_expression = agents_and_tokens.group(2).strip() if agents_and_tokens.group(2) else None
        self._agents = KappaComplex(self._agent_expression).get_all_agents()
        self._tokens = [KappaToken(item) for item in self._token_expression.split(',')]

        # canonicalize the kappa expression
        c_name = self._name + ' ' if self._name else ''
        c_agnt = ', '.join([str(ag) for ag in self._agents])
        c_tokn = ' | ' + ', '.join([str(tk) for tk in self._tokens]) if self._tokens else ''
        c_rt_p = ' @ ' + self._rate_pri
        c_rt_u = ' { ' + self._rate_uni + ' } ' if self._rate_uni else ''
        self._kappa_expression = c_name + c_agnt + c_tokn + c_rt_p + c_rt_u

    def get_name(self) -> str:
        """Returns a string with the name of this rule."""
        return self._name

    def get_rate_primary(self) -> str:
        """Returns a string with the primary (usually binary) rate for this rule."""
        return self._rate_pri

    def get_rate_unary(self) -> str:
        """Returns a string with the unary rate for this rule, if specified."""
        return self._rate_uni

    def get_agents(self) -> List[KappaAgent]:
        """Returns a list with the KappaAgents in this rule."""
        return self._agents

    def get_tokens(self) -> List[KappaToken]:
        """Returns a list with the KappaTokens in this rule."""
        return self._tokens