# PiCar Vehicle Rental System - AI Agent Instructions

## Architecture Overview
- **Backend**: Flask REST API (`Backend/Picar/`) with Supabase database integration
- **Frontend**: Flet-based mobile UI (`Frontend/`) mimicking native app experience
- **Data Flow**: Frontend → API Routes → Services → Models → Supabase database
- **Key Features**: User registration with OCR driving license detection, vehicle booking system, OTP authentication

## Core Components
- **Models** (`Backend/Picar/Model/`): Data classes with property validation (e.g., `User.py` with password strength checks)
- **Services** (`Backend/Picar/Services/`): Business logic (e.g., `AuthService.py` handles OTP via email/SMS)
- **Routes** (`Backend/Picar/Routes.py`): API endpoints mapping requests to service functions
- **Utils** (`Backend/Picar/Utils/`): OCR processing (`DrivingLicenseDetect.py`) and image handling
- **Frontend Screens** (`Frontend/Screens/`): Flet views with custom styling from `Style.py`

## Project Conventions
- **Language**: Vietnamese comments and variable names throughout codebase
- **Database**: Supabase client in `ExcuteDatabase.py` - use `supabase.table().select/insert/update()` patterns
- **Async**: Use `async/await` for email/SMS operations in services
- **Validation**: Model properties with setters enforcing rules (e.g., password: 6-20 chars, uppercase + digit)
- **ID Generation**: Custom IDs via `GenerateID.py` (e.g., "US" prefix for users)
- **Image Storage**: Upload to Supabase storage buckets, get public URLs

## Developer Workflows
- **Run Backend**: `python Run.py` (Flask on port 5000, debug mode)
- **Run Frontend**: `python Frontend/Main.py` (Flet app, window size 393x853)
- **Dependencies**: Install from `requirements.txt` (includes Flask, Flet, EasyOCR, OpenCV)
- **OCR Processing**: Use `easyocr.Reader(['vi', 'en'])` for Vietnamese/English text recognition
- **API Calls**: Frontend uses `APIService.py` for HTTP requests to backend

## Code Patterns
- **Route Handlers**: Extract JSON data, validate inputs, call service logic, return jsonify responses
- **Service Methods**: Static methods in classes, return (success: bool, message: str) tuples
- **Model Initialization**: Use setters for validation, generate IDs if not provided
- **Frontend Navigation**: `page.go()` for route changes, async event handlers
- **Error Handling**: Try/except blocks returning 400/500 status codes with error messages

## Integration Points
- **Supabase**: Primary database and file storage - configure URL/KEY in `ExcuteDatabase.py`
- **Email/SMS**: SMTP for email OTP, external API for SMS (credentials in `AuthService.py`)
- **OCR**: EasyOCR for license scanning - preprocess images with OpenCV rotations/sharpening