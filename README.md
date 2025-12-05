# **PKI 2FA Microservice**

This project is a small authentication microservice that uses RSA encryption and TOTP codes for two-factor authentication. It decrypts a secure seed, generates 6-digit TOTP codes, verifies them, and logs codes every minute using a cron job. The whole service runs inside Docker with persistent storage.

---

## **Features**

* RSA 4096-bit key pair
* Decrypt encrypted seed
* Generate TOTP 2FA codes
* Verify TOTP codes
* Cron job logs codes every minute
* Runs fully in Docker

---

## **API Endpoints**

* **POST /decrypt-seed** → decrypts seed and saves it
* **GET /generate-2fa** → returns current 6-digit TOTP
* **POST /verify-2fa** → checks if a TOTP code is valid

---

## **How to Run (Docker)**

```
docker compose build
docker compose up -d
```

API runs at:

```
http://localhost:8080
```

---

## **What I Learned**

I learned how RSA encryption works, how to generate and verify TOTP codes, how to use Docker, and how to run cron jobs inside a container. This project helped me understand secure backend development in a practical way.

