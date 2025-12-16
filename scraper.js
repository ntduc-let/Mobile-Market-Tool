// --- 1. POLYFILL FIX NODE 18 (BẮT BUỘC) ---
try {
    if (typeof File === 'undefined') {
        const { Blob } = require('buffer');
        global.File = class File extends Blob {
            constructor(fileBits, fileName, options) {
                super(fileBits, options);
                this.name = fileName;
                this.lastModified = options?.lastModified || Date.now();
            }
        };
    }
} catch (e) {}

const fs = require('fs');

// --- 2. IMPORT THƯ VIỆN ---
let gplay;
try {
    try { gplay = require('google-play-scraper'); } 
    catch { import('google-play-scraper').then(m => gplay = m.default); }
} catch (e) { process.exit(1); }

// --- 3. CONFIG ---
const mode = process.argv[2]; 
const target = process.argv[3];
const targetCountry = process.argv[4] || 'vn';
const targetToken = process.argv[5];
const targetLang = targetCountry === 'vn' ? 'vi' : 'en';

// --- MAIN ROUTER ---
async function main() {
    if (!gplay) {
        try { gplay = (await import('google-play-scraper')).default; } 
        catch (e) { console.error("Lib Error"); process.exit(1); }
    }

    try {
        switch (mode) {
            case 'LIST': await scrapeCategoryList(); break;
            case 'DETAIL': await scrapeAppDetail(); break;
            case 'MORE_REVIEWS': await scrapeMoreReviews(); break;
            case 'SEARCH': await scrapeSearch(); break;
            case 'SIMILAR': await scrapeSimilar(); break;
            case 'DEVELOPER': await scrapeDeveloper(); break;
            
            // --- CÁC TÍNH NĂNG MỚI BỔ SUNG ---
            case 'SUGGEST': await scrapeSuggest(); break;       // Gợi ý từ khóa
            case 'DATASAFETY': await scrapeDataSafety(); break; // An toàn dữ liệu
            case 'PERMISSIONS': await scrapePermissions(); break; // Quyền truy cập (riêng lẻ)
            case 'CATEGORIES': await scrapeCategories(); break; // Danh sách danh mục
            
            default: 
                console.error("Unknown Mode"); process.exit(1);
        }
    } catch (e) { handleError(e); }
}

// === CÁC HÀM XỬ LÝ ===

// 1. APP DETAIL (UPDATE: Thêm Data Safety)
async function scrapeAppDetail() {
    const d = await gplay.app({ appId: target, lang: targetLang, country: targetCountry });
    
    // Reviews
    try {
        const reviews = await gplay.reviews({ appId: target, sort: gplay.sort.NEWEST, num: 40, lang: targetLang, country: targetCountry });
        d.comments = reviews.data || [];
        d.nextToken = reviews.nextPaginationToken;
    } catch (e) { d.comments = []; }
    
    // Permissions
    try {
        const perms = await gplay.permissions({ appId: target, lang: targetLang, short: true });
        d.permissions = perms;
    } catch (e) {}

    // [NEW] Data Safety (Tích hợp luôn vào Detail)
    try {
        const ds = await gplay.datasafety({ appId: target, lang: targetLang, country: targetCountry });
        d.dataSafety = ds;
    } catch (e) {}

    saveJSON('app_detail.json', d);
}

// 2. SUGGEST (Gợi ý từ khóa)
async function scrapeSuggest() {
    const s = await gplay.suggest({ term: target });
    saveJSON('suggest_results.json', s);
}

// 3. DATA SAFETY (Chạy riêng lẻ nếu cần)
async function scrapeDataSafety() {
    const s = await gplay.datasafety({ appId: target, lang: targetLang, country: targetCountry });
    saveJSON('datasafety.json', s);
}

// 4. PERMISSIONS (Chạy riêng lẻ nếu cần)
async function scrapePermissions() {
    const s = await gplay.permissions({ appId: target, lang: targetLang, short: false }); // short: false để lấy full mô tả
    saveJSON('permissions.json', s);
}

// 5. CATEGORIES (Lấy danh sách category chuẩn từ Google)
async function scrapeCategories() {
    const s = await gplay.categories();
    saveJSON('all_categories.json', s);
}

// ... (Các hàm cũ giữ nguyên) ...
async function scrapeSearch() {
    const s = await gplay.search({ term: target, num: 20, country: targetCountry, lang: targetLang });
    saveJSON('search_results.json', s);
}
async function scrapeSimilar() {
    const s = await gplay.similar({ appId: target, lang: targetLang, country: targetCountry });
    saveJSON('similar_apps.json', s);
}
async function scrapeDeveloper() {
    const s = await gplay.developer({ devId: target, lang: targetLang, country: targetCountry, num: 20 });
    saveJSON('developer_apps.json', s);
}
async function scrapeMoreReviews() {
    try {
        if (!targetToken) throw new Error("No Token");
        const r = await gplay.reviews({ appId: target, sort: gplay.sort.NEWEST, num: 40, lang: targetLang, country: targetCountry, nextPaginationToken: targetToken });
        saveJSON('more_reviews.json', { comments: r.data || [], nextToken: r.nextPaginationToken });
    } catch (e) { saveJSON('more_reviews.json', { error: e.message }); }
}
async function scrapeCategoryList() {
    let allApps = [];
    const fetch = async (c) => { try { return await gplay.list({ category: target, collection: c, num: 20, country: targetCountry, lang: targetLang }); } catch(e){return[]} };
    const [free, paid, gross] = await Promise.all([ fetch(gplay.collection.TOP_FREE), fetch(gplay.collection.TOP_PAID), fetch(gplay.collection.GROSSING) ]);
    const push = (l, t) => l?.forEach((a, i) => allApps.push({...a, category: target, country: targetCountry, collection_type: t, rank: i+1, icon: a.icon||""}));
    push(free, 'top_free'); push(paid, 'top_paid'); push(gross, 'top_grossing');
    saveJSON('raw_data.json', allApps);
}

// Helpers
function saveJSON(file, data) {
    if (!fs.existsSync('data')) fs.mkdirSync('data');
    fs.writeFileSync(`data/${file}`, JSON.stringify(data, null, 2));
}
function handleError(e) { console.error(`ERR: ${e.message}`); process.exit(1); }

main();