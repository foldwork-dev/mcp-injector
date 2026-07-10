package handler

import (
	"bytes"
	"crypto/ed25519"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"

	svix "github.com/svix/svix-webhooks/go"
)

// WebhookPayload represents the Dodo Payments webhook event payload structure.
type WebhookPayload struct {
	Type string `json:"type"`
	Data struct {
		Customer struct {
			Email string `json:"email"`
		} `json:"customer"`
		NextBillingDate string `json:"next_billing_date"`
	} `json:"data"`
}

// LicensePayload matches the schema in auth/licensing.go
type LicensePayload struct {
	Sub  string `json:"sub"`  // customer email
	Plan string `json:"plan"` // "pro"
	Exp  int64  `json:"exp"`  // unix expiry seconds
	Iat  int64  `json:"iat"`  // unix issued at seconds
}

// ResendEmailPayload is the payload sent to the Resend API to send an email.
type ResendEmailPayload struct {
	From    string `json:"from"`
	To      string `json:"to"`
	Subject string `json:"subject"`
	HTML    string `json:"html"`
}

func Handler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Failed to read request body", http.StatusBadRequest)
		return
	}

	// ─── 1. Verify Webhook Signature using Svix ───────────────────────────────
	webhookSecret := os.Getenv("DODO_PAYMENTS_WEBHOOK_SECRET")

	if webhookSecret == "" {
		fmt.Println("ERROR: DODO_PAYMENTS_WEBHOOK_SECRET is not set. Failing closed.")
		http.Error(w, "Webhook secret not configured", http.StatusInternalServerError)
		return
	}

	headers := http.Header{}
	headers.Set("svix-id", r.Header.Get("webhook-id"))
	headers.Set("svix-timestamp", r.Header.Get("webhook-timestamp"))
	headers.Set("svix-signature", r.Header.Get("webhook-signature"))

	wh, err := svix.NewWebhook(webhookSecret)
	if err != nil {
		http.Error(w, "Invalid webhook secret configuration", http.StatusInternalServerError)
		return
	}

	err = wh.Verify(body, headers)
	if err != nil {
		http.Error(w, "Invalid webhook signature", http.StatusUnauthorized)
		return
	}

	// ─── 2. Parse Webhook Event JSON ──────────────────────────────────────────
	var payload WebhookPayload
	if err := json.Unmarshal(body, &payload); err != nil {
		http.Error(w, "Failed to parse webhook JSON", http.StatusBadRequest)
		return
	}

	eventName := payload.Type
	userEmail := strings.TrimSpace(payload.Data.Customer.Email)

	fmt.Printf("Received event: %s, email: %s\n", eventName, userEmail)

	// Validate email exists before routing
	if userEmail == "" {
		http.Error(w, "Missing customer email in webhook payload", http.StatusBadRequest)
		return
	}

	switch eventName {
	case "payment.failed":
		sendSimpleEmail(
			userEmail,
			"Action Required: Payment Failed",
			"Payment Failed",
			"We were unable to process your recent payment for your mcp-injector Pro subscription.",
			"Please update your payment method through the billing portal to ensure uninterrupted access.",
		)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "Processed payment.failed")
		return
	case "subscription.cancelled":
		expiryText := "the end of your current billing period"
		if payload.Data.NextBillingDate != "" {
			t, err := time.Parse(time.RFC3339Nano, payload.Data.NextBillingDate)
			if err == nil {
				expiryText = t.Format("January 2, 2006")
			}
		}

		sendSimpleEmail(
			userEmail,
			"Subscription Cancelled",
			"Subscription Cancelled",
			"Your mcp-injector Pro subscription has been cancelled successfully.",
			fmt.Sprintf("We're sorry to see you go! Your license key will remain active and valid until %s.", expiryText),
		)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "Processed subscription.cancelled")
		return
	case "subscription.on_hold":
		sendSimpleEmail(
			userEmail,
			"Action Required: Subscription On Hold",
			"Subscription On Hold",
			"Your mcp-injector Pro subscription has been placed on hold because your renewal payment failed.",
			"Your license will be revoked soon. Please update your payment method to keep your access active.",
		)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "Processed subscription.on_hold")
		return
	case "payment.succeeded", "subscription.active":
		// Proceed to generate license
	default:
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "Event ignored: status is not handled")
		return
	}

	if userEmail == "" {
		http.Error(w, "Missing customer email in webhook payload", http.StatusBadRequest)
		return
	}

	// ─── 3. Generate the Cryptographic License Key ──────────────────────────
	privateKeyHex := os.Getenv("MCP_LICENSE_PRIVATE_KEY")
	if privateKeyHex == "" {
		http.Error(w, "MCP_LICENSE_PRIVATE_KEY environment variable is not configured", http.StatusInternalServerError)
		return
	}

	seed, err := hex.DecodeString(strings.TrimSpace(privateKeyHex))
	if err != nil || len(seed) != ed25519.SeedSize {
		http.Error(w, "MCP_LICENSE_PRIVATE_KEY is not a valid 32-byte hex seed", http.StatusInternalServerError)
		return
	}

	privateKey := ed25519.NewKeyFromSeed(seed)

	// Determine plan length (Monthly vs Yearly)
	now := time.Now().UTC()
	var duration time.Duration

	// Check if the raw JSON payload contains the Dodo Payments Yearly Product ID
	if bytes.Contains(body, []byte("pdt_0NipTwQvleXFAze0ndedX")) {
		duration = 370 * 24 * time.Hour // 1 year + 5 days grace period
	} else {
		duration = 35 * 24 * time.Hour // 1 month + 5 days grace period
	}

	licensePayload := LicensePayload{
		Sub:  userEmail,
		Plan: "pro",
		Exp:  now.Add(duration).Unix(),
		Iat:  now.Unix(),
	}

	licenseBytes, err := json.Marshal(licensePayload)
	if err != nil {
		http.Error(w, "Failed to marshal license payload JSON", http.StatusInternalServerError)
		return
	}

	// Cryptographically sign the license payload using Ed25519
	signature := ed25519.Sign(privateKey, licenseBytes)

	// Concat: [signature (64 bytes)][payload bytes (variable JSON)]
	finalBlob := append(signature, licenseBytes...)
	licenseKeyHex := hex.EncodeToString(finalBlob)

	// ─── 4. Deliver the License Key via Resend Email API ──────────────────────
	resendAPIKey := os.Getenv("RESEND_API_KEY")
	if resendAPIKey == "" {
		// Log key and proceed to respond 200 so we don't lose the webhook if only email config is missing
		fmt.Printf("WARNING: RESEND_API_KEY is not set. Generated License Key for %s: %s\n", userEmail, licenseKeyHex)
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, "License generated successfully (Email skipped: RESEND_API_KEY missing): %s", licenseKeyHex)
		return
	}

	senderEmail := os.Getenv("RESEND_SENDER_EMAIL")
	if senderEmail == "" {
		// Resend free tier onboarding default address if custom domain is not yet verified
		senderEmail = "Foldwork <onboarding@resend.dev>"
	}

	emailSubject := "Your mcp-injector Pro License Key"
	emailHTML := fmt.Sprintf(`
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #1f2937; max-width: 600px; margin: 0 auto; padding: 20px; }
    .card { background: #0d1117; color: #f0f6fc; padding: 25px; border-radius: 12px; border: 1px solid rgba(240, 246, 252, 0.1); margin: 20px 0; }
    .code { font-family: "JetBrains Mono", Consolas, monospace; background: rgba(255,255,255,0.08); padding: 12px; border-radius: 6px; word-break: break-all; font-size: 0.95rem; color: #f0f6fc; border: 1px solid rgba(255,255,255,0.1); user-select: all; }
    .btn { display: inline-block; background: #7c3aed; color: white !important; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; margin-top: 15px; }
    .footer { font-size: 0.85rem; color: #6b7280; margin-top: 30px; border-top: 1px solid #e5e7eb; padding-top: 15px; }
  </style>
</head>
<body>
  <h2>Welcome to mcp-injector Pro!</h2>
  <p>Thank you for your purchase. Your license key has been generated and is ready for use.</p>
  
  <div class="card">
    <div style="font-weight: 600; margin-bottom: 8px; color: #a78bfa;">YOUR PRO LICENSE KEY:</div>
    <div class="code">%s</div>
  </div>

  <h3>How to Activate:</h3>
  <p>Open your terminal in your workspace directory and run the following command to activate your Pro license key:</p>
  <div style="font-family: monospace; background: #f3f4f6; padding: 10px; border-radius: 6px; border: 1px solid #e5e7eb; color: #111827;">
    mcp-injector --activate %s
  </div>

  <p>Once activated, the daemon runs completely offline on your computer. You will have full access to unlimited codebase sizes, token savings logs, and AST body folding context optimization.</p>

  <p>Need help or have questions? Just reply directly to this email or visit our website.</p>

  <div class="footer">
    <p>Sent by <b>Foldwork.dev</b> — High performance context compression tools for developers.</p>
  </div>
</body>
</html>
`, licenseKeyHex, licenseKeyHex)

	emailPayload := ResendEmailPayload{
		From:    senderEmail,
		To:      userEmail,
		Subject: emailSubject,
		HTML:    emailHTML,
	}

	payloadJSON, _ := json.Marshal(emailPayload)
	req, err := http.NewRequest(http.MethodPost, "https://api.resend.com/emails", bytes.NewBuffer(payloadJSON))
	if err != nil {
		http.Error(w, "Failed to construct Resend email request", http.StatusInternalServerError)
		return
	}

	req.Header.Set("Authorization", "Bearer "+resendAPIKey)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("ERROR: Failed to send email via Resend: %v\n", err)
		http.Error(w, "License generated but failed to send email", http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		respBody, _ := io.ReadAll(resp.Body)
		fmt.Printf("ERROR: Resend API returned status %d: %s\n", resp.StatusCode, string(respBody))
		http.Error(w, "License generated but Resend API rejected email sending", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w, "License successfully generated and email delivered to %s", userEmail)
}

func sendSimpleEmail(to, subject, title, p1, p2 string) error {
	resendAPIKey := os.Getenv("RESEND_API_KEY")
	if resendAPIKey == "" {
		fmt.Printf("WARNING: RESEND_API_KEY is not set. Skipping email to %s\n", to)
		return nil
	}
	senderEmail := os.Getenv("RESEND_SENDER_EMAIL")
	if senderEmail == "" {
		senderEmail = "Foldwork <onboarding@resend.dev>"
	}

	html := fmt.Sprintf(`<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #1f2937; max-width: 600px; margin: 0 auto; padding: 20px; }
    .footer { font-size: 0.85rem; color: #6b7280; margin-top: 30px; border-top: 1px solid #e5e7eb; padding-top: 15px; }
  </style>
</head>
<body>
  <h2>%s</h2>
  <p>%s</p>
  <p>%s</p>
  <div class="footer">
    <p>Sent by <b>Foldwork.dev</b> — High performance context compression tools for developers.</p>
  </div>
</body>
</html>`, title, p1, p2)

	emailPayload := ResendEmailPayload{
		From:    senderEmail,
		To:      to,
		Subject: subject,
		HTML:    html,
	}
	payloadJSON, _ := json.Marshal(emailPayload)
	req, err := http.NewRequest(http.MethodPost, "https://api.resend.com/emails", bytes.NewBuffer(payloadJSON))
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+resendAPIKey)
	req.Header.Set("Content-Type", "application/json")
	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}
