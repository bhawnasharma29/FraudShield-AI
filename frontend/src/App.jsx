import { useEffect, useState } from "react";
import axios from "axios";
import "./index.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));

  const [analytics, setAnalytics] = useState(null);
  const [fraudAnalysis, setFraudAnalysis] = useState(null);
  const [alerts, setAlerts] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);

  // ==========================================
  // LOGIN
  // ==========================================

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      setLoginLoading(true);
      setError("");

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
            "Content-Type": "application/x-www-form-urlencoded",
            Accept: "application/json",
          },
        }
      );

      const accessToken = response.data.access_token;

      if (!accessToken) {
        setError("Login failed: Access token nahi mila.");
        return;
      }

      // Save JWT
      localStorage.setItem("token", accessToken);

      // Update state
      setToken(accessToken);

      setEmail("");
      setPassword("");
      setError("");

    } catch (err) {
      console.error("Login Error:", err);

      if (err.response) {
        setError(
          `Login Error: ${err.response.data?.detail ||
          "Invalid email or password"
          }`
        );
      } else {
        setError(
          "Backend se connection nahi ho pa raha. Check karo FastAPI server running hai ya nahi."
        );
      }
    } finally {
      setLoginLoading(false);
    }
  };

  // ==========================================
  // LOGOUT
  // ==========================================

  const handleLogout = () => {
    localStorage.removeItem("token");

    setToken(null);

    setAnalytics(null);
    setFraudAnalysis(null);
    setAlerts(null);

    setError("");
  };

  // ==========================================
  // DASHBOARD API
  // ==========================================

  const loadDashboard = async () => {
    const savedToken = localStorage.getItem("token");

    if (!savedToken) {
      setToken(null);
      return;
    }

    try {
      setLoading(true);
      setError("");

      const api = axios.create({
        baseURL: API_URL,
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${savedToken}`,
        },
      });

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

        setError(
          "Session expire ho gaya. Please dobara login karo."
        );

        return;
      }

      if (err.response) {
        setError(
          `Backend Error: ${err.response.data?.detail ||
          "Request failed"
          }`
        );
      } else {
        setError(
          "Backend se connection nahi ho pa raha. Check karo FastAPI server running hai ya nahi."
        );
      }

    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // LOAD DASHBOARD AFTER LOGIN
  // ==========================================

  useEffect(() => {
    if (token) {
      loadDashboard();
    }
  }, [token]);

  // ==========================================
  // MONEY FORMAT
  // ==========================================

  const formatMoney = (amount) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount || 0);
  };

  // ==========================================
  // LOGIN SCREEN
  // ==========================================

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
            maxWidth: "420px",
            background: "white",
            padding: "35px",
            borderRadius: "18px",
            boxShadow: "0 10px 35px rgba(0,0,0,0.12)",
            boxSizing: "border-box",
          }}
        >
          {/* LOGO */}

          <div
            style={{
              textAlign: "center",
              marginBottom: "30px",
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
              AI-Powered Fraud Detection Dashboard
            </p>
          </div>

          {/* ERROR */}

          {error && (
            <div
              style={{
                background: "#ffe8e8",
                color: "#c62828",
                padding: "12px",
                borderRadius: "8px",
                marginBottom: "18px",
                lineHeight: "1.4",
              }}
            >
              ⚠️ {error}
            </div>
          )}

          {/* LOGIN FORM */}

          <form onSubmit={handleLogin}>

            {/* EMAIL */}

            <label
              style={{
                display: "block",
                marginBottom: "7px",
                fontWeight: "600",
              }}
            >
              Email
            </label>

            <input
              type="email"
              placeholder="Enter your registered email"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
              required
              style={{
                width: "100%",
                padding: "13px",
                marginBottom: "18px",
                border: "1px solid #ccc",
                borderRadius: "8px",
                boxSizing: "border-box",
                fontSize: "15px",
              }}
            />

            {/* PASSWORD */}

            <label
              style={{
                display: "block",
                marginBottom: "7px",
                fontWeight: "600",
              }}
            >
              Password
            </label>

            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              required
              style={{
                width: "100%",
                padding: "13px",
                marginBottom: "22px",
                border: "1px solid #ccc",
                borderRadius: "8px",
                boxSizing: "border-box",
                fontSize: "15px",
              }}
            />

            {/* LOGIN BUTTON */}

            <button
              type="submit"
              disabled={loginLoading}
              style={{
                width: "100%",
                padding: "14px",
                border: "none",
                borderRadius: "8px",
                background: loginLoading
                  ? "#93b4f5"
                  : "#2563eb",
                color: "white",
                fontSize: "16px",
                fontWeight: "600",
                cursor: loginLoading
                  ? "not-allowed"
                  : "pointer",
              }}
            >
              {loginLoading
                ? "Logging in..."
                : "🔐 Login"}
            </button>

          </form>
        </div>
      </div>
    );
  }

  // ==========================================
  // LOADING
  // ==========================================

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

  // ==========================================
  // DASHBOARD
  // ==========================================

  return (
    <div className="dashboard">

      {/* ======================================
          HEADER
      ====================================== */}

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

          {/* REFRESH */}

          <button
            className="refresh-btn"
            onClick={loadDashboard}
            disabled={loading}
          >
            {loading
              ? "⏳ Refreshing..."
              : "🔄 Refresh"}
          </button>

          {/* LOGOUT */}

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
            Logout
          </button>

        </div>
      </header>

      {/* ======================================
          ERROR
      ====================================== */}

      {error && (
        <div className="error-box">
          ⚠️ {error}
        </div>
      )}

      {/* ======================================
          ANALYTICS
      ====================================== */}

      {analytics && (
        <>
          <section className="stats-grid">

            {/* TOTAL TRANSACTIONS */}

            <div className="stat-card blue">

              <span className="stat-icon">
                💳
              </span>

              <div>
                <p>Total Transactions</p>

                <h2>
                  {analytics.total_transactions || 0}
                </h2>
              </div>

            </div>

            {/* FRAUD */}

            <div className="stat-card red">

              <span className="stat-icon">
                🚨
              </span>

              <div>
                <p>Fraud Transactions</p>

                <h2>
                  {analytics.fraud_transactions || 0}
                </h2>
              </div>

            </div>

            {/* SAFE */}

            <div className="stat-card green">

              <span className="stat-icon">
                ✅
              </span>

              <div>
                <p>Safe Transactions</p>

                <h2>
                  {analytics.safe_transactions || 0}
                </h2>
              </div>

            </div>

            {/* BLOCKED */}

            <div className="stat-card orange">

              <span className="stat-icon">
                🔒
              </span>

              <div>
                <p>Blocked Transactions</p>

                <h2>
                  {analytics.blocked_transactions || 0}
                </h2>
              </div>

            </div>

          </section>

          {/* MONEY STATS */}

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
                {analytics.average_risk_score || 0}
              </h2>

              <div className="risk-bar">

                <div
                  className="risk-fill"
                  style={{
                    width: `${Math.min(
                      analytics.average_risk_score || 0,
                      100
                    )}%`,
                  }}
                />

              </div>

            </div>

          </section>
        </>
      )}

      {/* ======================================
          MERCHANT ANALYSIS
      ====================================== */}

      {fraudAnalysis?.merchant_analysis && (
        <section className="panel">

          <div className="panel-header">

            <div>

              <h2>
                🏪 Merchant Risk Analysis
              </h2>

              <p>
                Transaction fraud analysis by merchant
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
                ).map(
                  ([merchant, data]) => {

                    const fraudRate =
                      data.total_transactions > 0
                        ? (
                          data.fraud_transactions /
                          data.total_transactions
                        ) * 100
                        : 0;

                    return (
                      <tr key={merchant}>

                        <td>
                          <strong>
                            {merchant}
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
                  }
                )}

              </tbody>

            </table>

          </div>

        </section>
      )}

      {/* ======================================
          LOCATION ANALYSIS
      ====================================== */}

      {fraudAnalysis?.location_analysis && (
        <section className="panel">

          <div className="panel-header">

            <div>

              <h2>
                📍 Location Risk Analysis
              </h2>

              <p>
                Fraud detection by transaction location
              </p>

            </div>

          </div>

          <div className="location-grid">

            {Object.entries(
              fraudAnalysis.location_analysis
            ).map(
              ([location, data]) => {

                const fraudRate =
                  data.total_transactions > 0
                    ? (
                      data.fraud_transactions /
                      data.total_transactions
                    ) * 100
                    : 0;

                return (
                  <div
                    className="location-card"
                    key={location}
                  >

                    <div className="location-top">

                      <h3>
                        📍 {location}
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
                        {fraudRate.toFixed(0)}% Fraud
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

                      <span>
                        Fraud Amount
                      </span>

                      <strong className="danger-text">
                        {formatMoney(
                          data.fraud_amount
                        )}
                      </strong>

                    </div>

                  </div>
                );
              }
            )}

          </div>

        </section>
      )}

      {/* ======================================
          FRAUD ALERTS
      ====================================== */}

      <section className="panel">

        <div className="panel-header">

          <div>

            <h2>
              🚨 Fraud Alerts
            </h2>

            <p>
              Suspicious transactions requiring attention
            </p>

          </div>

          <span className="alert-count">
            {alerts?.total_alerts || 0} Alerts
          </span>

        </div>

        {/* ALERTS EXIST */}

        {alerts?.alerts?.length > 0 ? (

          <div className="alerts-list">

            {alerts.alerts.map(
              (alert) => (

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
                      {formatMoney(
                        alert.amount
                      )}
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

                      ⚠️{" "}
                      {alert.fraud_alert}

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
              )
            )}

          </div>

        ) : (

          /* NO ALERTS */

          <div className="no-alerts">

            <div>✅</div>

            <h3>
              No Fraud Alerts
            </h3>

            <p>
              Currently there are no suspicious transactions.
            </p>

          </div>

        )}

      </section>

      {/* ======================================
          FOOTER
      ====================================== */}

      <footer>

        <p>
          🛡️ FraudShield-AI • AI-Powered
          Financial Fraud Detection System
        </p>

      </footer>

    </div>
  );
}

export default App;