// dev-server.js
const express = require('express');
const app = express();
// Import routes
//require('./_routes')(app);   // <-- or whatever you do to include your API endpoints and middleware
app.set('port', 5002);
app.listen(app.get('port'), function() {
    console.log('Node App Started');
});
