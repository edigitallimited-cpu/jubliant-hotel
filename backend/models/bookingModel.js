// const { MongoClient } = require('mongodb');

// const uri = 'mongodb+srv://jubilantlandhotelloungebarspa_db_user:Juba73812@@@jubilanthotel.dybd1xl.mongodb.net/jubilant_hotel?retryWrites=true&w=majority';

// const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });

async function createBooking(data) {
  try {
    await client.connect();
    const db = client.db('jubilant_hotel');
    const bookingsCollection = db.collection('bookings');
    const booking = {
      name: data.name,
      email: data.email,
      phone: data.phone,
      room: data.room,
      price: data.price,
      checkin: data.checkin,
      checkout: data.checkin
    };
    const result = await bookingsCollection.insertOne(booking);
    return result;
  } catch (error) {
    console.error('Error creating booking:', error);
    throw error;
  } finally {
    await client.close();
  }
}