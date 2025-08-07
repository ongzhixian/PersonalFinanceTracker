Analyze the following SQL Server stored procedure and generate a comprehensive, machine-readable explanation in JSON format.
The JSON should be well-formatted and suitable for automated documentation, code review, or impact analysis tools.
The output should include the following fields:
procedure_name: The name of the stored procedure.
schema: The schema to which the procedure belongs.
purpose: A concise summary of what the procedure does.
parameters: A list of input and output parameters, their data types, default values, directions (IN/OUT), and their purpose.
return_type: The return type, if any.
main_steps: An ordered list of the main logical steps performed.
tables_read: A list of tables/views the procedure reads from.
tables_written: A list of tables/views the procedure writes to, inserts into, updates, or deletes from.
temp_tables: Temporary tables or table variables created and used.
cursors: Any cursors declared and their purpose.
transactions: Transaction handling (BEGIN/COMMIT/ROLLBACK) and isolation levels.
error_handling: Error or exception handling logic (TRY/CATCH, RAISERROR, etc.).
stored_procs: A list of stored procedures called.
functions: Scalar or table-valued functions called.
triggers: Any triggers that may be invoked as a result of actions.
synonyms: Synonyms referenced.
dynamic_sql: Use of dynamic SQL (sp_executesql, EXEC, etc.).
business_rules: Key business rules, validations, or special logic.
security: Permission checks, EXECUTE AS, or security-related logic.
dependencies: Other database objects or external resources referenced.
comments: Notable comments or documentation within the procedure.
notes: Any additional important notes, caveats, or limitations.
