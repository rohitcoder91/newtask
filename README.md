# Expense Sharing Application

## Table of Contents
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [API Endpoints](#api-endpoints)

## Getting Started

### Prerequisites

Make sure you have the following software installed on your machine:

- Python (3.6 or higher)
- Django
- Celery
- RabbitMQ or Redis (as the message broker for Celery)

### Installation

1. Clone the repository:

   ```bash
   https://github.com/rohitcoder91/newtask.git)https://github.com/rohitcoder91/newtask.git

2. cd expense-sharing-app
3. pip install -r requirements.txt
4. apply migration
  python manage.py migrate
5. run devlopement server -  python manage.py runserver

### Usage
### API Endpoints
The application provides the following API endpoints:

Add Expense

Endpoint: /api/add_expense/
Method: POST
Data:
json
Copy code
{
  "payer_id": 1,
  "amount": 1000,
  "split_type": "EQUAL",
  "participants_ids": [2, 3, 4]
}
Show Balances

Endpoint: /api/show_balances/
Method: GET
Data:
json
Copy code
{
  "user_id": 1
}




