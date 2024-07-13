# README

Welcome to Ripple project! This document will guide you through understanding the project structure, how to run it locally, and how to use Docker for containerized execution.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Running the Project Locally](#running-the-project-locally)
- [Running the Project with Docker](#running-the-project-with-docker)
- [Configuration Files](#configuration-files)
- [Changing MongoDB Settings](#changing-mongodb-settings)

---

## Project Structure

The project has the following structure:

.
├── .env
├── .gitignore
├── .pre-commit-config.yaml
├── docker-compose.yml
├── file_structure.sh
├── logging.ini
├── mypy.ini
└── src
├── app
│ ├── main.py
│ └── ... (other source files)
└── ... (other directories)



- **.env**: Environment variables configuration.
- **.gitignore**: Specifies files to be ignored by Git.
- **.pre-commit-config.yaml**: Configuration for pre-commit hooks.
- **docker-compose.yml**: Docker Compose configuration for the project.
- **file_structure.sh**: Shell script related to file structure (if applicable).
- **logging.ini**: Configuration for logging.
- **mypy.ini**: Configuration for mypy static type checker.
- **src**: Contains the source code of the project.

---

## Prerequisites

Ensure you have the following installed:

- Python 3.8+
- Poetry
- Docker and Docker Compose
- Uvicorn (if running locally)

---

## Running the Project Locally

To run the project locally, follow these steps:

1. **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Navigate to the `src` Directory**:
    ```bash
    cd src
    ```

3. **Install Dependencies**:
    Use Poetry to install the necessary Python packages:
    ```bash
    poetry install
    ```

4. **Run the Application**:
    Start the application using Uvicorn:
    ```bash
    poetry run uvicorn app.main:app --reload
    ```

    The application will be available at `http://127.0.0.1:8000`.

---

## Running the Project with Docker

To run the project using Docker, follow these steps:

1. **Build and Start the Containers**:
    Navigate to the project root directory and run:
    ```bash
    docker-compose up --build
    ```

    This command will build the Docker image and start the containers as defined in the `docker-compose.yml` file.

2. **Access the Application**:
    The application will be available at `http://localhost:8000`.

---

## Configuration Files

### .env
This file contains environment-specific variables that are used by the application. Ensure to set the required variables before running the project.

### logging.ini
This file configures the logging settings for the application. Adjust the logging levels and handlers as needed.

### mypy.ini
This file contains configurations for mypy, a static type checker for Python. Modify it to fit the project's type checking requirements.

### .pre-commit-config.yaml
This file is used to configure pre-commit hooks to ensure code quality. It includes configurations for linting, formatting, and other checks.

---

## Changing MongoDB Settings

### Locally

To change the MongoDB settings when running the project locally:

1. **Install MongoDB**:
    Ensure MongoDB is installed on your local machine. Follow the instructions for your operating system from the [MongoDB installation guide](https://docs.mongodb.com/manual/installation/).

2. **Configure MongoDB**:
    Edit the `.env` file in the project root directory to set the appropriate MongoDB connection settings. For example:
    ```ini
    MONGODB_URI="mongodb://localhost:27017"
    MONGODB_DB_NAME="your_db_name"
    ```

3. **Start MongoDB**:
    Start the MongoDB service on your local machine. For example:
    ```bash
    mongod --config /usr/local/etc/mongod.conf
    ```

4. **Run the Application**:
    Start the application using Poetry and Uvicorn as described above. The application will connect to the MongoDB instance based on the settings in the `.env` file.

### With Docker

To change the MongoDB settings when running the project with Docker:

1. **Edit `docker-compose.yml`**:
    Ensure the `docker-compose.yml` file has the MongoDB service defined. For example:
    ```yaml
    version: '3.8'
    services:
      app:
        build: .
        ports:
          - "8000:8000"
        env_file:
          - .env
        depends_on:
          - mongo
      mongo:
        image: mongo:latest
        ports:
          - "27017:27017"
        environment:
          - MONGO_INITDB_DATABASE=your_db_name
    ```

2. **Configure Environment Variables**:
    Edit the `.env` file to match the Docker Compose configuration. For example:
    ```ini
    MONGODB_URI="mongodb://mongo:27017"
    MONGODB_DB_NAME="your_db_name"
    ```

3. **Start the Containers**:
    Run Docker Compose to build and start the containers:
    ```bash
    docker-compose up --build
    ```

4. **Access the Application**:
    The application will connect to the MongoDB instance running in the Docker container based on the settings in the `.env` file.

---

## Conclusion

This README provides a comprehensive overview of the project setup, execution, and configuration. For any further details or issues, refer to the specific files and their documentation within the project.
or contact - [@NwoluDavid](https://www.github.com/NwoluDavid)


Happy Coding!
