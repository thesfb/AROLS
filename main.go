// main.go - Go REST API Server
package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// Job represents an analysis job
type Job struct {
	ID          string     `json:"id"`
	Status      string     `json:"status"` // pending, processing, completed, failed
	UploadPath  string     `json:"upload_path"`
	ResultPath  string     `json:"result_path,omitempty"`
	CreatedAt   time.Time  `json:"created_at"`
	CompletedAt *time.Time `json:"completed_at,omitempty"`
	Error       string     `json:"error,omitempty"`
}

// AnalysisResult represents the analysis output
type AnalysisResult struct {
	JobID           string                 `json:"job_id"`
	ProjectName     string                 `json:"project_name"`
	TotalFiles      int                    `json:"total_files"`
	TotalLines      int                    `json:"total_lines"`
	Languages       map[string]int         `json:"languages"`
	ComplexityScore float64                `json:"complexity_score"`
	SecurityIssues  []SecurityIssue        `json:"security_issues"`
	CodeSmells      []CodeSmell            `json:"code_smells"`
	BusinessLogic   []BusinessLogicPattern `json:"business_logic"`
	Recommendations []string               `json:"recommendations"`
	GeneratedAt     string                 `json:"generated_at"`
}

type SecurityIssue struct {
	Type        string `json:"type"`
	Severity    string `json:"severity"`
	File        string `json:"file"`
	Line        int    `json:"line"`
	Description string `json:"description"`
}

type CodeSmell struct {
	Type        string `json:"type"`
	File        string `json:"file"`
	Line        int    `json:"line"`
	Description string `json:"description"`
	Suggestion  string `json:"suggestion"`
}

type BusinessLogicPattern struct {
	Type        string `json:"type"`
	File        string `json:"file"`
	Function    string `json:"function"`
	Description string `json:"description"`
	Value       string `json:"value"`
}

// In-memory job store (use database in production)
var jobs = make(map[string]*Job)

func main() {
	// Create necessary directories
	os.MkdirAll("uploads", 0755)
	os.MkdirAll("results", 0755)

	r := gin.Default()

	// CORS middleware for frontend
	r.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type")
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	})

	// Routes
	r.POST("/api/analyze", uploadAndAnalyze)
	r.GET("/api/job/:id", getJobStatus)
	r.GET("/api/result/:id", getAnalysisResult)
	r.GET("/health", healthCheck)

	// Serve static files (for simple frontend)
	r.Static("/static", "./static")
	r.LoadHTMLGlob("templates/*")
	r.GET("/", func(c *gin.Context) {
		c.HTML(http.StatusOK, "index.html", gin.H{
			"title": "CodeArcheology MVP",
		})
	})

	log.Println(" CodeArcheology MVP starting on :8080")
	log.Fatal(r.Run(":8080"))
}

func uploadAndAnalyze(c *gin.Context) {
	// Handle file upload
	file, err := c.FormFile("codebase")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No file uploaded"})
		return
	}

	// Generate job ID
	jobID := uuid.New().String()

	// Save uploaded file
	uploadPath := filepath.Join("uploads", jobID+".zip")
	if err := c.SaveUploadedFile(file, uploadPath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
		return
	}

	// Create job record
	job := &Job{
		ID:         jobID,
		Status:     "pending",
		UploadPath: uploadPath,
		CreatedAt:  time.Now(),
	}
	jobs[jobID] = job

	// Start analysis in background
	go runAnalysis(jobID)

	c.JSON(http.StatusOK, gin.H{
		"job_id":  jobID,
		"status":  "pending",
		"message": "Analysis started. Check /api/job/" + jobID + " for status.",
	})
}

func runAnalysis(jobID string) {
	job := jobs[jobID]
	if job == nil {
		log.Printf("Job %s not found in runAnalysis", jobID)
		return
	}

	// Update status
	job.Status = "processing"
	log.Printf("Starting analysis for job %s", jobID)

	// Extract uploaded zip file
	extractPath := filepath.Join("uploads", jobID+"_extracted")
	if err := extractZip(job.UploadPath, extractPath); err != nil {
		log.Printf("Failed to extract zip for job %s: %v", jobID, err)
		job.Status = "failed"
		job.Error = "Failed to extract ZIP file: " + err.Error()
		return
	}

	// Update the result path in the job
	resultPath := filepath.Join("results", jobID+".json")

	// Call Python analyzer with proper error handling
	cmd := exec.Command("python3", "analyzer.py", extractPath, resultPath)
	output, err := cmd.CombinedOutput()

	if err != nil {
		log.Printf("Python analysis failed for job %s: %v\nOutput: %s", jobID, err, string(output))
		job.Status = "failed"
		job.Error = "Analysis failed: " + err.Error()
		return
	}

	// Check if result file was created
	if _, err := os.Stat(resultPath); os.IsNotExist(err) {
		log.Printf("Result file not created for job %s", jobID)
		job.Status = "failed"
		job.Error = "Result file was not generated"
		return
	}

	// Update the job_id in the result file
	if err := updateJobIDInResult(resultPath, jobID); err != nil {
		log.Printf("Failed to update job_id in result for job %s: %v", jobID, err)
		// Don't fail the job for this, just log the error
	}

	// Update job status
	now := time.Now()
	job.Status = "completed"
	job.ResultPath = resultPath
	job.CompletedAt = &now

	log.Printf(" Analysis completed for job %s", jobID)
}

func updateJobIDInResult(resultPath, jobID string) error {
	// Read the result file
	data, err := os.ReadFile(resultPath)
	if err != nil {
		return err
	}

	// Parse JSON
	var result map[string]interface{}
	if err := json.Unmarshal(data, &result); err != nil {
		return err
	}

	// Update job_id
	result["job_id"] = jobID

	// Write back to file
	updatedData, err := json.MarshalIndent(result, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(resultPath, updatedData, 0644)
}

func getJobStatus(c *gin.Context) {
	jobID := c.Param("id")
	job := jobs[jobID]

	if job == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Job not found"})
		return
	}

	c.JSON(http.StatusOK, job)
}

func getAnalysisResult(c *gin.Context) {
	jobID := c.Param("id")
	job := jobs[jobID]

	if job == nil {
		log.Printf("Job %s not found in getAnalysisResult", jobID)
		c.JSON(http.StatusNotFound, gin.H{"error": "Job not found"})
		return
	}

	if job.Status == "failed" {
		log.Printf("Job %s failed: %s", jobID, job.Error)
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Analysis failed",
			"details": job.Error,
		})
		return
	}

	if job.Status != "completed" {
		log.Printf("Job %s not completed yet, status: %s", jobID, job.Status)
		c.JSON(http.StatusBadRequest, gin.H{"error": "Analysis not completed yet"})
		return
	}

	// Check if result path exists
	if job.ResultPath == "" {
		log.Printf("No result path for job %s", jobID)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "No result path available"})
		return
	}

	// Check if file exists
	if _, err := os.Stat(job.ResultPath); os.IsNotExist(err) {
		log.Printf("Result file does not exist for job %s: %s", jobID, job.ResultPath)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Result file not found"})
		return
	}

	// Read analysis result from file
	resultFile, err := os.ReadFile(job.ResultPath)
	if err != nil {
		log.Printf("Failed to read result file for job %s: %v", jobID, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read result file"})
		return
	}

	// Parse and validate JSON
	var result AnalysisResult
	if err := json.Unmarshal(resultFile, &result); err != nil {
		log.Printf("Failed to parse result JSON for job %s: %v", jobID, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse result"})
		return
	}

	log.Printf("Successfully returning results for job %s", jobID)
	c.JSON(http.StatusOK, result)
}

func healthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "healthy",
		"service":   "codearcheology-mvp",
		"timestamp": time.Now().Unix(),
	})
}

func extractZip(zipPath, extractPath string) error {
	// Create the extraction directory
	if err := os.MkdirAll(extractPath, 0755); err != nil {
		return err
	}

	cmd := exec.Command("unzip", "-q", zipPath, "-d", extractPath)
	return cmd.Run()
}
