const { MongoClient } = require('mongodb');

const uri = 'mongodb+srv://jubilantlandhotelloungebarspa_db_user:Juba73812@@@jubilanthotel.dybd1xl.mongodb.net/jubilant_hotel?retryWrites=true&w=majority';

const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });

async function getDB() {
  try {
    await client.connect();
    return client.db('jubilant_hotel');
  } catch (error) {
    console.error('Error connecting to MongoDB:', error);
    return null;
  }
}

module.exports = { getDB };