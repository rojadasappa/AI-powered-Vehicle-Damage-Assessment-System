# Vehicle Damage Assessment System

A simple and reliable AI-powered vehicle damage assessment system that uses computer vision to detect and analyze vehicle damage, estimate repair costs, and generate detailed reports.

## Features

- **Damage Detection**: Computer vision-based damage detection using image analysis
- **Cost Estimation**: Intelligent cost estimation based on damage type and severity
- **Web Interface**: User-friendly Flask web application
- **Report Generation**: Detailed damage assessment reports
- **User Management**: User registration, login, and damage history
- 
## Dataset
The car damage severity dataset is not included in this repository due to size constraints.

Dataset source:
- Kaggle: Car Damage Severity Dataset

To use the dataset:
1. Download the dataset from Kaggle
2. Extract it into:
   data/datasets/car_damage_severity/

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python3 app.py
```

The application will be available at: http://localhost:5001

### 3. Test the System
```bash
python3 test_simple.py
```

## Project Structure

```
├── app.py                          # Main Flask application
├── models.py                       # Database models
├── simple_damage_detector.py       # Core damage detection logic
├── cost_estimator.py              # Cost estimation system
├── report_generator.py            # Report generation
├── routes/                        # Flask route handlers
│   ├── auth.py                    # Authentication routes
│   ├── damage_assessment.py       # Damage assessment routes
│   ├── reports.py                 # Report generation routes
│   └── api.py                     # API endpoints
├── templates/                     # HTML templates
├── static/                        # Static files (CSS, JS, images)
├── data/                          # Data and datasets
└── test_simple.py                 # Test suite
```

## How It Works

### 1. Damage Detection
The system uses computer vision techniques to analyze uploaded images:
- **Edge Detection**: Identifies structural damage and cracks
- **Brightness Analysis**: Detects dents and paint damage
- **Color Analysis**: Identifies rust and paint issues
- **Pattern Recognition**: Distinguishes between different damage types

### 2. Damage Classification
- **Damage Types**: Scratch, Dent, Paint Damage, Bumper Damage, Broken Part, Crack, Rust, Headlight Damage, Glass Damage
- **Severity Levels**: Minor, Moderate, Severe, Critical
- **Confidence Scoring**: Provides confidence levels for each prediction

### 3. Cost Estimation
- **Parts Cost**: Based on damage type and vehicle specifications
- **Labor Cost**: Calculated using regional labor rates
- **Additional Costs**: Paint, materials, and specialized equipment
- **Repair Time**: Estimated repair duration

## API Endpoints

- `GET /` - Main dashboard
- `GET /api/health` - Health check
- `POST /damage/upload` - Upload images for damage assessment
- `GET /damage/results/<id>` - View damage assessment results
- `GET /damage/history` - View damage assessment history
- `POST /auth/login` - User login
- `POST /auth/register` - User registration

## Usage

### 1. Register/Login
- Create an account or login to access the system
- User profiles are stored securely with password hashing

### 2. Upload Images
- Upload one or more images of the damaged vehicle
- Supported formats: JPG, JPEG, PNG, GIF, WEBP
- Maximum file size: 16MB per image

### 3. View Results
- Get detailed damage assessment with:
  - Damage type and severity
  - Confidence score
  - Estimated repair cost
  - Repair time estimate
  - Cost breakdown

### 4. Generate Reports
- Create detailed PDF reports
- Save assessment history
- Export data for insurance claims

## Technical Details

### Dependencies
- **Flask**: Web framework
- **PIL/Pillow**: Image processing
- **NumPy**: Numerical computations
- **SQLAlchemy**: Database ORM
- **Flask-Login**: User authentication

### Database
- SQLite database for development
- User accounts and damage reports
- Automatic database initialization

### Image Processing
- Automatic image resizing and normalization
- RGB color space conversion
- Edge detection using gradient analysis
- Statistical analysis of image properties

## Testing

Run the test suite to verify functionality:
```bash
python3 test_simple.py
```

The test suite checks:
- Damage detection accuracy
- Cost estimation functionality
- Web application endpoints
- Database operations

## Performance

- **Detection Speed**: ~2ms per image
- **Accuracy**: 60-70% for basic damage types
- **Supported Formats**: JPG, JPEG, PNG, GIF, WEBP
- **Max Image Size**: 16MB per image

## Limitations

- Currently optimized for cars only
- Accuracy depends on image quality
- Best results with clear, well-lit images
- May require multiple angles for complex damage

## Future Improvements

- Machine learning model integration
- Support for more vehicle types
- Mobile app development
- Real-time damage assessment
- Integration with insurance systems

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request


## Support

For support or questions, please open an issue in the repository or contact the development team.
## 👩‍💻 Project Team

This project was developed by:

- **Roja H D**
- **Shravani**
- **Preeti**
- **Rimjhim**

---

**Note**: This is a simplified version focused on core functionality. The system provides reliable damage detection using computer vision techniques without complex machine learning dependencies.
