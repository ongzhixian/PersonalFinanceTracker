import re
from collections import defaultdict

class SpecScriptParser:
    def __init__(self):
        self.sections = []
        self.current_section = None
        self.current_section_name = None
        self.current_section_title = None
        self.indent_stack = [0]

    def parse(self, lines):
        result = []
        self.sections = []
        self.current_section = None
        self.current_section_name = None
        self.current_section_title = None
        self.indent_stack = [0]

        for line in lines:
            raw_line = line
            line = line.rstrip('\n')
            if not line.strip() or line.strip().startswith('#'):
                continue  # Skip blank lines and comments

            indent = len(line) - len(line.lstrip(' '))
            content = line.lstrip(' ')

            # Section header
            if content.startswith('@'):
                # Save previous section
                if self.current_section:
                    self.sections.append(self.current_section)
                # Parse section name and optional title
                m = re.match(r'@(\w+)(?:\s+(.+))?', content)
                if m:
                    self.current_section_name = m.group(1)
                    self.current_section_title = m.group(2) if m.group(2) else None
                    self.current_section = {
                        'type': self.current_section_name,
                        'title': self.current_section_title,
                        'content': []
                    }
                continue

            # Inside a section
            if self.current_section is not None:
                # Key-value pair
                if ':' in content:
                    key, value = content.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    self.current_section['content'].append({'type': 'kv', 'key': key, 'value': value})
                # Numbered step
                elif re.match(r'\d+\.', content):
                    step = content.strip()
                    self.current_section['content'].append({'type': 'step', 'text': step})
                # List item
                else:
                    self.current_section['content'].append({'type': 'list', 'text': content.strip()})

        # Save last section
        if self.current_section:
            self.sections.append(self.current_section)

        return self._structure_sections(self.sections)

    def _structure_sections(self, sections):
        """
        Converts the flat list of sections and their content into a more structured dictionary.
        """
        result = defaultdict(list)
        for section in sections:
            sec_type = section['type']
            sec_title = section['title']
            content = section['content']
            parsed_content = self._parse_content(content)
            if sec_title:
                result[sec_type].append({'title': sec_title, **parsed_content})
            else:
                result[sec_type].append(parsed_content)
        return dict(result)

    def _parse_content(self, content):
        """
        Parses the content list into dicts/lists as appropriate.
        """
        result = {}
        steps = []
        items = []
        for item in content:
            if item['type'] == 'kv':
                # If value looks like a list, split it
                if ',' in item['value']:
                    values = [v.strip() for v in item['value'].split(',')]
                    result[item['key']] = values
                else:
                    result[item['key']] = item['value']
            elif item['type'] == 'step':
                steps.append(item['text'])
            elif item['type'] == 'list':
                items.append(item['text'])
        if steps:
            result['steps'] = steps
        if items:
            result['items'] = items
        return result

# Example usage:
if __name__ == "__main__":
    specscript = """
@meta
  Title: User Authentication Module
  Version: 1.0
  Author: Jane Doe
  Date: 2024-06-15

@entity User
  id: UUID, required, unique
  email: string, required, unique
  password_hash: string, required

@usecase RegisterUser
  Description: Allows a new user to create an account.
  Input: email (string), password (string)
  Output: user_id (UUID)
  Steps:
    1. Validate email format
    2. Check if email is unique
    3. Hash password
    4. Create user record
    5. Return user_id

@constraint
  Password must be at least 8 characters.
  Email must be unique.
"""

    parser = SpecScriptParser()
    parsed = parser.parse(specscript.splitlines())
    import pprint
    pprint.pprint(parsed)