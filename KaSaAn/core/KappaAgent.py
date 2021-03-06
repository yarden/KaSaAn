#!/usr/bin/env python3

import re
from typing import List, Union

from .KappaEntity import KappaEntity
from .KappaSite import KappaPort, KappaCounter, KappaSite
from .KappaError import AgentParseError, TokenParseError, PortParseError, CounterParseError


class KappaAgent(KappaEntity):
    """Class for representing Kappa agents. I.e. <<A(b[1])>> or <<A(s{a}[.] a[1] b[.])>>."""

    def __init__(self, expression: str):
        self._raw_expression: str
        self._agent_name: str
        self._agent_signature: List[KappaSite]
        self._kappa_expression: str
        self._abundance_change: str

        expression = re.sub(r'\s+|\t+|\n+', ' ', expression)  # Remove line breaks, tabs, multi-spaces
        # Check if kappa expression's name & overall structure is valid
        agent_name_pat = r'([_~][a-zA-Z0-9_~+-]+|[a-zA-Z][a-zA-Z0-9_~+-]*)'
        agent_sign_pat = r'\(([^()]*)\)'
        agent_oper_pat = r'(\+|-)?'
        agent_pat = r'^' + agent_name_pat + agent_sign_pat + agent_oper_pat + r'$'
        matches = re.match(agent_pat, expression.strip())
        if not matches:
            matches = re.match(agent_pat, expression.strip() + '()')
        if not matches:
            raise AgentParseError('Invalid agent declaration <' + expression + '>')
        self._raw_expression = expression

        # process & assign to variables
        self._agent_name = matches.group(1)
        # process agent signature
        ag_signature = matches.group(2)
        if ag_signature == '':
            site_list = []
        else:
            # Kappa4 allows commas or whitespace as separators:
            # swap all commas for spaces, then split by whitespace, then sort alphabetically
            site_list = sorted(ag_signature.replace(',', ' ').split())
        self._agent_signature = []
        for entry in site_list:
            try:
                try:
                    site = KappaPort(entry)
                except PortParseError:
                    site = KappaCounter(entry)
            except CounterParseError:
                raise ValueError('Could not parse <' + entry + '> as a Port nor as a Counter')
            self._agent_signature.append(site)
        # process abundance operator, if present
        self._abundance_change = matches.group(3) if matches.group(3) else ''

        # canonicalize the kappa expression
        self._kappa_expression = \
            self._agent_name + r'(' + \
            ' '.join([str(site) for site in self._agent_signature]) + \
            ')' + self._abundance_change

    def __contains__(self, item) -> bool:
        # type parsing: try to make it an Agent, if that fails try a Site, if that tails, raise exception
        if (not type(item) is KappaPort) and (not type(item) is KappaCounter) and (not type(item) is KappaAgent):
            try:
                try:
                    try:
                        item = KappaAgent(item)
                    except AgentParseError:
                        item = KappaPort(item)
                except PortParseError:
                    item = KappaCounter(item)
            except CounterParseError:
                raise ValueError('Could not parse <' + item + '> as an Agent, nor as a Port, nor a Counter')
        # once item has been typed, or if it was properly typed, then we can decide what comparison to do
        if type(item) is KappaPort:
            for site in self._agent_signature:
                if item in site:
                    return True
        elif type(item) is KappaCounter:
            for site in self._agent_signature:
                if item == site:
                    return True
        elif type(item) is KappaAgent:
            if item._agent_name == self._agent_name:
                counter = 0
                for site in item._agent_signature:
                    if site in self:
                        counter += 1
                if counter == len(item._agent_signature):
                    return True

    def get_agent_name(self) -> str:
        """Return a string with the agent's name."""
        return self._agent_name

    def get_agent_signature(self) -> List[Union[KappaPort, KappaCounter]]:
        """Return a list of strings with the agent's signature."""
        return self._agent_signature

    def get_bond_identifiers(self) -> List[str]:
        """Return the list of bonds ending/starting at this agent, e.g. for <<A(a[.] b[1] c[2] d{a}[.])>> these would
         be the list ['1','2']."""
        agent_bonds = []
        all_bonds_data = []
        for item in self._agent_signature:
            if type(item) is KappaPort:
                all_bonds_data.append(item.get_port_current_bond())
                all_bonds_data.append(item.get_port_future_bond())
        for bond_data in all_bonds_data:
            if re.match(r'\d+', bond_data):
                agent_bonds.append(bond_data)
        return agent_bonds

    def get_abundance_change_operation(self) -> str:
        """Return the operation being performed on this agent: creation, deletion, or empty string."""
        return self._abundance_change


class KappaToken(KappaEntity):
    """Class for representing Kappa tokens. I.e. <<X>>, or <<ATP>>."""

    def __init__(self, expression: str):
        self._raw_expression: str
        self._token_name: str
        self._token_operation: str
        self._kappa_expression: str

        # Check if expression has valid structure
        token_name_pat = r'([_~][a-zA-Z0-9_~+-]+|[a-zA-Z][a-zA-Z0-9_~+-]*)'
        token_oper_pat = r'(.+\s)?'
        token_pat = '^' + token_oper_pat + token_name_pat + '$'
        matches = re.match(token_pat, expression.strip())
        if not matches:
            raise TokenParseError('Invalid token declaration <' + expression + '>')
        self._raw_expression = expression

        # assign to variables
        self._token_operation = matches.group(1).strip() if matches.group(1) else ''
        self._token_name = matches.group(2).strip()
        self._kappa_expression = self._raw_expression.strip()

    def get_token_name(self) -> str:
        return self._token_name

    def get_token_operation(self) -> str:
        return self._token_operation
