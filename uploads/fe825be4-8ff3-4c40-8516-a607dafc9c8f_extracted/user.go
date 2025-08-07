// File: internal/user/user.go
package user

import (
	"context"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"golang.org/x/crypto/bcrypt"
)

// User defines the structure for a user in our application.
type User struct {
	ID           int       `json:"id"`
	Email        string    `json:"email"`
	PasswordHash string    `json:"-"` // The '-' tag prevents this from ever being sent in JSON responses
	CreatedAt    time.Time `json:"created_at"`
}

// Store handles all database operations related to users.
type Store struct {
	db *pgxpool.Pool
}

// NewStore creates a new user Store.
func NewStore(db *pgxpool.Pool) *Store {
	return &Store{db: db}
}

// Create inserts a new user into the database. It hashes the password before storing.
func (s *Store) Create(ctx context.Context, email, password string) (*User, error) {
	// Hash the password using bcrypt.
	// bcrypt.DefaultCost is a good balance of security and performance.
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return nil, err
	}

	// The SQL query to insert a new user.
	// We use RETURNING to get the new user's data back from the database in one query.
	query := `INSERT INTO users (email, password_hash) VALUES ($1, $2)
			  RETURNING id, email, password_hash, created_at`

	var u User
	// Execute the query.
	err = s.db.QueryRow(ctx, query, email, string(hashedPassword)).Scan(&u.ID, &u.Email, &u.PasswordHash, &u.CreatedAt)
	if err != nil {
		return nil, err
	}

	return &u, nil
}

// GetByEmail retrieves a user by their email address.
// This will be used during the login process.
func (s *Store) GetByEmail(ctx context.Context, email string) (*User, error) {
	query := `SELECT id, email, password_hash, created_at FROM users WHERE email = $1`

	var u User
	err := s.db.QueryRow(ctx, query, email).Scan(&u.ID, &u.Email, &u.PasswordHash, &u.CreatedAt)
	if err != nil {
		// It's common for a user not to be found, so we can handle this error specifically.
		return nil, err
	}

	return &u, nil
}

// Authenticate checks if a given password matches the stored hash for a user.
func (s *Store) Authenticate(ctx context.Context, email, password string) (*User, error) {
	// First, get the user by their email.
	user, err := s.GetByEmail(ctx, email)
	if err != nil {
		return nil, err // User not found
	}

	// Compare the provided password with the stored hash.
	// bcrypt.CompareHashAndPassword handles this securely.
	err = bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(password))
	if err != nil {
		// If they don't match, bcrypt returns an error.
		return nil, err // Invalid password
	}

	// Passwords match. Return the user.
	return user, nil
}
