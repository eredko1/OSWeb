// Standalone server for self-hosting / local testing:  PROXY_SECRET=... node proxy/server.js  (PORT defaults to 8787)
const http = require('http');
const { handle } = require('./lib');
http.createServer((req, res) => handle(req, res)).listen(process.env.PORT || 8787, () => console.log('OSWeb proxy listening on', process.env.PORT || 8787));
