import { useEffect, useState } from "react";
import axios from "axios";
import "./index.css";

const API_URL = "https://fraudshield-ai-sxtt.onrender.com";

function App() {
  // =========================================================
  // AUTH STATE
  // =========================================================

  const [token, setToken] = useState(localStorage.getItem("token"));

  const [authMode, setAuthMode] = useState("login");

  const [fullName, setFullName] = useState("");
  const [registerEmail, setRegisterEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [registerPassword, setRegisterPassword] = useState("");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [otpEmail, setOtpEmail] = useState("");
  const [otp, setOtp] = useState("");

  const [loginLoading, setLoginLoading] = useState(false);
  const [registerLoading, setRegisterLoading] = useState(false);
  const [otpLoading, setOtpLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);

  const [authMessage, setAuthMessage] = useState("");
  const [authError, setAuthError] = useState("");

  // =========================================================
  // DASHBOARD STATE
  // =========================================================

  const [analytics, setAnalytics] = useState(null);
  const [fraudAnalysis, setFraudAnalysis] = useState(null);
  const [alerts, setAlerts] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // =========================================================
  // TRANSACTION STATE
  // =========================================================

  const [amount, setAmount] = useState("");
  const [transactionType, setTransactionType] = useState("Purchase");
  const [merchant, setMerchant] = useState("");
  const [location, setLocation] = useState("");

  const [transactionLoading, setTransactionLoading] = useState(false);
  const [transactionResult, setTransactionResult] = useState(null);
  const [transactionError, setTransactionError] = useState("");

  // =========================================================
  // AXIOS API
  // =========================================================

  const getApi = () => {
    const savedToken = localStorage.getItem("token");

    return axios.create({
      baseURL: API_URL,
      headers: {
        Accept: "application/json",
        ...(savedToken
          ? {
              Authorization: `Bearer ${savedToken}`,
            }
          : {}),
      },
    });
  };

  // =========================================================
  // REGISTER
  // =========================================================

  const handleRegister = async (e) => {
    e.preventDefault();

    try {
      setRegisterLoading(true);
      setAuthError("");
      setAuthMessage("");

      const response = await axios.post(`${API_URL}/auth/register`, {
        full_name: fullName,
        email: registerEmail,
        phone: phone,
        password: registerPassword,
      });

      setAuthMessage(
        response.data?.message ||
          "Registration successful. OTP verify karo."
      );

      setOtpEmail(registerEmail);

      setFullName("");
      setPhone("");
      setRegisterPassword("");

      setAuthMode("verify");
    } catch (err) {
      console.error("Register Error:", err);

      setAuthError(
        err.response?.data?.detail ||
          "Registration failed. Details check karo."
      );
    } finally {
      setRegisterLoading(false);
    }
  };

  // =========================================================
  // VERIFY OTP
  // =========================================================

  const handleVerifyOTP = async (e) => {
    e.preventDefault();

    try {
      setOtpLoading(true);
      setAuthError("");
      setAuthMessage("");

      const response = await axios.post(
        `${API_URL}/auth/verify-otp`,
        {
          email: otpEmail,
          otp: otp,
        }
      );

      setAuthMessage(
        response.data?.message ||
          "OTP verified successfully. Ab login karo."
      );

      setOtp("");
      setEmail(otpEmail);

      setTimeout(() => {
        setAuthMode("login");
      }, 800);
    } catch (err) {
      console.error("OTP Error:", err);

      setAuthError(
        err.response?.data?.detail ||
          "OTP verification failed."
      );
    } finally {
      setOtpLoading(false);
    }
  };

  // =========================================================
  // RESEND OTP
  // FIXED: backend expects email as query parameter
  // =========================================================

  const handleResendOTP = async () => {
    if (!otpEmail) {
      setAuthError("Pehle email enter karo.");
      return;
    }

    try {
      setResendLoading(true);
      setAuthError("");
      setAuthMessage("");

      const response = await axios.post(
        `${API_URL}/auth/resend-otp?email=${encodeURIComponent(
          otpEmail
        )}`
      );

      setAuthMessage(
        response.data?.message ||
          "OTP dobara send kar diya gaya hai."
      );
    } catch (err) {
      console.error("Resend OTP Error:", err);

      setAuthError(
        err.response?.data?.detail ||
          "OTP resend nahi ho paya."
      );
    } finally {
      setResendLoading(false);
    }
  };

  // =========================================================
  // LOGIN
  // =========================================================

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      setLoginLoading(true);
      setAuthError("");
      setAuthMessage("");

      const formData = new URLSearchParams();

      formData.append("grant_type", "password");
      formData.append("username", email);
      formData.append("password", password);
      formData.append("scope", "");
      formData.append("client_id", "");
      formData.append("client_secret", "");

      const response = await axios.post(
        `${API_URL}/auth/login`,
        formData,
        {
          headers: {
            "Content-Type":
              "application/x-www-form-urlencoded",
            Accept: "application/json",
          },
        }
      );

      const accessToken =
        response.data?.access_token;

      if (!accessToken) {
        setAuthError(
          "Login failed: Access token nahi mila."
        );
        return;
      }

      localStorage.setItem("token", accessToken);
      setToken(accessToken);

      setEmail("");
      setPassword("");
      setAuthError("");
    } catch (err) {
      console.error("Login Error:", err);

      setAuthError(
        err.response?.data?.detail ||
          "Invalid email or password."
      );
    } finally {
      setLoginLoading(false);
    }
  };

  // =========================================================
  // LOGOUT
  // =========================================================

  const handleLogout = () => {
    localStorage.removeItem("token");

    setToken(null);

    setAnalytics(null);
    setFraudAnalysis(null);
    setAlerts(null);

    setTransactionResult(null);

    setError("");
    setAuthError("");
    setAuthMessage("");

    setAuthMode("login");
  };

  // =========================================================
  // DASHBOARD
  // =========================================================

  const loadDashboard = async () => {
    const savedToken = localStorage.getItem("token");

    if (!savedToken) {
      setToken(null);
      return;
    }

    try {
      setLoading(true);
      setError("");

      const api = getApi();

      const [
        analyticsResponse,
        fraudResponse,
        alertsResponse,
      ] = await Promise.all([
        api.get("/dashboard/analytics"),
        api.get("/dashboard/fraud-analysis"),
        api.get("/transactions/fraud-alerts"),
      ]);

      setAnalytics(analyticsResponse.data);
      setFraudAnalysis(fraudResponse.data);
      setAlerts(alertsResponse.data);
    } catch (err) {
      console.error("Dashboard Error:", err);

      if (err.response?.status === 401) {
        localStorage.removeItem("token");
        setToken(null);

        setAnalytics(null);
        setFraudAnalysis(null);
        setAlerts(null);

        setAuthError(
          "Session expire ho gaya. Please dobara login karo."
        );

        return;
      }

      setError(
        err.response?.data?.detail ||
          "Dashboard data load nahi ho pa raha."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // ADD TRANSACTION
  // =========================================================

  const handleTransaction = async (e) => {
    e.preventDefault();

    try {
      setTransactionLoading(true);
      setTransactionError("");
      setTransactionResult(null);

      if (!amount || Number(amount) <= 0) {
        setTransactionError(
          "Valid transaction amount enter karo."
        );
        return;
      }

      if (!merchant.trim()) {
        setTransactionError(
          "Merchant name enter karo."
        );
        return;
      }

      if (!location.trim()) {
        setTransactionError(
          "Transaction location enter karo."
        );
        return;
      }

      const api = getApi();

      const response = await api.post(
        "/transactions/",
        {
          amount: Number(amount),
          transaction_type: transactionType,
          merchant: merchant.trim(),
          location: location.trim(),
        }
      );

      setTransactionResult(response.data);

      setAmount("");
      setMerchant("");
      setLocation("");

      // Dashboard numbers + alerts automatically update
      await loadDashboard();
    } catch (err) {
      console.error("Transaction Error:", err);

      if (err.response?.status === 401) {
        localStorage.removeItem("token");
        setToken(null);

        setTransactionError(
          "Session expire ho gaya. Dobara login karo."
        );
        return;
      }

      setTransactionError(
        err.response?.data?.detail ||
          "Transaction submit nahi ho paayi."
      );
    } finally {
      setTransactionLoading(false);
    }
  };

  // =========================================================
  // LOAD DASHBOARD AFTER LOGIN
  // =========================================================

  useEffect(() => {
    if (token) {
      loadDashboard();
    }
  }, [token]);

  // =========================================================
  // MONEY FORMAT
  // =========================================================

  const formatMoney = (value) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(Number(value) || 0);
  };

  // =========================================================
  // AUTH SCREEN
  // =========================================================

  if (!token) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          background: "#f4f7fb",
          padding: "20px",
          boxSizing: "border-box",
        }}
      >
        <div
          style={{
            width: "100%",
            maxWidth: "450px",
            background: "white",
            padding: "35px",
            borderRadius: "18px",
            boxShadow:
              "0 10px 35px rgba(0,0,0,0.12)",
            boxSizing: "border-box",
          }}
        >
          {/* LOGO */}

          <div
            style={{
              textAlign: "center",
              marginBottom: "25px",
            }}
          >
            <div style={{ fontSize: "50px" }}>
              🛡️
            </div>

            <h1
              style={{
                margin: "10px 0 5px",
                fontSize: "28px",
                color: "#111827",
              }}
            >
              FraudShield-AI
            </h1>

            <p
              style={{
                color: "#666",
                margin: 0,
              }}
            >
              AI-Powered Fraud Detection
            </p>
          </div>

          {/* ERROR */}

          {authError && (
            <div
              style={{
                background: "#ffe8e8",
                color: "#c62828",
                padding: "12px",
                borderRadius: "8px",
                marginBottom: "15px",
              }}
            >
              ⚠️ {authError}
            </div>
          )}

          {/* SUCCESS */}

          {authMessage && (
            <div
              style={{
                background: "#e8f8ee",
                color: "#16733c",
                padding: "12px",
                borderRadius: "8px",
                marginBottom: "15px",
              }}
            >
              ✅ {authMessage}
            </div>
          )}

          {/* =================================================
              LOGIN
          ================================================= */}

          {authMode === "login" && (
            <>
              <h2>🔐 Login</h2>

              <form onSubmit={handleLogin}>
                <label>Email</label>

                <input
                  type="email"
                  placeholder="Enter registered email"
                  value={email}
                  onChange={(e) =>
                    setEmail(e.target.value)
                  }
                  required
                  style={inputStyle}
                />

                <label>Password</label>

                <input
                  type="password"
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) =>
                    setPassword(e.target.value)
                  }
                  required
                  style={inputStyle}
                />

                <button
                  type="submit"
                  disabled={loginLoading}
                  style={primaryButton}
                >
                  {loginLoading
                    ? "Logging in..."
                    : "🔐 Login"}
                </button>
              </form>

              <button
                onClick={() => {
                  setAuthMode("register");
                  setAuthError("");
                  setAuthMessage("");
                }}
                style={secondaryButton}
              >
                📝 Create New Account
              </button>

              <button
                onClick={() => {
                  setAuthMode("verify");
                  setAuthError("");
                  setAuthMessage("");
                }}
                style={linkButton}
              >
                📧 Already registered? Verify OTP
              </button>
            </>
          )}

          {/* =================================================
              REGISTER
          ================================================= */}

          {authMode === "register" && (
            <>
              <h2>📝 Create Account</h2>

              <form onSubmit={handleRegister}>
                <label>Full Name</label>

                <input
                  type="text"
                  placeholder="Enter full name"
                  value={fullName}
                  onChange={(e) =>
                    setFullName(e.target.value)
                  }
                  required
                  style={inputStyle}
                />

                <label>Email</label>

                <input
                  type="email"
                  placeholder="Enter email"
                  value={registerEmail}
                  onChange={(e) =>
                    setRegisterEmail(e.target.value)
                  }
                  required
                  style={inputStyle}
                />

                <label>Phone</label>

                <input
                  type="tel"
                  placeholder="Enter phone number"
                  value={phone}
                  onChange={(e) =>
                    setPhone(e.target.value)
                  }
                  required
                  style={inputStyle}
                />

                <label>Password</label>

                <input
                  type="password"
                  placeholder="Create password"
                  value={registerPassword}
                  onChange={(e) =>
                    setRegisterPassword(e.target.value)
                  }
                  required
                  style={inputStyle}
                />

                <button
                  type="submit"
                  disabled={registerLoading}
                  style={primaryButton}
                >
                  {registerLoading
                    ? "Creating Account..."
                    : "📝 Register"}
                </button>
              </form>

              <button
                onClick={() => {
                  setAuthMode("login");
                  setAuthError("");
                  setAuthMessage("");
                }}
                style={secondaryButton}
              >
                ← Back to Login
              </button>
            </>
          )}

          {/* =================================================
              VERIFY OTP
          ================================================= */}

          {authMode === "verify" && (
            <>
              <h2>📧 Verify OTP</h2>

              <p
                style={{
                  color: "#666",
                  lineHeight: "1.5",
                }}
              >
                Registered email aur OTP enter karo.
              </p>

              <form onSubmit={handleVerifyOTP}>
                <label>Email</label>

                <input
                  type="email"
                  placeholder="Enter registered email"
                  value={otpEmail}
                  onChange={(e) =>
                    setOtpEmail(e.target.value)
                  }
                  required
                  style={inputStyle}
                />

                <label>OTP</label>

                <input
                  type="text"
                  placeholder="Enter OTP"
                  value={otp}
                  onChange={(e) =>
                    setOtp(e.target.value)
                  }
                  required
                  maxLength={6}
                  style={inputStyle}
                />

                <button
                  type="submit"
                  disabled={otpLoading}
                  style={primaryButton}
                >
                  {otpLoading
                    ? "Verifying..."
                    : "✅ Verify OTP"}
                </button>
              </form>

              <button
                onClick={handleResendOTP}
                disabled={resendLoading}
                style={secondaryButton}
              >
                {resendLoading
                  ? "Sending..."
                  : "🔄 Resend OTP"}
              </button>

              <button
                onClick={() => {
                  setAuthMode("login");
                  setAuthError("");
                  setAuthMessage("");
                }}
                style={linkButton}
              >
                ← Back to Login
              </button>
            </>
          )}
        </div>
      </div>
    );
  }

  // =========================================================
  // LOADING
  // =========================================================

  if (loading && !analytics) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          fontSize: "20px",
          background: "#f4f7fb",
        }}
      >
        🛡️ Loading FraudShield-AI...
      </div>
    );
  }

  // =========================================================
  // DASHBOARD
  // =========================================================

  return (
    <div className="dashboard">
      {/* HEADER */}

      <header className="header">
        <div>
          <h1>🛡️ FraudShield-AI</h1>

          <p>
            AI-Powered Fraud Detection Dashboard
          </p>
        </div>

        <div
          style={{
            display: "flex",
            gap: "10px",
            alignItems: "center",
          }}
        >
          <button
            className="refresh-btn"
            onClick={loadDashboard}
            disabled={loading}
          >
            {loading
              ? "⏳ Refreshing..."
              : "🔄 Refresh"}
          </button>

          <button
            onClick={handleLogout}
            style={{
              padding: "10px 16px",
              border: "none",
              borderRadius: "8px",
              background: "#dc2626",
              color: "white",
              cursor: "pointer",
            }}
          >
            🚪 Logout
          </button>
        </div>
      </header>

      {/* ERROR */}

      {error && (
        <div className="error-box">
          ⚠️ {error}
        </div>
      )}

      {/* =====================================================
          ADD TRANSACTION
      ===================================================== */}

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>💳 New Transaction</h2>

            <p>
              Transaction enter karo aur AI fraud
              detection result dekho.
            </p>
          </div>
        </div>

        <form onSubmit={handleTransaction}>
          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(220px, 1fr))",
              gap: "15px",
              padding: "20px",
            }}
          >
            {/* AMOUNT */}

            <div>
              <label
                style={{
                  display: "block",
                  marginBottom: "7px",
                  fontWeight: "600",
                }}
              >
                Amount (₹)
              </label>

              <input
                type="number"
                min="1"
                placeholder="Enter amount"
                value={amount}
                onChange={(e) =>
                  setAmount(e.target.value)
                }
                required
                style={inputStyle}
              />
            </div>

            {/* TYPE */}

            <div>
              <label
                style={{
                  display: "block",
                  marginBottom: "7px",
                  fontWeight: "600",
                }}
              >
                Transaction Type
              </label>

              <select
                value={transactionType}
                onChange={(e) =>
                  setTransactionType(e.target.value)
                }
                style={inputStyle}
              >
                <option value="Purchase">
                  Purchase
                </option>
                <option value="Transfer">
                  Transfer
                </option>
                <option value="Withdrawal">
                  Withdrawal
                </option>
                <option value="Payment">
                  Payment
                </option>
                <option value="Deposit">
                  Deposit
                </option>
              </select>
            </div>

            {/* MERCHANT */}

            <div>
              <label
                style={{
                  display: "block",
                  marginBottom: "7px",
                  fontWeight: "600",
                }}
              >
                Merchant
              </label>

              <input
                type="text"
                placeholder="Amazon / Flipkart / etc."
                value={merchant}
                onChange={(e) =>
                  setMerchant(e.target.value)
                }
                required
                style={inputStyle}
              />
            </div>

            {/* LOCATION */}

            <div>
              <label
                style={{
                  display: "block",
                  marginBottom: "7px",
                  fontWeight: "600",
                }}
              >
                Location
              </label>

              <input
                type="text"
                placeholder="Delhi / Noida / Agra..."
                value={location}
                onChange={(e) =>
                  setLocation(e.target.value)
                }
                required
                style={inputStyle}
              />
            </div>
          </div>

          {transactionError && (
            <div
              style={{
                margin: "0 20px 15px",
                padding: "12px",
                borderRadius: "8px",
                background: "#ffe8e8",
                color: "#c62828",
              }}
            >
              ⚠️ {transactionError}
            </div>
          )}

          <div style={{ padding: "0 20px 20px" }}>
            <button
              type="submit"
              disabled={transactionLoading}
              style={{
                ...primaryButton,
                maxWidth: "300px",
              }}
            >
              {transactionLoading
                ? "🔍 Checking Transaction..."
                : "🛡️ Submit & Check Fraud"}
            </button>
          </div>
        </form>
      </section>

      {/* =====================================================
          TRANSACTION RESULT
      ===================================================== */}

      {transactionResult && (
        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>
                {transactionResult.fraud_status ===
                "Fraud"
                  ? "🚨 Fraud Detected"
                  : "✅ Transaction Result"}
              </h2>

              <p>
                Latest transaction analysis
              </p>
            </div>
          </div>

          <div
            style={{
              padding: "20px",
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(180px, 1fr))",
              gap: "15px",
            }}
          >
            <div className="info-card">
              <p>Transaction ID</p>

              <h2>
                #
                {transactionResult.id ||
                  transactionResult.transaction_id ||
                  "-"}
              </h2>
            </div>

            <div className="info-card">
              <p>Amount</p>

              <h2>
                {formatMoney(
                  transactionResult.amount
                )}
              </h2>
            </div>

            <div className="info-card">
              <p>Risk Score</p>

              <h2>
                {transactionResult.risk_score ?? 0}
                /100
              </h2>
            </div>

            <div className="info-card">
              <p>Status</p>

              <h2>
                {transactionResult.fraud_status ||
                  transactionResult.status ||
                  "Unknown"}
              </h2>
            </div>
          </div>

          {transactionResult.fraud_reason && (
            <div
              style={{
                margin: "0 20px 20px",
                padding: "15px",
                borderRadius: "10px",
                background: "#fff4e5",
              }}
            >
              <strong>🚨 Fraud Reason:</strong>

              <p>
                {transactionResult.fraud_reason}
              </p>
            </div>
          )}

          {transactionResult.fraud_alert && (
            <div
              style={{
                margin: "0 20px 20px",
                padding: "15px",
                borderRadius: "10px",
                background: "#ffe8e8",
                color: "#b91c1c",
              }}
            >
              ⚠️ {transactionResult.fraud_alert}
            </div>
          )}

          {transactionResult.is_blocked !==
            undefined && (
            <div
              style={{
                padding: "0 20px 20px",
                fontWeight: "700",
              }}
            >
              {transactionResult.is_blocked
                ? "🔒 Transaction BLOCKED"
                : "✅ Transaction Allowed"}
            </div>
          )}
        </section>
      )}

      {/* =====================================================
          ANALYTICS
      ===================================================== */}

      {analytics && (
        <>
          <section className="stats-grid">
            <div className="stat-card blue">
              <span className="stat-icon">
                💳
              </span>

              <div>
                <p>Total Transactions</p>

                <h2>
                  {analytics.total_transactions ||
                    0}
                </h2>
              </div>
            </div>

            <div className="stat-card red">
              <span className="stat-icon">
                🚨
              </span>

              <div>
                <p>Fraud Transactions</p>

                <h2>
                  {analytics.fraud_transactions ||
                    0}
                </h2>
              </div>
            </div>

            <div className="stat-card green">
              <span className="stat-icon">
                ✅
              </span>

              <div>
                <p>Safe Transactions</p>

                <h2>
                  {analytics.safe_transactions ||
                    0}
                </h2>
              </div>
            </div>

            <div className="stat-card orange">
              <span className="stat-icon">
                🔒
              </span>

              <div>
                <p>Blocked Transactions</p>

                <h2>
                  {analytics.blocked_transactions ||
                    0}
                </h2>
              </div>
            </div>
          </section>

          {/* MONEY */}

          <section className="stats-grid">
            <div className="info-card">
              <p>Total Amount</p>

              <h2>
                {formatMoney(
                  analytics.total_amount
                )}
              </h2>
            </div>

            <div className="info-card fraud-money">
              <p>Fraud Amount</p>

              <h2>
                {formatMoney(
                  analytics.fraud_amount
                )}
              </h2>
            </div>

            <div className="info-card safe-money">
              <p>Safe Amount</p>

              <h2>
                {formatMoney(
                  analytics.safe_amount
                )}
              </h2>
            </div>

            <div className="info-card risk">
              <p>Average Risk Score</p>

              <h2>
                {analytics.average_risk_score ||
                  0}
              </h2>

              <div className="risk-bar">
                <div
                  className="risk-fill"
                  style={{
                    width: `${Math.min(
                      analytics.average_risk_score ||
                        0,
                      100
                    )}%`,
                  }}
                />
              </div>
            </div>
          </section>
        </>
      )}

      {/* =====================================================
          MERCHANT ANALYSIS
      ===================================================== */}

      {fraudAnalysis?.merchant_analysis && (
        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>
                🏪 Merchant Risk Analysis
              </h2>

              <p>
                Transaction fraud analysis by
                merchant
              </p>
            </div>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Merchant</th>
                  <th>Total</th>
                  <th>Fraud</th>
                  <th>Safe</th>
                  <th>Total Amount</th>
                  <th>Fraud Amount</th>
                  <th>Risk</th>
                </tr>
              </thead>

              <tbody>
                {Object.entries(
                  fraudAnalysis.merchant_analysis
                ).map(([merchantName, data]) => {
                  const fraudRate =
                    data.total_transactions > 0
                      ? (data.fraud_transactions /
                          data.total_transactions) *
                        100
                      : 0;

                  return (
                    <tr key={merchantName}>
                      <td>
                        <strong>
                          {merchantName}
                        </strong>
                      </td>

                      <td>
                        {data.total_transactions}
                      </td>

                      <td className="danger-text">
                        {data.fraud_transactions}
                      </td>

                      <td className="success-text">
                        {data.safe_transactions}
                      </td>

                      <td>
                        {formatMoney(
                          data.total_amount
                        )}
                      </td>

                      <td className="danger-text">
                        {formatMoney(
                          data.fraud_amount
                        )}
                      </td>

                      <td>
                        <span
                          className={
                            fraudRate >= 50
                              ? "badge danger"
                              : fraudRate > 0
                              ? "badge warning"
                              : "badge safe"
                          }
                        >
                          {fraudRate.toFixed(0)}%
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* =====================================================
          LOCATION ANALYSIS
      ===================================================== */}

      {fraudAnalysis?.location_analysis && (
        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>
                📍 Location Risk Analysis
              </h2>

              <p>
                Fraud detection by transaction
                location
              </p>
            </div>
          </div>

          <div className="location-grid">
            {Object.entries(
              fraudAnalysis.location_analysis
            ).map(([locationName, data]) => {
              const fraudRate =
                data.total_transactions > 0
                  ? (data.fraud_transactions /
                      data.total_transactions) *
                    100
                  : 0;

              return (
                <div
                  className="location-card"
                  key={locationName}
                >
                  <div className="location-top">
                    <h3>
                      📍 {locationName}
                    </h3>

                    <span
                      className={
                        fraudRate >= 50
                          ? "badge danger"
                          : fraudRate > 0
                          ? "badge warning"
                          : "badge safe"
                      }
                    >
                      {fraudRate.toFixed(0)}%
                      Fraud
                    </span>
                  </div>

                  <div className="location-stats">
                    <div>
                      <span>Total</span>

                      <strong>
                        {data.total_transactions}
                      </strong>
                    </div>

                    <div>
                      <span>Fraud</span>

                      <strong className="danger-text">
                        {data.fraud_transactions}
                      </strong>
                    </div>

                    <div>
                      <span>Safe</span>

                      <strong className="success-text">
                        {data.safe_transactions}
                      </strong>
                    </div>
                  </div>

                  <div className="amount-row">
                    <span>Total</span>

                    <strong>
                      {formatMoney(
                        data.total_amount
                      )}
                    </strong>
                  </div>

                  <div className="amount-row">
                    <span>Fraud Amount</span>

                    <strong className="danger-text">
                      {formatMoney(
                        data.fraud_amount
                      )}
                    </strong>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* =====================================================
          FRAUD ALERTS
      ===================================================== */}

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>🚨 Fraud Alerts</h2>

            <p>
              Suspicious transactions requiring
              attention
            </p>
          </div>

          <span className="alert-count">
            {alerts?.total_alerts || 0} Alerts
          </span>
        </div>

        {alerts?.alerts?.length > 0 ? (
          <div className="alerts-list">
            {alerts.alerts.map((alert) => (
              <div
                className="alert-card"
                key={alert.transaction_id}
              >
                <div className="alert-icon">
                  🚨
                </div>

                <div className="alert-content">
                  <div className="alert-title">
                    <h3>
                      Transaction #
                      {alert.transaction_id}
                    </h3>

                    <span
                      className={
                        alert.fraud_status ===
                        "Fraud"
                          ? "badge danger"
                          : "badge warning"
                      }
                    >
                      {alert.fraud_status}
                    </span>
                  </div>

                  <p>
                    <strong>
                      Merchant:
                    </strong>{" "}
                    {alert.merchant}
                  </p>

                  <p>
                    <strong>
                      Location:
                    </strong>{" "}
                    {alert.location}
                  </p>

                  <p>
                    <strong>
                      Amount:
                    </strong>{" "}
                    {formatMoney(alert.amount)}
                  </p>

                  <p>
                    <strong>
                      Risk Score:
                    </strong>{" "}
                    {alert.risk_score}/100
                  </p>

                  <p className="alert-reason">
                    <strong>
                      Reason:
                    </strong>{" "}
                    {alert.fraud_reason}
                  </p>

                  <p className="alert-message">
                    ⚠️ {alert.fraud_alert}
                  </p>
                </div>

                <div className="alert-status">
                  {alert.is_blocked ? (
                    <span className="blocked">
                      🔒 BLOCKED
                    </span>
                  ) : (
                    <span className="verification">
                      🔐 VERIFICATION
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-alerts">
            <div>✅</div>

            <h3>No Fraud Alerts</h3>

            <p>
              Currently there are no suspicious
              transactions.
            </p>
          </div>
        )}
      </section>

      {/* FOOTER */}

      <footer>
        <p>
          🛡️ FraudShield-AI • AI-Powered
          Financial Fraud Detection System
        </p>
      </footer>
    </div>
  );
}

// =========================================================
// COMMON STYLES
// =========================================================

const inputStyle = {
  width: "100%",
  padding: "13px",
  marginBottom: "16px",
  border: "1px solid #ccc",
  borderRadius: "8px",
  boxSizing: "border-box",
  fontSize: "15px",
};

const primaryButton = {
  width: "100%",
  padding: "14px",
  border: "none",
  borderRadius: "8px",
  background: "#2563eb",
  color: "white",
  fontSize: "16px",
  fontWeight: "600",
  cursor: "pointer",
  marginTop: "5px",
};

const secondaryButton = {
  width: "100%",
  padding: "12px",
  border: "1px solid #2563eb",
  borderRadius: "8px",
  background: "white",
  color: "#2563eb",
  fontSize: "15px",
  fontWeight: "600",
  cursor: "pointer",
  marginTop: "12px",
};

const linkButton = {
  width: "100%",
  padding: "10px",
  border: "none",
  background: "transparent",
  color: "#2563eb",
  fontSize: "14px",
  cursor: "pointer",
  marginTop: "8px",
};

export default App;