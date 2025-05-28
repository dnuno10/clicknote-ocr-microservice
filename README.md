# Click Note OCR Microservice

A cloud-native, secure Optical Character Recognition (OCR) microservice built with FastAPI and Microsoft's TrOCR model. This project implements a hybrid architecture where OCR inference runs on local hardware while providing a scalable, cloud-hosted API accessible to mobile applications and other clients.

## Architecture Overview

The system implements a distributed microservice architecture that separates computational workload from API management, resulting in cost-effective deployment while maintaining high performance and security standards.

![Click Note](https://github.com/user-attachments/assets/a3e66902-9598-4c17-89d0-874946734af8)

The technical and conceptual details are defined in the following document: [Public API Network (PDF)](https://github.com/dnuno10/clicknote-ocr-microservice/blob/main/Public_API_Network_FINAL.pdf).

### System Flow Diagram

```
[Mobile Client] → [DNS Resolution] → [NGINX Reverse Proxy] → [FastAPI API]
                                                                    ↓
[Email Service] ← [FTP Server] ← [Authentication Layer] ← [Request Handler]
       ↑                                                           ↓
[SMTP/Resend]                                          [SSH Tunnel to Local]
                                                              ↓
                                                    [Local TrOCR Model]
```

### Key Components

- **Cloud API Server**: FastAPI application with NGINX reverse proxy
- **Local Inference Engine**: TrOCR model running on dedicated hardware
- **Security Layer**: HMAC-based authentication with custom headers
- **File Management**: FTP server for image upload and processing
- **Communication**: SMTP email delivery for asynchronous results
- **Database**: Supabase for client credential management
- **Networking**: DNS resolution and SSH tunneling for secure connectivity

## Features

### Core Functionality
- **Transformer-based OCR**: Utilizes Microsoft's TrOCR model for high-accuracy text recognition
- **RESTful API**: Clean, documented endpoints for easy integration
- **Hybrid Deployment**: Local model inference with cloud API accessibility
- **Mobile-First Design**: Optimized for mobile application integration
- **Asynchronous Processing**: Non-blocking request handling with optional email delivery

### Security
- **HMAC Authentication**: Custom header-based authentication without JWT dependency
- **Request Integrity**: Cryptographic signature validation for all requests
- **Timestamp Validation**: Replay attack prevention with time-bounded requests
- **Client Isolation**: Individual API credentials for each registered client
- **Secure Tunneling**: SSH reverse proxy for local model access

### Scalability
- **Modular Architecture**: Independent scaling of components
- **Service Decoupling**: Replaceable components (FTP, email, database)
- **Resource Optimization**: Offloaded computation to dedicated hardware
- **Fault Tolerance**: Comprehensive error handling and graceful degradation

## Technical Stack

### Backend Services
- **FastAPI**: Python web framework for API development
- **TrOCR**: Microsoft's transformer-based OCR model
- **NGINX**: Reverse proxy and load balancer
- **Supabase**: PostgreSQL-based backend-as-a-service
- **pyftpdlib**: Python FTP server implementation
- **Resend API**: Email delivery service

### Infrastructure
- **Cloud VM**: 2GB RAM, 1 CPU core, 50GB SSD
- **Local Machine**: Dedicated hardware for model inference
- **SSH Tunneling**: Secure connection between cloud and local resources
- **DNS Management**: Public domain resolution
- **SSL/TLS**: HTTPS encryption for all communications

### Mobile Integration
- **Flutter**: Cross-platform mobile application framework
- **Dart HTTP**: Client-side API communication
- **Image Compression**: Intelligent file size optimization
- **HMAC Generation**: Client-side signature creation

## Installation and Setup

### Prerequisites
- Python 3.8+
- Docker (optional)
- SSH access to deployment server
- Supabase account
- Resend API key
- Domain name with DNS management

### Cloud Server Setup

1. **Clone the repository**
```bash
git clone https://github.com/dnuno10/clicknote-ocr-microservice.git
cd clicknote-ocr-microservice
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
# Create .env file
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
RESEND_API_KEY=your_resend_api_key
FTP_HOST=your_ftp_host
FTP_PORT=21
API_HOST=0.0.0.0
API_PORT=8000
```

4. **Setup NGINX reverse proxy**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;
    }
}
```

5. **Start the API server**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

6. **Start the FTP server**
```bash
python scripts/server.py
```

### Local Model Server Setup

1. **Install model dependencies**
```bash
pip install transformers torch torchvision pillow
```

2. **Start the model server**
```bash
python model_server.py --port 8001
```

3. **Establish SSH tunnel**
```bash
ssh -i ocr_api_client_key -R 8001:localhost:8001 root@your-cloud-server
```

### Database Schema

The system uses Supabase with the following table structure:

```sql
CREATE TABLE api_clients (
    idAPI SERIAL PRIMARY KEY,
    idUser UUID REFERENCES auth.users(id),
    apiKey VARCHAR(255) UNIQUE NOT NULL,
    apiSecret VARCHAR(255) NOT NULL,
    usageCounter INTEGER DEFAULT 0,
    lastUsedAt TIMESTAMP WITH TIME ZONE,
    createdAt TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## API Documentation

### Authentication

All requests must include the following headers:

- `X-API-KEY`: Unique client identifier
- `X-TIMESTAMP`: UTC timestamp (ISO 8601 format)
- `X-SIGNATURE`: HMAC-SHA256 signature

#### Signature Generation

```python
import hmac
import hashlib

def generate_signature(api_secret, timestamp, path):
    payload = f"{timestamp}{path}"
    signature = hmac.new(
        api_secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature
```

### Endpoints

#### POST /prediction/ftp_upload_and_predict/

Upload an image and receive OCR prediction.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Query Parameters:
  - `email` (optional): Email address for result delivery

**Headers:**
```
X-API-KEY: your-api-key
X-TIMESTAMP: 2025-05-26T10:30:00Z
X-SIGNATURE: calculated-hmac-signature
```

**Response:**
```json
{
    "filename": "example.jpg",
    "prediction": "Extracted text from the image",
    "timestamp": "2025-05-26T10:30:15Z",
    "email_sent": true
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid headers
- `403 Forbidden`: Invalid API key or signature
- `413 Request Entity Too Large`: File size exceeds limit
- `422 Unprocessable Entity`: Invalid file format
- `500 Internal Server Error`: Model inference failure

## Mobile Integration

The mobile client demonstrates production-ready integration with the OCR microservice.

![ocr_menu_option](https://github.com/user-attachments/assets/fedc3b97-d8fa-404d-892a-50e1022bf7bc) ![ocr_loading_fetch](https://github.com/user-attachments/assets/db7cba35-1c82-4525-a3df-edef9d635d70) ![ocr_result_display](https://github.com/user-attachments/assets/7bf6cdb4-325c-4665-9414-77e8ac863cba)




### Flutter Service Implementation

```dart
class OcrService {
  static const String baseUrl = 'https://your-domain.com';
  
  Future<OcrResult> processImage(File imageFile, String email) async {
    // Generate authentication headers
    final credentials = await _generateCredentials();
    
    // Compress image if necessary
    final compressedImage = await _compressImage(imageFile);
    
    // Create multipart request
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/prediction/ftp_upload_and_predict/'),
    );
    
    // Add authentication headers
    request.headers.addAll({
      'X-API-KEY': credentials.apiKey,
      'X-TIMESTAMP': credentials.timestamp,
      'X-SIGNATURE': credentials.signature,
    });
    
    // Add file and email
    request.files.add(await http.MultipartFile.fromPath(
      'file',
      compressedImage.path,
    ));
    
    if (email.isNotEmpty) {
      request.fields['email'] = email;
    }
    
    // Send request and process response
    final response = await request.send();
    final responseBody = await response.stream.bytesToString();
    
    if (response.statusCode == 200) {
      return OcrResult.fromJson(json.decode(responseBody));
    } else {
      throw OcrException(response.statusCode, responseBody);
    }
  }
}
```

### Mobile Application Screenshots

The following screenshots demonstrate the mobile implementation:

1. **Main Menu Interface**: Clean, intuitive access to OCR functionality
2. **Processing Interface**: Real-time feedback during API communication
3. **Results Display**: Extracted text in an editable format for further manipulation

### Image Compression Strategy

The mobile client implements intelligent compression to optimize upload performance:

```dart
Future<File> _compressImage(File file) async {
  final fileSize = await file.length();
  
  // Skip compression for small files
  if (fileSize < 100 * 1024) return file;
  
  // Determine compression parameters based on file size
  int quality = 70;
  int targetWidth = 1920;
  int targetHeight = 1080;
  
  if (fileSize > 2 * 1024 * 1024) {
    quality = 50;
    targetWidth = 1600;
    targetHeight = 900;
  }
  
  if (fileSize > 4 * 1024 * 1024) {
    quality = 40;
    targetWidth = 1280;
    targetHeight = 720;
  }
  
  return await FlutterImageCompress.compressAndGetFile(
    file.path,
    outputPath,
    quality: quality,
    minWidth: targetWidth,
    minHeight: targetHeight,
    format: CompressFormat.jpeg,
  );
}
```

## Security Implementation

### HMAC Authentication Flow

1. **Client Registration**: Generate unique API key and secret
2. **Request Preparation**: Create timestamp and calculate signature
3. **Server Validation**: Verify headers and signature integrity
4. **Database Lookup**: Validate client credentials against Supabase
5. **Request Processing**: Execute OCR pipeline for authenticated requests

### Security Features

- **Zero-Trust Architecture**: Every request requires cryptographic validation
- **Replay Attack Prevention**: Timestamp validation with 5-minute window
- **Request Integrity**: HMAC signature covers path and timestamp
- **Client Isolation**: Individual credentials prevent cross-client access
- **Secure Transport**: HTTPS encryption for all communications

## Performance Optimization

### Response Time Optimization
- Asynchronous request handling prevents blocking
- Local model inference reduces network latency
- Image compression minimizes transfer time
- Connection pooling for database operations

### Resource Management
- Modular service architecture enables independent scaling
- Local computation offloads cloud resource requirements
- FTP server provides efficient file transfer
- Email delivery operates asynchronously

### Monitoring and Logging
- Comprehensive error handling with informative messages
- Request tracking and usage analytics via Supabase
- Performance metrics collection for optimization
- Automated health checks for service availability

## Deployment Considerations

### Production Checklist
- [ ] SSL certificate configuration
- [ ] DNS propagation verification
- [ ] SSH key security and rotation
- [ ] Database connection pooling
- [ ] Log rotation and monitoring
- [ ] Backup and disaster recovery
- [ ] Load balancer configuration
- [ ] Rate limiting implementation

### Scaling Strategies
- **Horizontal Scaling**: Multiple model servers behind load balancer
- **Vertical Scaling**: Increased resources for model inference
- **Geographic Distribution**: Regional API deployments
- **Caching Layer**: Redis for frequent predictions
- **CDN Integration**: Static asset delivery optimization

## Troubleshooting

### Common Issues

**Authentication Errors (401/403)**
- Verify API key exists in Supabase
- Check timestamp format and server time synchronization
- Validate HMAC signature generation

**Model Server Connection Issues**
- Confirm SSH tunnel is active
- Verify local model server is running on correct port
- Check firewall settings on local machine

**File Upload Problems**
- Ensure FTP server is running and accessible
- Check file size limits and format restrictions
- Verify directory permissions for uploaded files

**Email Delivery Issues**
- Validate Resend API key configuration
- Check email address format and domain
- Review SMTP server connectivity

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export DEBUG=true
uvicorn main:app --reload --log-level debug
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Microsoft Research for the TrOCR model
- FastAPI community for excellent documentation
- Supabase team for backend-as-a-service platform
- Flutter team for mobile development framework

## Contact

- **Daniel Nuño** - dnuno@cetys.edu.mx
- **Kevin Hernandez** - kevin.hernandez@cetys.edu.mx  
- **Diego Hernandez** - diego.hernandez@cetys.edu.mx
- **Professor Moises Sanchez Adame** - moises.adame@cetys.mx

Project Link: [https://github.com/dnuno10/clicknote-ocr-microservice](https://github.com/dnuno10/clicknote-ocr-microservice)

## Citation

If you use this project in your research or development, please cite:

```
@article{nuno2025clicknote,
  title={Public API Network: A Cloud-Native OCR Microservice Implementation},
  author={Nuño, Daniel and Hernandez, Kevin and Hernandez, Diego and Adame, Moises Sanchez},
  journal={Networks and Communication Final Project},
  year={2025},
  institution={CETYS University}
}
```
