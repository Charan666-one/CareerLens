# Project Overview

CareerLens is a web application designed to help students and early-career professionals discover suitable tech jobs, understand their skill gaps, and receive a step-by-step learning roadmap.

It solves the problem of turning a resume and a career goal into a practical plan for growth. Instead of manually searching jobs and guessing what to learn next, the system aims to analyze a candidate profile, compare it to job requirements, and recommend the most relevant opportunities and learning steps.

The main users are:
- Students targeting their first tech role
- Recent graduates preparing for internships or entry-level jobs
- Job seekers who want a structured career growth path

The intended workflow is:
1. User registers and logs in
2. User uploads or provides a resume
3. Resume content is parsed and skills are extracted
4. Candidate profile is built from those skills
5. Recommendation engine compares the profile with job data
6. Missing skills are identified and a roadmap is generated
7. Results are shown in the dashboard and roadmap views

Current development stage:
- The project is in an early architectural and scaffolding stage
- The backend, frontend, database models, and service folders are in place
- Core business logic is still mostly placeholder code and needs implementation

------------------------------------------------

# Current Architecture

Frontend
- Built with React, TypeScript, Vite, and Tailwind CSS
- The UI currently contains placeholder pages for login, register, dashboard, jobs, and roadmap
- Routing is handled through React Router
- The frontend is expected to communicate with the FastAPI backend through axios

Backend
- Built with FastAPI
- The app is initialized in backend/app/main.py
- API routers are mounted for auth, users, jobs, recommendations, roadmap, and resume
- The current backend is mostly a structure scaffold with empty route handlers

Machine Learning
- The project intends to use NLP and graph-based methods
- Dependencies include spaCy, scikit-learn, networkx, numpy, and pandas
- The current implementation is not yet functional for parsing or recommendation scoring

Database
- SQLAlchemy ORM is used with PostgreSQL
- Models are defined for users, skills, jobs, candidate profiles, recommendations, and roadmaps
- Database initialization is connected through the app startup path

Recommendation Engine
- Planned as the core production module
- The service directory exists, but the engine is currently empty
- It is intended to combine semantic relevance, graph-based skill similarity, and market demand signals

Resume Parser
- Planned as an NLP-based module for extracting technical skills from resumes
- The parser module exists as a scaffold and imports spaCy
- The actual parsing logic is not implemented yet

Authentication
- Password hashing and JWT helpers are implemented in the security module
- The route layer for authentication exists but has no endpoint logic yet

Admin Module
- No dedicated admin module is present yet
- The current architecture does not include admin-specific routes or models

Dashboard
- The frontend dashboard page exists as a placeholder shell
- It is expected to display recommendations, profile summaries, and roadmaps once implemented

API Structure
- The API is organized around route modules under backend/app/api/routes
- The main app mounts those routers under /api/* prefixes
- Communication is intended to flow as: frontend -> API routes -> service modules -> database/models

------------------------------------------------

# Folder Structure

Root
- Purpose: project container and top-level orchestration
- Files inside: docker-compose.yml, README.md, LICENSE, backend/, frontend/, docs/, data/
- Responsibilities: local development orchestration, project documentation, environment setup
- Dependencies: Docker Compose, backend and frontend services

backend/
- Purpose: Python backend application
- Files inside: Dockerfile, requirements.txt, app/, tests/
- Responsibilities: API server, data access, service modules, business logic
- Dependencies: FastAPI, SQLAlchemy, PostgreSQL, spaCy, networkx, JWT auth libraries

backend/app/
- Purpose: main application package
- Files inside: main.py, api/, core/, db/, models/, schemas/, services/, utils/
- Responsibilities: application entry points, routing, configuration, persistence, services
- Dependencies: all backend modules

backend/app/api/
- Purpose: API layer
- Files inside: routes/auth.py, routes/jobs.py, routes/recommendations.py, routes/roadmap.py, routes/resume.py, routes/users.py
- Responsibilities: route definitions and request handling
- Dependencies: FastAPI, service modules, database session helpers

backend/app/core/
- Purpose: application configuration and security helpers
- Files inside: config.py, security.py
- Responsibilities: environment loading, JWT token generation, password hashing
- Dependencies: pydantic-settings, passlib, jose

backend/app/db/
- Purpose: database layer
- Files inside: database.py, models.py
- Responsibilities: engine/session creation and ORM model definitions
- Dependencies: SQLAlchemy, PostgreSQL driver

backend/app/services/
- Purpose: domain logic modules
- Files inside: graph/skill_graph.py, nlp/resume_parser.py, nlp/skill_normalizer.py, recommendation/engine.py, roadmap/generator.py
- Responsibilities: skill graph handling, NLP parsing, recommendation scoring, roadmap generation
- Dependencies: networkx, spaCy, scikit-learn, pandas, numpy

frontend/
- Purpose: React-based user interface
- Files inside: package.json, vite.config.ts, index.html, public/, src/
- Responsibilities: rendering pages, routing, API calls, UI state
- Dependencies: React Router, axios, Zustand, Tailwind, Recharts, D3

frontend/src/pages/
- Purpose: route-level screens
- Files inside: Dashboard.tsx, Jobs.tsx, Login.tsx, Register.tsx, Roadmap.tsx
- Responsibilities: page-level UI components
- Dependencies: shared services and UI components

frontend/src/services/
- Purpose: API client layer
- Files inside: api.ts
- Responsibilities: central axios configuration and authorization token injection
- Dependencies: axios

frontend/src/store/
- Purpose: global state management
- Files inside: auth.ts
- Responsibilities: authentication state management
- Dependencies: Zustand

frontend/src/types/
- Purpose: shared TypeScript data models
- Files inside: index.ts
- Responsibilities: shared type definitions for API payloads and UI data
- Dependencies: frontend type usage only

Data seed folder
- Purpose: initial knowledge base materials
- Files inside: skills.json and edges.json
- Responsibilities: seed data for skills and skill relationships
- Dependencies: graph module and recommendation logic

------------------------------------------------

# File Responsibilities

backend/app/main.py
- Purpose: API application entry point
- What it does: creates the FastAPI app, enables CORS, mounts routers, and exposes the root endpoint
- Functions inside: root()
- Classes inside: none
- Dependencies: FastAPI, route modules, database models
- Who calls it: Uvicorn when the backend server starts
- What calls it: none directly from the app code
- Status: complete as a bootstrap file, but incomplete in business logic

backend/app/core/config.py
- Purpose: environment configuration loader
- What it does: reads database URL, secret key, and token settings from environment variables
- Functions inside: none beyond settings instantiation
- Classes inside: Settings
- Dependencies: pydantic-settings
- Who calls it: database layer, security module
- What calls it: settings object used throughout the backend
- Status: complete for configuration loading

backend/app/core/security.py
- Purpose: password hashing and JWT helpers
- What it does: hashes passwords, verifies them, and creates access tokens
- Functions inside: hash_password(), verify_password(), create_access_token()
- Classes inside: none
- Dependencies: passlib, jose
- Who calls it: authentication routes when implemented
- What calls it: currently no route implementation calls it
- Status: implemented but not yet wired into endpoints

backend/app/db/database.py
- Purpose: database session and engine setup
- What it does: creates SQLAlchemy engine, session factory, base class, and DB dependency helper
- Functions inside: get_db()
- Classes inside: none
- Dependencies: SQLAlchemy, settings
- Who calls it: future route handlers and service modules
- What calls it: currently no route implementation uses it
- Status: complete as infrastructure

backend/app/db/models.py
- Purpose: persistence model definitions
- What it does: defines tables for skills, skill edges, jobs, users, candidate profiles, recommendations, and roadmaps
- Functions inside: none
- Classes inside: Skill, SkillEdge, Job, User, CandidateProfile, Recommendation, Roadmap
- Dependencies: SQLAlchemy ORM, UUID support, PostgreSQL dialect
- Who calls it: database initialization and future API logic
- What calls it: backend/app/main.py during startup
- Status: implemented and central to the current architecture

backend/app/services/graph/skill_graph.py
- Purpose: skill graph handling
- What it does: imports networkx and is intended to represent prerequisite relationships between skills
- Functions inside: none yet
- Classes inside: none yet
- Dependencies: networkx
- Who calls it: future recommendation and roadmap modules
- What calls it: currently none
- Status: scaffolded only

backend/app/services/nlp/resume_parser.py
- Purpose: resume parsing and skill extraction
- What it does: imports spaCy and is intended to parse resume text into structured candidate skills
- Functions inside: none yet
- Classes inside: none yet
- Dependencies: spaCy
- Who calls it: resume routes and recommendation pipeline
- What calls it: currently none
- Status: scaffolded only

backend/app/services/nlp/skill_normalizer.py
- Purpose: normalize extracted skill names into canonical forms
- What it does: file exists but currently empty
- Functions inside: none yet
- Classes inside: none yet
- Dependencies: none yet
- Who calls it: future parser and recommendation logic
- What calls it: currently none
- Status: not implemented

backend/app/services/recommendation/engine.py
- Purpose: recommendation scoring logic
- What it does: intended to combine semantic similarity, graph proximity, and demand signals
- Functions inside: none yet
- Classes inside: none yet
- Dependencies: planned ML and graph libraries
- Who calls it: recommendations route module
- What calls it: currently none
- Status: not implemented

backend/app/services/roadmap/generator.py
- Purpose: roadmap generation logic
- What it does: intended to produce a sequence of learning steps based on missing skills
- Functions inside: none yet
- Classes inside: none yet
- Dependencies: planned logic and graph traversal
- Who calls it: roadmap route module
- What calls it: currently none
- Status: not implemented

frontend/src/App.tsx
- Purpose: application routing entry point
- What it does: defines routes for login, register, dashboard, jobs, and roadmap
- Functions inside: App()
- Classes inside: none
- Dependencies: react-router-dom, page components
- Who calls it: main.tsx
- What calls it: browser router bootstrap
- Status: implemented as navigation shell

frontend/src/services/api.ts
- Purpose: API client middleware
- What it does: creates an axios instance and adds bearer tokens to requests
- Functions inside: none beyond module initialization
- Classes inside: none
- Dependencies: axios
- Who calls it: future frontend pages and hooks
- What calls it: currently none directly from implemented pages
- Status: implemented but not yet fully used by UI features

------------------------------------------------

# Development Progress

✔ Project structure and folders created
✔ Docker Compose setup added
✔ FastAPI backend bootstrapping completed
✔ SQLAlchemy database models defined
✔ JWT and password hashing helpers implemented
✔ React frontend shell and routes created
✔ Basic API client configured
✔ Seed data folders prepared

⬜ Authentication endpoints implemented
⬜ Resume upload and parsing flow implemented
⬜ Recommendation scoring implemented
⬜ Roadmap generation implemented
⬜ Frontend forms and API integration completed
⬜ Database migrations and seed loading added
⬜ Tests for core logic written

------------------------------------------------

# Current Workflow

The current workflow is intended to be:

User registers
↓
User logs in
↓
User uploads resume
↓
Resume is stored or processed
↓
Resume parser extracts technical skills
↓
Candidate profile is generated
↓
Recommendation engine compares profile against jobs
↓
Matching jobs are scored and explained
↓
Missing skills are identified
↓
Roadmap generator creates a learning sequence
↓
Results are displayed in the dashboard and roadmap pages

At the moment, the flow is only partially wired. The app has the right structure and expected modules, but the actual processing steps are not yet implemented.

------------------------------------------------

# What Has Been Built

Exactly what is working:
- The repository is organized into backend, frontend, docs, and data folders
- Docker Compose can start the core services structure
- FastAPI app boots with the expected routers
- SQLAlchemy models exist for the main domain entities
- Security helpers for hashing and JWT creation exist
- React pages and routes exist as placeholders
- Axios client is configured for API calls

Exactly what is implemented:
- Project skeleton and architectural separation
- Database schema definitions
- Authentication utility layer
- Frontend routing shell
- Service directories for NLP, graph, recommendation, and roadmap logic

Exactly what is partially implemented:
- Route modules exist but contain no endpoint logic yet
- NLP and recommendation services are imported but empty
- The frontend pages are present but do not yet connect to real data
- No working end-to-end user journey is available yet

Exactly what is still missing:
- Real authentication endpoints
- Resume upload flow and actual parsing
- Job recommendation scoring
- Roadmap generation logic
- Seed data loading into the database
- Connected frontend forms and dashboards
- Test coverage for the main business flow

------------------------------------------------

# Responsibilities of Every Module

Frontend modules
- Purpose: present the product to users and collect inputs
- Inputs: user actions, form submissions, token storage
- Outputs: API requests, rendered pages, visual summaries
- Dependencies: React, Router, axios, Zustand
- Internal logic: page rendering and state management
- Interaction: sends requests to backend routes and displays responses

Backend API routes
- Purpose: expose HTTP endpoints to the frontend
- Inputs: HTTP requests and payloads
- Outputs: JSON responses and status codes
- Dependencies: FastAPI, service modules, database sessions
- Internal logic: request parsing, validation, and orchestration
- Interaction: calls service functions and returns results

Service modules
- Purpose: contain the domain logic for parsing, recommendation, and roadmap generation
- Inputs: parsed resume data, job data, skill graph information
- Outputs: candidate profile data, ranked jobs, roadmap steps
- Dependencies: NLP and graph libraries
- Internal logic: transformation and scoring logic
- Interaction: invoked by route handlers and shared across features

Database layer
- Purpose: store and retrieve persistent data
- Inputs: ORM objects and query operations
- Outputs: rows and records from PostgreSQL
- Dependencies: SQLAlchemy and PostgreSQL
- Internal logic: schema and relationship management
- Interaction: used by routes and services through sessions

------------------------------------------------

# Machine Learning Status

Current algorithm
- No production recommendation algorithm is implemented yet
- The project is prepared for a hybrid approach involving NLP and graph methods

Dataset used
- The repository contains seed folders intended to hold skills and relationship data
- No live or imported training dataset is yet wired into the application flow

Features extracted
- The intended feature set includes skills, job requirements, experience, market demand, and prerequisite relationships
- Resume parsing is not yet implemented to generate these features

Vectorization
- The stack includes scikit-learn and pandas, suggesting a future TF-IDF or similar vectorization approach
- This is not yet active in the codebase

Similarity calculation
- The planned approach is to compute similarity between candidate profiles and job requirements
- The implementation is not present yet

Recommendation logic
- Intended to combine:
  - semantic similarity
  - graph proximity across skills
  - demand weighting based on skill popularity
- No scoring logic is currently available

Current limitations
- No actual resume parsing
- No trained or configured model
- No recommendation pipeline wired to real data

Future improvements
- Add resume parser with skill extraction
- Use TF-IDF or embeddings for semantic matching
- Add graph traversal for prerequisite and adjacent skill reasoning
- Introduce explainability for why a job was recommended

------------------------------------------------

# Database Status

Tables
- skills
- skill_edges
- jobs
- users
- candidate_profiles
- recommendations
- roadmaps

Relationships
- User has many candidate profiles
- CandidateProfile belongs to one user
- Recommendation links a user and a job
- Roadmap links a user to its generated learning output
- SkillEdge links skills in a directed relationship graph

Keys
- UUID primary keys are used for most entities
- Foreign keys connect users, jobs, and skills where relevant

Current data flow
- The models are defined and the app initializes them on startup
- Actual CRUD operations and seed loading are not implemented yet

Unused tables
- No evidence of tables for uploaded resume files, admin users, or feedback tracking yet

Missing tables
- A table for storing uploaded resume content or file metadata is not yet defined
- A table for learning resources or course recommendations is not yet present

------------------------------------------------

# API Documentation

Root endpoint
- Endpoint: /
- Method: GET
- Input: none
- Output: simple health status JSON
- Purpose: verify API availability
- Status: implemented

Authentication routes
- Endpoint: /api/auth/*
- Method: planned
- Input: registration and login payloads
- Output: tokens and user metadata
- Purpose: user identity and session creation
- Status: route mounted, logic not implemented

User routes
- Endpoint: /api/users/*
- Method: planned
- Input: user profile operations
- Output: user-related responses
- Purpose: profile management
- Status: route mounted, logic not implemented

Jobs routes
- Endpoint: /api/jobs/*
- Method: planned
- Input: job queries or filters
- Output: job list or job details
- Purpose: browse and retrieve job opportunities
- Status: route mounted, logic not implemented

Recommendations routes
- Endpoint: /api/recommendations/*
- Method: planned
- Input: candidate profile and target role
- Output: scored job recommendations
- Purpose: generate personalized recommendations
- Status: route mounted, logic not implemented

Roadmap routes
- Endpoint: /api/roadmap/*
- Method: planned
- Input: user profile and target role
- Output: learning roadmap steps
- Purpose: generate skill progression plan
- Status: route mounted, logic not implemented

Resume routes
- Endpoint: /api/resume/*
- Method: planned
- Input: uploaded resume file or text
- Output: parsed profile or skill summary
- Purpose: process resumes
- Status: route mounted, logic not implemented

------------------------------------------------

# Code Understanding

What new code was added
- Added this documentation file, README_AI.md, as the project's living memory

Why it was added
- To preserve architectural knowledge, implementation status, and development direction in one place
- To ensure future changes remain aligned with the actual repository state

Which files changed
- README_AI.md was created

What functionality changed
- No application behavior changed; the repository documentation was updated

Whether anything broke
- No runtime or build behavior was changed

Any technical debt introduced
- No new code debt was introduced; the existing project still has placeholder modules that need implementation

------------------------------------------------

# Next Development Tasks

1. Implement authentication endpoints
- Why: users need a working sign-in and sign-up flow
- Estimated difficulty: medium
- Dependencies: security helpers and database models
- Expected output: functional register/login API

2. Implement resume upload and parsing
- Why: the core product depends on converting resume text into structured skills
- Estimated difficulty: high
- Dependencies: NLP module, database model for profiles
- Expected output: parsed candidate profile from resume input

3. Build recommendation engine
- Why: the main value proposition is personalized job matching
- Estimated difficulty: high
- Dependencies: job data, skill graph, scoring logic
- Expected output: ranked job recommendations with explanations

4. Implement roadmap generator
- Why: users need actionable next steps after receiving recommendations
- Estimated difficulty: medium-high
- Dependencies: skill graph, missing skill analysis
- Expected output: ordered learning roadmap

5. Connect frontend pages to the real API
- Why: the current UI is only a shell
- Estimated difficulty: medium
- Dependencies: backend endpoints and auth flow
- Expected output: working pages for login, dashboard, jobs, and roadmap

6. Add database migrations and seed data
- Why: the app needs reproducible data initialization
- Estimated difficulty: medium
- Dependencies: database setup and seed files
- Expected output: migration scripts and initial skill data loading

7. Add automated tests
- Why: the core modules need reliability as development progresses
- Estimated difficulty: medium
- Dependencies: test framework and implemented logic
- Expected output: regression tests for graph and API behavior

------------------------------------------------

# Known Bugs

- No working authentication flow yet because the auth routes are empty
  - Possible cause: route handlers were not implemented yet
  - Files involved: backend/app/api/routes/auth.py, backend/app/core/security.py
  - Priority: high

- The frontend pages are placeholders and do not interact with backend data
  - Possible cause: pages were scaffolded without API integration
  - Files involved: frontend/src/pages/*.tsx
  - Priority: high

- Resume parsing and recommendation modules are not functional
  - Possible cause: service files exist but contain no logic
  - Files involved: backend/app/services/nlp/resume_parser.py, backend/app/services/recommendation/engine.py
  - Priority: high

- The backend may fail or behave unexpectedly without required environment variables
  - Possible cause: settings depend on .env values such as DATABASE_URL and SECRET_KEY
  - Files involved: backend/app/core/config.py
  - Priority: medium

------------------------------------------------

# Technical Decisions

Decision: Use FastAPI for the backend
- Reason: it is lightweight, modern, and well suited for API-first applications
- Alternatives: Flask, Django
- Pros: simple routing, async support, easy integration with Python ML libraries
- Cons: less built-in admin structure than Django

Decision: Use SQLAlchemy ORM with PostgreSQL
- Reason: the app needs a scalable and structured persistence layer
- Alternatives: raw SQL or NoSQL document storage
- Pros: clean Python model definitions and maintainable schema handling
- Cons: requires proper migration management

Decision: Use React with TypeScript for the frontend
- Reason: typed components make the UI easier to maintain and evolve
- Alternatives: plain JavaScript or a server-rendered framework
- Pros: strong developer experience and clear component boundaries
- Cons: slightly higher initial setup complexity

Decision: Use NetworkX and NLP libraries for the core intelligence layer
- Reason: the product concept depends on graph reasoning and skill extraction
- Alternatives: pure rule-based matching only
- Pros: easier to model skill dependencies and explainability
- Cons: requires more domain logic to make the results useful

------------------------------------------------

# Learning Notes

What is FastAPI?
- FastAPI is a Python web framework for building APIs quickly
- We used it because it is simple to set up and works well with modern Python services
- It works by defining route functions and returning JSON responses

What is SQLAlchemy?
- SQLAlchemy is an ORM that lets Python code work with relational databases using models
- We used it to define the app's persistence layer in a structured way
- It helps keep database logic readable and centralized

What is JWT?
- JWT is a token format used to represent authenticated user sessions
- We used it to prepare secure authentication for the app
- The server creates a signed token after login and validates it on future requests

What is a skill graph?
- A skill graph is a network of related skills and prerequisites
- We used this concept because career growth is often path-based and dependency-driven
- In the future, the graph can help explain which skills are missing and what should be learned next

What is NLP?
- NLP stands for Natural Language Processing
- We used it as the direction for resume parsing and skill extraction
- It helps convert human-written text into structured information the app can use

------------------------------------------------

# Session Summary

Date: 2026-07-11
- Files modified: README_AI.md
- Features completed: living project documentation created and aligned with the current codebase
- Bugs fixed: none; documentation now reflects the current scaffolded implementation state
- Current project status: early-stage architecture is present, but core business logic remains to be implemented
- Next recommended task: implement authentication endpoints and the first working resume upload flow
