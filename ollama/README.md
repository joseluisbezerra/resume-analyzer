## 🚀 How to Run This Project with GPU Support

This guide explains how to build and run the Docker image with GPU support for optimal performance.

---

### 📦 Step 1: Build the Docker Image

Make sure you're in the root directory (where the Dockerfile is located), then run:

```bash
docker build -t your-image-name .
```

### 📦 Step 2: Run the Docker Image

```bash
docker run -d -p 11434:11434 --gpus all -it --rm your-image-name
```



