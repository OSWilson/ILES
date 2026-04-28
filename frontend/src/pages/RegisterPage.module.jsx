.page {
  min-height: 100vh;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card {
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 36px 32px;
  width: 100%;
  max-width: 480px;
}

.title {
  font-size: 22px;
  font-weight: 700;
  color: #2563eb;
  text-align: center;
  margin-bottom: 4px;
}

.subtitle {
  font-size: 13px;
  color: #9ca3af;
  text-align: center;
  margin-bottom: 24px;
}

.grid2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 14px;
}

.label { font-size: 13px; color: #6b7280; }

.input {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 9px 12px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  width: 100%;
}
.input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.select {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 9px 12px;
  font-size: 14px;
  outline: none;
  background: #fff;
  width: 100%;
}
.select:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.submit {
  width: 100%;
  background: #2563eb;
  color: #ffffff;
  padding: 10px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  margin-top: 8px;
  transition: background 0.15s;
}
.submit:hover { background: #1d4ed8; }
.submit:disabled { opacity: 0.5; cursor: not-allowed; }

.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 14px;
}

.success {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #15803d;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 14px;
}

.loginLink {
  text-align: center;
  font-size: 13px;
  color: #9ca3af;
  margin-top: 16px;
}

.loginLink a {
  color: #2563eb;
  font-weight: 500;
}
.loginLink a:hover { text-decoration: underline; }