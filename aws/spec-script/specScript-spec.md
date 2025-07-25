@meta
  Title: SpecScript Format Specification
  Version: 1.0
  Author: AI Assistant
  Date: 2024-06-15

@description
  SpecScript is a human-readable, machine-interpretable format for software specifications.
  It uses section markers, indentation, and key-value pairs to define structure and content.

@entity Section
  name: string, required, unique
  description: string, optional

@entity Field
  name: string, required
  type: string, required
  required: boolean, optional
  unique: boolean, optional
  description: string, optional

@usecase DefineSection
  Description: How to define a section in SpecScript.
  Input: section name (string), section content (lines)
  Output: section block
  Steps:
    1. Start with @ followed by section name (e.g., @entity, @usecase)
    2. Indent all lines belonging to the section
    3. Use key: value pairs for properties
    4. For lists, use indented lines or comma-separated values

@usecase DefineField
  Description: How to define a field within an entity or section.
  Input: field name (string), field type (string), optional attributes
  Output: field definition
  Steps:
    1. Write field name followed by colon and type
    2. Add attributes after type, separated by commas (e.g., required, unique)
    3. Optionally add description

@usecase DefineList
  Description: How to define a list of items.
  Input: list items (lines or comma-separated)
  Output: list block
  Steps:
    1. Indent each item under the list key
    2. Or, separate items by commas on a single line

@constraint
  Section names must start with @ and be followed by a word (letters only).
  Indentation must be consistent within a section.
  Key-value pairs must use colon and space (key: value).
  Field attributes are separated by commas.
  Steps in a usecase must be numbered.

@nonfunctional
  SpecScript files must be UTF-8 encoded.
  Parsers should ignore blank lines and comments (lines starting with #).

@testcase SectionParsing
  Input:
    @entity User
      id: UUID, required
      email: string, required, unique
  Expect: Section 'entity' with name 'User' and two fields parsed.

@testcase ListParsing
  Input:
    @constraint
      Password must be at least 8 characters.
      Email must be unique.
  Expect: Section 'constraint' with two list items parsed.

@testcase KeyValueParsing
  Input:
    @meta
      Title: Example
      Version: 1.0
  Expect: Section 'meta' with two key-value pairs parsed.


@meta: Metadata about the SpecScript specification itself.
@description: Overview of SpecScript.
@entity: Defines the main building blocks (Section, Field).
@usecase: Describes how to use the format (defining sections, fields, lists).
@constraint: Lists the rules for writing valid SpecScript.
@nonfunctional: Non-functional requirements for files and parsers.
@testcase: Example inputs and expected parsing results.
