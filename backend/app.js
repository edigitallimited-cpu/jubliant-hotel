const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
import mongoose from 'mongoose';
import dotenv from 'dotenv';
const bookingRoutes = require('./routes/bookingRoutes');
const reviewRoutes = require('./routes/reviewRoutes');

dotenv.config();
const app = express();

const dbConnection = mongoose.connect(process.env.DB_CONNECTION_STRING, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

dbConnection
  .then(() => console.log('Connected to MongoDB'))
  .catch((error) => console.error('Error connecting to MongoDB:', error));
app.use(bodyParser.json());

app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  next();
});      

// Serve static files from the 'static' directory
app.use(express.static(path.join(__dirname, '../static')));


app.use((req, res) => {
  res.status(404);
  res.send(`<h1>Error 404: Resource Not Found</h1>`);
});


// Connect to the database
// const database = require('./utils/database');
// const db = database.getDB();

// Define your routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../static', 'index.html'));
});

app.use('/book', bookingRoutes);
app.use('/review', reviewRoutes);

// Start the server
app.listen(3000, () => {
  console.log('Server is running on port 3000');
});