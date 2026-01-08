# Data Model: Phase II - Todo Full-Stack Web Application

This document outlines the data structures for the main entities in the application.

## User

Represents a registered user of the application.

| Field         | Type         | Description                               | Constraints      |
|---------------|--------------|-------------------------------------------|------------------|
| `id`          | `UUID`       | Unique identifier for the user (Primary Key) | Not Null, Unique |
| `email`       | `String`     | User's email address                      | Not Null, Unique |
| `password_hash`| `String`     | Hashed password for the user              | Not Null         |
| `created_at`  | `DateTime`   | Timestamp when the user was created       | Not Null         |
| `updated_at`  | `DateTime`   | Timestamp when the user was last updated  | Not Null         |

## Task

Represents a single todo item belonging to a user.

| Field         | Type         | Description                               | Constraints      |
|---------------|--------------|-------------------------------------------|------------------|
| `id`          | `UUID`       | Unique identifier for the task (Primary Key)| Not Null, Unique |
| `user_id`     | `UUID`       | Foreign key referencing the `User` table  | Not Null         |
| `title`       | `String`     | The title of the task                     | Not Null         |
| `description` | `String`     | A more detailed description of the task   | Nullable         |
| `status`      | `String`     | The current status of the task (`pending`, `completed`) | Not Null         |
| `priority`    | `String`     | The priority of the task (`low`, `medium`, `high`)      | Nullable         |
| `due_date`    | `Date`       | The date the task is due                  | Nullable         |
| `created_at`  | `DateTime`   | Timestamp when the task was created       | Not Null         |
| `updated_at`  | `DateTime`   | Timestamp when the task was last updated  | Not Null         |

## Relationships

- A **User** can have **many** Tasks.
- A **Task** belongs to **one** User.
