# System Architecture Document

This document is based on the "Activity Registration System PRD" and aims to plan the technical architecture, data model, and core API design of the system.

## 1. Architecture Overview
The system will adopt a Client-Server Architecture to ensure scalability and future maintainability.
* Frontend: Responsible for UI/UX display and user interaction (Single Page Application).
* Backend: Handles all business logic (e.g., event management, registration verification, concurrency protection) and provides RESTful APIs.
* Database: Responsible for storing user data, event information, and registration records.

## 2. Technology Stack Recommendations
For this type of campus project, the following modern and fast-to-develop technologies are recommended:
* Frontend: React.js with Tailwind CSS for a modern, responsive interface.
* Backend: Node.js with Express.js or Python FastAPI.
* Database: PostgreSQL or MySQL (Relational databases are ideal for handling transactional registration processes and preventing overbooking).

## 3. Core Modules
1. User Module: Handles student and admin authentication and Role-Based Access Control (RBAC).
2. Event Module: Handles CRUD operations for events.
3. Registration Module: Responsible for registration logic validation, atomic capacity reduction, and status updates.

## 4. Database Schema (ER Diagram)

```mermaid
erDiagram
    USERS ||--o{ REGISTRATIONS : "makes"
        USERS {
                int id PK
                        string name
                                string email
                                        string role "student, admin"
                                            }

                                                    EVENTS ||--o{ REGISTRATIONS : "has"
                                                        EVENTS {
                                                                int id PK
                                                                        string title
                                                                                string description
                                                                                        datetime event_time
                                                                                                string location
                                                                                                        int max_capacity
                                                                                                                int current_capacity
                                                                                                                        int created_by FK
                                                                                                                            }
                                                                                                                                
                                                                                                                                    REGISTRATIONS {
                                                                                                                                            int id PK
                                                                                                                                                    int user_id FK
                                                                                                                                                            int event_id FK
                                                                                                                                                                    datetime registered_at
                                                                                                                                                                            string status "active, cancelled"
                                                                                                                                                                                }
                                                                                                                                                                                ```
                                                                                                                                                                                
                                                                                                                                                                                ## 5. Core API Endpoints Design
                                                                                                                                                                                
                                                                                                                                                                                ### Authentication
                                                                                                                                                                                * POST /api/auth/login - User login and Token issuance (e.g., JWT).
                                                                                                                                                                                
                                                                                                                                                                                ### Events
                                                                                                                                                                                * GET /api/events - Get public event list.
                                                                                                                                                                                * GET /api/events/:id - Get single event details and current capacity.
                                                                                                                                                                                * POST /api/events - [Admin] Create new event.
                                                                                                                                                                                * PUT /api/events/:id - [Admin] Edit existing event.
                                                                                                                                                                                * DELETE /api/events/:id - [Admin] Delete or cancel event.
                                                                                                                                                                                
                                                                                                                                                                                ### Registrations
                                                                                                                                                                                * POST /api/events/:id/register - [Student] Register for an event.
                                                                                                                                                                                * DELETE /api/events/:id/register - [Student] Cancel registration.
                                                                                                                                                                                * GET /api/events/:id/attendees - [Admin] Get the list of registered students.
                                                                                                                                                                                
                                                                                                                                                                                ## 6. Key Technical Challenge: Concurrency Control
                                                                                                                                                                                To prevent overbooking during high-demand registrations, the backend must implement transaction protection:
                                                                                                                                                                                1. Open database transaction.
                                                                                                                                                                                2. Use SELECT ... FOR UPDATE or Optimistic Locking to read capacities.
                                                                                                                                                                                3. Check current_capacity < max_capacity.
                                                                                                                                                                                4. If capacity is available, add registration record and increment current_capacity.
                                                                                                                                                                                5. Commit transaction.
                                                                                                                                                                                
                                                                                                                                                                                > [!IMPORTANT]
                                                                                                                                                                                > This mechanism is the core of the registration system, ensuring data correctness and consistency under high concurrency.
                                                                                                                                                                                
