const fs = require('fs');
// [QUAN TRỌNG] Import trực tiếp cho bản 9.1.0
const gplay = require('google-play-scraper');

// --- CONFIG ---
// Command: node scraper.js <MODE> <ID/TERM> <COUNTRY> <TOKEN (Optional)>
const mode = process.argv[2]; 
const target = process.argv[3]; // Category, AppID, hoặc Search Term
const targetCountry = process.argv[4] || 'vn';
const targetToken = process.argv[5];
const targetLang = targetCountry === 'vn' ? 'vi' : 'en';

// --- MAIN ROUTER ---
async function main() {
    try {
        switch (mode) {
            case 'LIST': await scrapeCategoryList(); break;
            case 'DETAIL': await scrapeAppDetail(); break;
            case 'MORE_REVIEWS': await scrapeMoreReviews(); break;
            case 'SEARCH': await scrapeSearch(); break;
            case 'SIMILAR': await scrapeSimilar(); break;
            case 'DEVELOPER': await scrapeDeveloper(); break;
            default: 
                console.error("❌ Mode không hợp lệ"); 
                process.exit(1);
        }
    } catch (e) {
        handleError(e);
    }
}

// === CÁC HÀM XỬ LÝ ===

async function scrapeAppDetail() {
    // console.log(`🚀 Detail: '${target}'...`);
    const appDetails = await gplay.app({ appId: target, lang: targetLang, country: targetCountry });
    
    try {
        const reviewsResult = await gplay.reviews({
            appId: target, sort: gplay.sort.NEWEST, num: 40, lang: targetLang, country: targetCountry
        });
        appDetails.comments = reviewsResult.data || [];
        appDetails.nextToken = reviewsResult.nextPaginationToken || null;
    } catch (err) {}

    try {
        const perms = await gplay.permissions({ appId: target, lang: targetLang, short: true });
        appDetails.permissions = perms;
    } catch (err) {}

    saveJSON('app_detail.json', appDetails);
}

async function scrapeSearch() {
    // console.log(`🚀 Search: '${target}'...`);
    const results = await gplay.search({ term: target, num: 20, country: targetCountry, lang: targetLang });
    saveJSON('search_results.json', results);
}

async function scrapeSimilar() {
    // console.log(`🚀 Similar: '${target}'...`);
    const results = await gplay.similar({ appId: target, lang: targetLang, country: targetCountry });
    saveJSON('similar_apps.json', results);
}

async function scrapeDeveloper() {
    // console.log(`🚀 Dev: '${target}'...`);
    const results = await gplay.developer({ devId: target, lang: targetLang, country: targetCountry, num: 20 });
    saveJSON('developer_apps.json', results);
}

async function scrapeMoreReviews() {
    const reviewsResult = await gplay.reviews({
        appId: target, sort: gplay.sort.NEWEST, num: 40, lang: targetLang, country: targetCountry,
        nextPaginationToken: targetToken
    });
    saveJSON('more_reviews.json', { comments: reviewsResult.data || [], nextToken: reviewsResult.nextPaginationToken });
}

async function scrapeCategoryList() {
    // console.log(`🚀 Chart: '${target}'...`);
    let allApps = [];
    const fetch = async (c) => { 
        try { return await gplay.list({ category: target, collection: c, num: 20, country: targetCountry, lang: targetLang }); } 
        catch(e){ return [] } 
    };
    
    // Lưu ý: v9.1.0 dùng gplay.collection.TOP_FREE (viết hoa)
    const [free, paid, gross] = await Promise.all([
        fetch(gplay.collection.TOP_FREE || 'top_free'),
        fetch(gplay.collection.TOP_PAID || 'top_paid'),
        fetch(gplay.collection.GROSSING || 'grossing')
    ]);
    
    const push = (l, t) => l?.forEach((a, i) => allApps.push({...a, category: target, country: targetCountry, collection_type: t, rank: i+1, icon: a.icon||""}));
    push(free, 'top_free'); push(paid, 'top_paid'); push(gross, 'top_grossing');
    
    saveJSON('raw_data.json', allApps);
}

//Helpers
function saveJSON(file, data) {
    if (!fs.existsSync('data')) fs.mkdirSync('data');
    fs.writeFileSync(`data/${file}`, JSON.stringify(data, null, 2));
    // console.log(`✅ OK: ${file}`);
}

function handleError(e) { 
    console.error(`ERROR_JSON_START{"error": "${e.message}"}ERROR_JSON_END`); 
    process.exit(1); 
}

main();