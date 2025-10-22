# Create README.md file
# Library Attendance System

A Django-based library attendance tracking system with QR code scanning.

## Features
- ✅ Student check-in/check-out via QR codes
- 📊 Real-time dashboard with statistics
- 📋 Attendance reports and filtering
- 💾 Data export to CSV
- 👥 Role-based user management
- 🎫 QR code generation
- 🔐 User authentication

## Quick Start

1. **Clone the repository**
   \`\`\`bash
   git clone https://github.com/YOUR_USERNAME/LibrarySystem.git
   cd LibrarySystem
   \`\`\`

2. **Create virtual environment**
   \`\`\`bash
   python -m venv venv
   \`\`\`

3. **Activate virtual environment**
   - Windows: \`.\venv\Scripts\Activate.ps1\`
   - Mac/Linux: \`source venv/bin/activate\`

4. **Install dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

5. **Run migrations**
   \`\`\`bash
   python manage.py makemigrations
   python manage.py migrate
   \`\`\`

6. **Create superuser**
   \`\`\`bash
   python manage.py createsuperuser
   \`\`\`

7. **Run development server**
   \`\`\`bash
   python manage.py runserver
   \`\`\`

8. **Access the system**
   - Main app: http://127.0.0.1:8000/attendance/
   - Admin panel: http://127.0.0.1:8000/admin/

## Project Structure
\`\`\`
LibrarySystem/
├── attendance/          # Main app
├── library_app/         # Project settings
├── manage.py
├── requirements.txt
└── README.md
\`\`\`