cd server
start "BitBot Server" cmd /k "node index.js"
cd ../dashboard
npm start
pause