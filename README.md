# AI Resume Screening System

This project is a high-performance resume screening tool built during my internship. It leverages the **Endee Labs Vector Engine** as a local database service to store and search candidate resumes using semantic AI embeddings.

---

## 🏗 Project Architecture

The system is designed using a microservices-inspired approach, separating the database engine from the application logic.

- **`endee-09/`**: The core Vector Database (C++ engine) cloned from the official [Endee repository](https://github.com/EndeeLabs/endee). It handles high-speed vector storage and similarity searches locally on your machine.
- **`resume-screening-app/`**: The custom application layer. It handles PDF text extraction, AI embedding generation (NLP), and provides a REST API for the frontend.



---

# AI Resume Screening System

This project was developed as a **technical test project for the internship selection process at Endee Labs**. It demonstrates a high-performance resume screening tool that leverages the **Endee Labs Vector Engine** as a local database service to store and search candidate resumes using semantic AI embeddings.

---

## 🏗 Project Architecture

The system is designed using a microservices-inspired approach, separating the database engine from the application logic.

- **`endee-09/`**: The core Vector Database (C++ engine). Cloned from the official [Endee repository](https://github.com/EndeeLabs/endee).
- **`resume-screening-app/`**: The custom application layer. It handles PDF text extraction, AI embedding generation (NLP), and provides a REST API for the frontend.



---

## 🚀 Setup & Installation

### 1. Workspace Initialization
First, create your workspace directory and clone both the database engine and the application repository.

```bash
# Create and enter the workspace
mkdir EndeeLabs
cd EndeeLabs
```

### 2. Clone the Endee Vector Engine

Using HTTP:
```
git clone https://github.com/EndeeLabs/endee.git
```
Using SSH:
```
git clone git@github.com:EndeeLabs/endee.git
```
> **Note:** I have renamed my local copy of the official Endee repository to **"endee-09"**.

### 3. Clone the Application Repository

Using HTTP:
```
git clone https://github.com/EndeeLabs/endee.git
```
Using SSH:
```
git clone git@github.com:EndeeLabs/endee.git
```


### 4. Initializing the Endee Vector Database

 we build the Docker image from source.

**Navigate to the engine directory:**
```
cd endee-09
```

**Create docker image from docker file:**

```
docker build -t endee-oss:latest -f infra/Dockerfile --build-arg BUILD_ARCH=avx2 .
```
**Start the service:**

```
docker compose up -d
```





