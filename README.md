# VoxWave Project

## Overview

The VoxWave project is a web application built with the Django Python framework, designed to empower and connect sensory-impaired individuals, including the deaf, mute, and blind. Inspired by social media platforms like Instagram, VoxWave aims to create an inclusive community where disabled users can engage with technology on par with their non-disabled counterparts.

## Project Features

### Social Media Platform
- Users can upload image posts within the VoxWave community.
- User authentication ensures a secure and personalized experience.

### Assistive Features
1. **Speech-to-Text with Emotion Recognition**
   - Converts spoken words into written text.
   - Incorporates emotion recognition for nuanced communication.

2. **Text-to-Speech with Emotion Implementation**
   - Transforms written content into spoken words.
   - Integrates emotion to enhance expression in synthesized speech.

3. **PDF Summarizer**
   - Aids blind users by summarizing key information within PDF documents.

## Setup Instructions

Follow these steps to set up and run the VoxWave project:

Certainly! Let's go through the steps to create a folder, enter that folder, open the terminal, and then clone the VoxWave project:

1. **Create a Folder:**
   ```bash
   mkdir VoxWaveProject
   ```

2. **Enter the Folder:**
   ```bash
   cd VoxWaveProject
   ```

3. **Open the Terminal in the Folder:**
   - On Windows: You can open the Command Prompt or PowerShell.
   - On macOS/Linux: You can use the terminal.

4. **Fork the Repository:**
   - Visit the VoxWave repository on GitHub: [https://github.com/Vox-Wave/VoxWave.git](https://github.com/Vox-Wave/VoxWave.git)
   - Click on the "Fork" button in the top right corner of the GitHub page.
   - This will create a copy (fork) of the repository under your GitHub account. And then clone that forked repo onto your local system.

5. **Clone Your Forked Repository:**
   ```bash
   git clone https://github.com/your-username/VoxWave.git
   ```

   Replace `your-username` with your actual GitHub username.

6. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   ```

7. **Activate the Virtual Environment:**
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

8. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

9. **Apply Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

10. **Create a Superuser:**
   ```bash
   python manage.py createsuperuser
   ```

11. **Run the Development Server:**
   ```bash
   python manage.py runserver
   ```

12. **Access the Admin Panel:**
   - Open your web browser and go to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).
   - Log in with the superuser credentials created in step 10.

   **Access the VoxWave Platform:**
   - Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to explore the VoxWave community.

#IMPORTANT
##For installing ffmpeg in your system refer the youtube video [https://youtu.be/4jx2_j5Seew?si=GBu7MZukpUNjsGNY](https://youtu.be/4jx2_j5Seew?si=GBu7MZukpUNjsGNY)

Thank you for contributing to VoxWave, where technology meets inclusivity!
