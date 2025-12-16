const fs = require('fs');
// Import trực tiếp kiểu cũ (Chuẩn cho v9.1.0)
const gplay = require('google-play-scraper');

// --- CONFIG ---
const mode = process.argv[2]; 
const target = process.argv[3];
const targetCountry = process.argv[4] || 'vn';
const targetToken = process.argv[5];
const targetLang = targetCountry === 'vn' ? 'vi' : 'en';

// ... (Phần code logic bên dưới giữ nguyên) ...

// --- MAIN ROUTER ---
async function main() {
    switch (mode) {
        case 'LIST': await scrapeCategoryList(); break;
        case 'DETAIL': await scrapeAppDetail(); break;
        case 'MORE_REVIEWS': await scrapeMoreReviews(); break;
        case 'SEARCH': await scrapeSearch(); break;       // MỚI
        case 'SIMILAR': await scrapeSimilar(); break;     // MỚI
        case 'DEVELOPER': await scrapeDeveloper(); break; // MỚI
        default: 
            console.error("❌ Mode không hợp lệ"); 
            process.exit(1);
    }
}

// === 1. SOI CHI TIẾT (KÈM PERMISSIONS) ===
async function scrapeAppDetail() {
    console.log(`🚀 Detail: '${target}'...`);
    try {
        const appDetails = await gplay.app({ appId: target, lang: targetLang, country: targetCountry });
        
        // Lấy Review
        try {
            const reviewsResult = await gplay.reviews({
                appId: target, sort: gplay.sort.NEWEST, num: 40, lang: targetLang, country: targetCountry
            });
            appDetails.comments = reviewsResult.data || [];
            appDetails.nextToken = reviewsResult.nextPaginationToken || null;
        } catch (err) {}

        // Lấy Permissions (Quyền) - MỚI
        try {
            const perms = await gplay.permissions({ appId: target, lang: targetLang, short: true });
            appDetails.permissions = perms;
        } catch (err) {}

        saveJSON('app_detail.json', appDetails);
    } catch (e) { handleError(e); }
}

// === 2. TÌM KIẾM TỪ KHÓA (SEARCH) ===
async function scrapeSearch() {
    console.log(`🚀 Search: '${target}'...`);
    try {
        const results = await gplay.search({ term: target, num: 20, country: targetCountry, lang: targetLang });
        saveJSON('search_results.json', results);
    } catch (e) { handleError(e); }
}

// === 3. TÌM APP TƯƠNG TỰ (SIMILAR) ===
async function scrapeSimilar() {
    console.log(`🚀 Similar: '${target}'...`);
    try {
        const results = await gplay.similar({ appId: target, lang: targetLang, country: targetCountry });
        saveJSON('similar_apps.json', results);
    } catch (e) { handleError(e); }
}

// === 4. TÌM APP CÙNG DEV (DEVELOPER) ===
async function scrapeDeveloper() {
    console.log(`🚀 Dev Apps: '${target}'...`); // target ở đây là Dev ID
    try {
        const results = await gplay.developer({ devId: target, lang: targetLang, country: targetCountry, num: 20 });
        saveJSON('developer_apps.json', results);
    } catch (e) { handleError(e); }
}

// === 5. LOAD MORE REVIEWS ===
async function scrapeMoreReviews() {
    try {
        const reviewsResult = await gplay.reviews({
            appId: target, sort: gplay.sort.NEWEST, num: 40, lang: targetLang, country: targetCountry,
            nextPaginationToken: targetToken
        });
        saveJSON('more_reviews.json', { comments: reviewsResult.data || [], nextToken: reviewsResult.nextPaginationToken });
    } catch (e) { handleError(e); }
}

// === 6. TOP CHART LIST ===
async function scrapeCategoryList() {
    console.log(`🚀 Chart: '${target}'...`);
    let allApps = [];
    try {
        const fetch = async (c) => { try { return await gplay.list({ category: target, collection: c, num: 20, country: targetCountry, lang: targetLang }); } catch(e){return[]} };
        const [free, paid, gross] = await Promise.all([
            fetch(gplay.collection.TOP_FREE || 'top_free'),
            fetch(gplay.collection.TOP_PAID || 'top_paid'),
            fetch(gplay.collection.GROSSING || 'grossing')
        ]);
        
        const push = (l, t) => l?.forEach((a, i) => allApps.push({...a, category: target, country: targetCountry, collection_type: t, rank: i+1, icon: a.icon||""}));
        push(free, 'top_free'); push(paid, 'top_paid'); push(gross, 'top_grossing');
        
        saveJSON('raw_data.json', allApps);
    } catch (e) { handleError(e); }
}

//Helpers
function saveJSON(file, data) {
    if (!fs.existsSync('data')) fs.mkdirSync('data');
    fs.writeFileSync(`data/${file}`, JSON.stringify(data, null, 2));
    console.log(`✅ OK: ${file}`);
}
function handleError(e) { console.error(`❌ Error: ${e.message}`); process.exit(1); }

main();