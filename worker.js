// worker.js
const gplay = require('google-play-scraper');

// Lấy tham số (appId) từ dòng lệnh do Python truyền vào
// Ví dụ: node worker.js com.facebook.katana
const appId = process.argv[2]; 

if (!appId) {
    console.error(JSON.stringify({ error: "Thieu appId" }));
    process.exit(1);
}

gplay.app({ appId: appId })
    .then(result => {
        // QUAN TRỌNG: Chỉ in ra JSON kết quả cuối cùng để Python đọc
        console.log(JSON.stringify(result));
    })
    .catch(err => {
        // In lỗi dạng JSON để Python bắt được
        console.log(JSON.stringify({ error: err.message }));
    });