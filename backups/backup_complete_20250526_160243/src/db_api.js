
// API para conectar con Neon DB
const express = require('express');
const cors = require('cors');
const db = require('./db_neon');

// Crear aplicación Express
const app = express();

// Middleware
app.use(express.json());
app.use(cors());

// Ruta de estado
app.get('/health', async (req, res) => {
  try {
    const dbStatus = await db.testConnection();
    res.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      env: process.env.NODE_ENV,
      database: dbStatus
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: error.message
    });
  }
});

// Ruta para obtener usuarios
app.get('/api/users', async (req, res) => {
  try {
    const result = await db.query('SELECT * FROM users LIMIT 10', []);
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: error.message
    });
  }
});

// Ruta para obtener tablas de la base de datos
app.get('/api/tables', async (req, res) => {
  try {
    const result = await db.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public'
    `, []);
    
    res.json(result.rows.map(row => row.table_name));
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: error.message
    });
  }
});

// Iniciar servidor si no es importado
if (require.main === module) {
  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => {
    console.log(`Servidor escuchando en puerto ${PORT}`);
  });
}

// Exportar app para Vercel
module.exports = { app };
