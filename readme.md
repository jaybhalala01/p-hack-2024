# Vehicle Detection and Tracking Application

https://github.com/user-attachments/assets/b86faf34-7995-4aad-9632-2cc51beb8b04

## Overview

This repository contains a Flask-based web application for vehicle detection and tracking. The application uses object detection to identify vehicles and their number plates in uploaded videos. It tracks these objects frame-by-frame, maintaining a count of currently visible and total detected vehicles and number plates.

## Features

- **Model Information Display**: Shows details about the detection model used.
- **Vehicle Detection**: Detects vehicles and number plates in uploaded videos.
- **Object Tracking**: Tracks detected vehicles and number plates across frames. Stops tracking if an object is not detected for five consecutive frames.
- **Statistics**: Displays current and total counts of detected vehicles and number plates and additional images of number plates in the front-end.
- **Video Controls**: After uploading a video, use "Detect", "Play", and "Pause" buttons to control video processing and playback in the UI.

## Installation

### Prerequisites

Ensure you have [conda](https://docs.conda.io/en/latest/miniconda.html) installed.

### Step-by-Step Guide

1. **Clone the repository**

    ```sh
    git clone https://github.com/jaybhalala01/p-hack-2024.git
    cd p-hack-2024
    ```

2. **Create a new environment with conda**

    ```sh
    conda create --name vehicle-detection python=3.8
    ```

3. **Activate the environment**

    ```sh
    conda activate vehicle-detection
    ```

4. **Install the required packages**

    ```sh
    pip install -r requirements.txt
    ```

5. **Run the application**

    ```sh
    python3 app.py
    ```

## Usage

1. **Start the Flask application**

    Running the command `python3 app.py` will start the Flask application. Open your web browser and navigate to `http://localhost:5000` to access the web interface.

2. **Navigate through the website**

    - **Model Information Page**: The homepage displays information about the object detection model being used.
    - **Start Detection**: Click the "Start" button to proceed to the video upload page.
    - **Upload Video**: Upload a video file. The application will process the video to detect and track vehicles and their number plates. 

3. **Viewing Results**

    - **Inference**: After uploading the video, the application will run inference to detect vehicles and number plates.
    - **Tracking**: The application will track each detected object across frames, showing IDs and counts on the website.
    - **Video Controls**: Use the "Detect", "Play", and "Pause" buttons to control video processing and playback.
        - **Detect**: Starts the detection process on the uploaded video.
        - **Play**: Plays the processed video.
        - **Pause**: Pauses the video playback.
    - **Statistics**: Current and total counts of detected vehicles and number plates are displayed on the web page.

## Dataset Overview

- We collected and manually annotated 4,000 images for vehicle detection.
- Additionally, we used a public dataset containing 10,000 images of number plates.
- These datasets were combined to train a model capable of detecting both vehicles and number plates.
- The model was trained using the YOLO (You Only Look Once) architecture.
- For tracking, we developed a custom tracker based on the center point tracking algorithm.

## Collaboration

This project was developed as part of the Parul University Hackathon by a team of three members: Jay Bhalala, Prink Hapaliya, and Shashank Nakka.

## Note

The model file is not included in this repository due to its large size. Please contact the project maintainers for access to the model file or instructions on how to obtain it.

## Contact

For issues or questions, please open an issue in this repository.
