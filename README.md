# AROLS

🔍 **Uncover hidden insights in your legacy codebase**

CodeArcheology is a lightweight code analysis tool that helps developers understand complex codebases by identifying security vulnerabilities, code smells, business logic patterns, and providing actionable recommendations for modernization.

## ✨ Features

- **🛡️ Security Analysis** - Detects hardcoded secrets, SQL injection risks, and unsafe code patterns
- **🔧 Code Quality Assessment** - Identifies code smells, complexity issues, and technical debt
- **💼 Business Logic Extraction** - Finds valuable business logic patterns that could be extracted into APIs
- **📊 Multi-language Support** - Analyzes Python, JavaScript, Go, Java, C++, PHP, Ruby, Rust, and more
- **⚡ Fast Analysis** - Processes entire codebases in seconds
- **🎯 Actionable Insights** - Provides concrete recommendations for improvement

## 🏗️ Architecture

### Backend (Go)
- **REST API** built with Gin framework
- **Asynchronous job processing** for handling large codebases
- **File upload and extraction** with ZIP support
- **In-memory job store** (easily replaceable with database)

### Analysis Engine (Python)
- **AST-based analysis** for deep code understanding
- **Pattern matching** for security issue detection
- **Cyclomatic complexity calculation**
- **Business logic pattern recognition**

### Frontend (HTML/JS)
- **Modern glass-morphism UI** with drag-and-drop file upload
- **Real-time progress tracking** with polling
- **Interactive results dashboard**
- **Mobile-responsive design**

## 🚀 Quick Start

### Prerequisites
- Go 1.19+ 
- Python 3.8+
- `unzip` command available in PATH

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/codearcheology-mvp.git
cd codearcheology-mvp
```

2. **Set up Go dependencies**
```bash
go mod init codearcheology-mvp
go get github.com/gin-gonic/gin
go get github.com/google/uuid
go mod tidy
```

3. **Create required directories**
```bash
mkdir -p uploads results templates
```

4. **Move the HTML template**
```bash
mv index.html templates/
```

5. **Start the server**
```bash
go run main.go
```

6. **Open your browser**
Navigate to `http://localhost:8080` and start analyzing!

## 📁 Project Structure

```
codearcheology-mvp/
├── main.go              # Go REST API server
├── analyzer.py          # Python analysis engine
├── test_runner.py       # End-to-end testing script
├── templates/
│   └── index.html       # Frontend interface
├── uploads/             # Temporary file storage
├── results/             # Analysis results (JSON)
└── README.md
```

## 🔧 API Reference

### Upload and Analyze
```http
POST /api/analyze
Content-Type: multipart/form-data

Form Data:
- codebase: ZIP file containing source code
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "pending",
  "message": "Analysis started..."
}
```

### Check Job Status
```http
GET /api/job/{job_id}
```

**Response:**
```json
{
  "id": "uuid-string",
  "status": "completed|processing|pending|failed",
  "created_at": "2025-01-01T00:00:00Z",
  "completed_at": "2025-01-01T00:01:00Z"
}
```

### Get Analysis Results
```http
GET /api/result/{job_id}
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "project_name": "my-project",
  "total_files": 42,
  "total_lines": 1337,
  "languages": {"Python": 15, "JavaScript": 8},
  "complexity_score": 7.2,
  "security_issues": [...],
  "code_smells": [...],
  "business_logic": [...],
  "recommendations": [...]
}
```

## 🧪 Testing

Run the included test suite to verify everything works:

```bash
python3 test_runner.py
```

This creates a dummy project with various code issues and tests the complete analysis pipeline.

## 🛠️ Technical Details

### Security Detection Patterns
- **Hardcoded Credentials**: Regex patterns for passwords, API keys, tokens
- **SQL Injection**: Unsafe string concatenation in SQL queries  
- **Code Injection**: `eval()`, `exec()`, and shell command injection
- **Unsafe Functions**: `os.system()`, `subprocess.call()` with user input

### Code Quality Metrics
- **Cyclomatic Complexity**: AST-based calculation using control flow analysis
- **Line Length**: Configurable threshold (default: 120 characters)
- **Magic Numbers**: Detection of hardcoded numeric literals
- **Technical Debt**: TODO/FIXME comment tracking

### Business Logic Recognition
Identifies functions containing keywords like:
- Financial: `payment`, `invoice`, `billing`, `tax`, `discount`
- Authentication: `login`, `authenticate`, `authorize`, `permission`
- Data Processing: `calculate`, `compute`, `process`, `validate`

## 🔄 Workflow

1. **Upload**: User uploads ZIP file via web interface
2. **Extract**: Go server extracts ZIP to temporary directory
3. **Analyze**: Python engine performs AST analysis and pattern matching
4. **Store**: Results saved as JSON file
5. **Retrieve**: Frontend polls for completion and displays results
6. **Cleanup**: Temporary files removed after processing

## ⚡ Performance

- **Small projects** (<100 files): ~2-5 seconds
- **Medium projects** (100-1000 files): ~10-30 seconds  
- **Large projects** (1000+ files): ~1-5 minutes

Memory usage scales linearly with codebase size.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## 🎯 Roadmap

- [ ] **Database integration** (PostgreSQL/SQLite)
- [ ] **Distributed analysis** with Redis job queue
- [ ] **More languages** (C#, Kotlin, Swift, Scala)
- [ ] **Advanced security scanning** (OWASP integration)
- [ ] **Git repository analysis** (commit history insights)
- [ ] **Trend tracking** (complexity over time)
- [ ] **Team collaboration** features
- [ ] **CI/CD integration** (GitHub Actions, Jenkins)

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Gin Web Framework](https://gin-gonic.com/)
- Inspired by tools like SonarQube and CodeClimate
- UI design influenced by modern glassmorphism trends

---

**Made with ❤️ for developers drowning in legacy code**