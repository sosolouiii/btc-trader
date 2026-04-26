const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(__dirname, 'trades.db');
let db;

function initDB() {
  db = new sqlite3.Database(dbPath);
  db.run(`
    CREATE TABLE IF NOT EXISTS trades (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      symbol TEXT,
      side TEXT,
      amount REAL,
      entryPrice REAL,
      sl REAL,
      tp REAL,
      message TEXT,
      status TEXT,
      pnl REAL DEFAULT 0,
      createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
}

function logTrade(trade) {
  const { symbol, side, amount, entryPrice, sl, tp, message, status, pnl } = trade;
  db.run(
    `INSERT INTO trades (symbol, side, amount, entryPrice, sl, tp, message, status, pnl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [symbol, side, amount, entryPrice, sl, tp, message, status, pnl],
    (err) => {
      if (err) console.error('DB insert error:', err.message);
    }
  );
}

function getTrades(limit = 100) {
  return new Promise((resolve, reject) => {
    db.all(`SELECT * FROM trades ORDER BY createdAt DESC LIMIT ?`, [limit], (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

function getStats() {
  return new Promise((resolve, reject) => {
    db.get(`
      SELECT 
        COUNT(*) as totalTrades,
        SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses,
        SUM(pnl) as totalPnl
      FROM trades
    `, (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

function getTodayLoss() {
  return new Promise((resolve, reject) => {
    db.get(`
      SELECT COALESCE(SUM(CASE WHEN pnl < 0 THEN ABS(pnl) ELSE 0 END), 0) as loss
      FROM trades
      WHERE DATE(createdAt) = DATE('now')
    `, (err, row) => {
      if (err) reject(err);
      else resolve(row?.loss || 0);
    });
  });
}

module.exports = { initDB, logTrade, getTrades, getStats, getTodayLoss };
