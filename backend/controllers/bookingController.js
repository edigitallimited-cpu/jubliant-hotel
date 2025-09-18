const bookingModel = require('../models/bookingModel');

async function createBooking(req, res) {
  try {
    const data = req.body;
    // Perform booking logic here
    const booking = await bookingModel.createBooking(data);
    res.json({ message: 'Booking successful' });
  } catch (error) {
    console.error('Error creating booking:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
}

module.exports = { createBooking };