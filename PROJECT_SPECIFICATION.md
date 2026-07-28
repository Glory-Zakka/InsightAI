# InsightAI Project Specification

## 1. Executive Summary

**Project:** InsightAI\
**Tagline:** AI-Powered Business Intelligence & Decision Support
Platform

InsightAI is a modern NiceGUI-based business intelligence application
that combines Excel KPI extraction, analytics visualization, and an
AI-powered business assistant into one professional dashboard.

This MVP is intended for client demonstration within a short development
timeline and should emphasize an impressive user experience while
providing a scalable architecture for future enhancements.

------------------------------------------------------------------------

## 2. Business Problem

Current workflow: 1. Employees complete a complex Excel workbook each
month. 2. Excel formulas calculate KPIs. 3. A separate Python script
generates charts. 4. Analysis is performed manually.

Problems: - Multiple disconnected tools. - Manual workflow. - Difficult
for non-technical users. - No conversational insights.

------------------------------------------------------------------------

## 3. Product Vision

A single application where users can:

-   Upload Excel reports.
-   Automatically calculate KPIs.
-   Visualize business metrics.
-   Chat with AI about uploaded data.
-   Export reports.

------------------------------------------------------------------------

## 4. Technology Stack

-   Python 3.14
-   NiceGUI
-   Pandas
-   OpenPyXL
-   Plotly
-   Google Gemini API
-   python-dotenv

------------------------------------------------------------------------

## 5. Folder Structure

    InsightAI/
    ├── app.py
    ├── assets/
    ├── config/
    ├── core/
    ├── models/
    ├── services/
    ├── ui/
    │   ├── components/
    │   ├── layouts/
    │   ├── pages/
    │   └── theme/
    ├── utils/
    ├── uploads/
    ├── exports/
    ├── tests/
    ├── requirements.txt
    ├── README.md
    └── PROJECT_SPECIFICATION.md

------------------------------------------------------------------------

## 6. UI Design System

### Style

-   Premium SaaS appearance
-   Inspired by Power BI, Stripe, Linear, Notion

### Colors

  Item         Color
  ------------ ---------
  Primary      #2563EB
  Secondary    #1E40AF
  Sidebar      #111827
  Background   #F5F7FA
  Success      #10B981
  Warning      #F59E0B
  Danger       #EF4444

### Font

Inter

------------------------------------------------------------------------

## 7. Navigation

Sidebar:

-   Dashboard
-   Upload Report
-   Analytics
-   AI Assistant
-   Settings

Navbar:

-   Logo
-   Current Page
-   Search
-   Notifications
-   User Avatar

------------------------------------------------------------------------

## 8. Dashboard

Contains:

-   KPI Cards
-   Welcome Card
-   Sales Chart
-   Revenue Chart
-   AI Preview
-   Recent Uploads

------------------------------------------------------------------------

## 9. Upload Module

Features:

-   Drag-and-drop upload
-   XLS/XLSX validation
-   Upload progress
-   File preview

------------------------------------------------------------------------

## 10. Excel Processing

Pipeline:

Upload → Validation → Workbook Reader → KPI Extraction → Summary →
Charts → Dashboard

------------------------------------------------------------------------

## 11. KPI Engine

Responsibilities:

-   Read workbook values
-   Compute KPIs
-   Format results
-   Handle missing values

------------------------------------------------------------------------

## 12. Analytics

Uses Plotly.

Initial charts:

-   Revenue
-   Profit
-   Orders
-   Growth
-   Trend Analysis

------------------------------------------------------------------------

## 13. AI Assistant

Gemini-powered.

Capabilities:

-   Summarize uploaded report
-   Explain KPIs
-   Identify trends
-   Answer business questions
-   Suggest actions

------------------------------------------------------------------------

## 14. Export Module

Support:

-   PDF (future)
-   Excel
-   CSV
-   PNG charts

------------------------------------------------------------------------

## 15. Coding Standards

-   PEP8
-   Type hints
-   Docstrings
-   Reusable components
-   Modular architecture
-   Small functions
-   No duplicated UI code

------------------------------------------------------------------------

## 16. Development Roadmap

### Phase 1

Environment Setup ✅

### Phase 2

UI Framework - Theme - Layout - Sidebar - Navbar - Dashboard

### Phase 3

Upload Module

### Phase 4

Excel Reader

### Phase 5

KPI Engine

### Phase 6

Chart Engine

### Phase 7

Analytics Dashboard

### Phase 8

AI Assistant

### Phase 9

Export Features

### Phase 10

Testing & MVP Delivery

------------------------------------------------------------------------

## 17. Current Development Status

Completed:

-   Environment Setup
-   NiceGUI Integration
-   Theme
-   Main Layout
-   Sidebar
-   Navbar
-   Dashboard Skeleton

Current Focus:

Improve dashboard UI into a production-quality MVP.

------------------------------------------------------------------------

## 18. Rules for AI Coding Agents

Before making any code changes:

1.  Scan the workspace.
2.  Understand existing architecture.
3.  Reuse existing files.
4.  Do not rename folders.
5.  Do not rewrite working code without justification.
6.  Implement incrementally.
7.  Never leave broken imports.
8.  Ensure `python app.py` runs after every implementation.

When editing: - Prefer modifying existing components. - Maintain NiceGUI
architecture. - Preserve styling consistency. - Keep the project
demo-ready at all times.

------------------------------------------------------------------------

## 19. Definition of Done

The MVP is complete when:

-   Users upload Excel files.
-   KPIs display automatically.
-   Charts render correctly.
-   AI answers questions about uploaded data.
-   Reports can be exported.
-   UI appears polished and professional.
-   Application launches successfully using:

``` bash
python app.py
```
