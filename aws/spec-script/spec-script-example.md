@meta
  Title: User Authentication Module
  Version: 1.0
  Author: Jane Doe
  Date: 2024-06-15

@description
  This module provides user registration, login, and password reset functionality.

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

@usecase Login
  Description: Authenticates a user.
  Input: email (string), password (string)
  Output: token (string)
  Steps:
    1. Find user by email
    2. Verify password
    3. Generate authentication token
    4. Return token

@constraint
  Password must be at least 8 characters.
  Email must be unique.

@nonfunctional
  All responses within 500ms.
  Passwords must be stored using bcrypt.

@testcase RegisterValid
  Input: email="test@example.com", password="securePass123"
  Expect: user_id is UUID

@testcase RegisterDuplicate
  Input: email="test@example.com", password="anotherPass"
  Expect: error="Email already exists"