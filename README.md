# **Salon Chemistry Booking System (CSC425 Assignment)**

This is a booking system for **Salon Chemistry**, a hair salon run by my uncle. The focus of this assignment was to create a **portable** web application using **Docker** and **Terraform**. While the current version is functional, it needs further polishing to refine the user experience and address security vulnerabilities before being published to production.

## **Overview**

This web application allows users to book hair salon appointments, with available time slots displayed dynamically. It consists of:

- **Frontend**: Built with **Flask**, handling client-side logic for displaying available time slots and submitting booking requests.
- **Backend**: Built with **Flask**, managing business logic for bookings, connecting to a PostgreSQL database, and enforcing rate limiting.

## **Running the Program**

To clone and run the project, follow these steps:

```bash
git clone https://github.com/schwarztim/CSC425.git
cd CSC425
terraform init
terraform apply
```

This will set up the infrastructure, including the PostgreSQL database, backend API, and frontend interface.

## **Application Structure**

### **Backend (`backend/app.py`)**

- **Database**: PostgreSQL is used to store appointment details in a `bookings` table.
- **APIs**: The backend exposes endpoints for booking management, such as `/available-slots` to retrieve open slots, and `/book` to create bookings.
- **CORS and Logging**: CORS is enabled to allow cross-origin requests, and detailed logging is in place for debugging purposes.
- **Rate Limiting**: The backend uses basic rate limiting to prevent endpoint abuse.
- **Database Connection Pooling**: Connection pooling improves performance when interacting with the PostgreSQL database.

### **Frontend (`frontend/app.py`)**

- **User Interface**: The frontend displays available time slots and allows users to submit booking requests.
- **Dynamic Slot Management**: JavaScript dynamically fetches and displays available time slots based on the selected date.
- **Rate Limiting**: The frontend respects rate limits to prevent overloading the backend with requests.
- **JavaScript Improvements**: `static/js/main.js` needs an update to dynamically inherit the backend URL rather than being hardcoded to `127.0.0.1`.

### **Database (`database/init.sql`)**

The PostgreSQL database stores appointments in the `bookings` table:

```sql
CREATE TABLE bookings (
  id SERIAL PRIMARY KEY,
  time_slot TIMESTAMP UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  phone_number VARCHAR(20) NOT NULL
);
```

### **High-Level Flow**

1. **User Interaction**: The user selects a date and views available time slots.
2. **Slot Availability**: Slots are fetched from the backend through the `/available-slots` endpoint.
3. **Booking**: The user submits their booking with the selected time, name, and phone number, which is sent to the backend for processing.
4. **Database Storage**: The backend checks for availability and saves the booking in the PostgreSQL database.
5. **Feedback**: The user receives feedback on whether the booking was successful or if the time slot was already taken.

## **Key Technologies Used**

- **Flask** (Backend and Frontend)
- **PostgreSQL** (Database for appointments)
- **Docker** (For containerizing the application)
- **Terraform** (For infrastructure provisioning and orchestration)
- **JavaScript** (For dynamic frontend functionality)

## **Areas for Improvement**

- **Security Fixes**: Address known vulnerabilities related to Flask, CORS, and request handling.
- **Admin Interface**: Enhance the application with an admin interface for staff to manually manage bookings.
- **UI/UX Enhancements**: Improve frontend styling and usability for a more polished user experience.
- **JavaScript Origin Issue**: Update the JavaScript in `frontend/static/js/main.js` to dynamically inherit the origin, making it more flexible in various environments.

## **Deployment Notes**

This application is designed to be **portable** and runs entirely in Docker containers, with Terraform managing the orchestration. Running `terraform init` and `terraform apply` sets up all necessary dependencies, including PostgreSQL, Flask, and the network configuration.
