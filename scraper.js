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
    // Thử load dynamic import (cho bản mới) hoặc require thường
    try {
        gplay = require('google-play-scraper');
    } catch {
        import('google-play-scraper').then(m => gplay = m.default);
    }
} catch (e) {
    // Fallback nếu lỗi
    console.error("Library Error");
    process.exit(1);
}

// --- 3. CONFIG ---
const mode = process.argv[2]; 
const target = process.argv[3];
const targetCountry = process.argv[4] || 'vn';
const targetToken = process.argv[5];
const targetLang = targetCountry === 'vn' ? 'vi' : 'en';

// --- MAIN ROUTER ---
async function main() {
    // Đợi import xong (nếu là dynamic)
    if (!gplay) {
        try { gplay = (await import('google-play-scraper')).default; } 
        catch (e) { console.error("Cannot load lib"); process.exit(1); }
    }

    try {
        switch (mode) {
            case 'LIST': await scrapeCategoryList(); break;
            case 'DETAIL': await scrapeAppDetail(); break;
            case 'MORE_REVIEWS': await scrapeMoreReviews(); break; // <--- ĐÃ SỬA
            case 'SEARCH': await scrapeSearch(); break;
            case 'SIMILAR': await scrapeSimilar(); break;
            case 'DEVELOPER': await scrapeDeveloper(); break;
            default: 
                console.error("Unknown Mode"); 
                process.exit(1);
        }
    } catch (e) {
        handleError(e);
    }
}

// === CÁC HÀM XỬ LÝ ===

// 1. TẢI THÊM REVIEW (ĐÃ FIX CRASH)
async function scrapeMoreReviews() {
    console.log(`🚀 More Reviews...`);
    try {
        if (!targetToken) throw new Error("Token rỗng");

        const reviewsResult = await gplay.reviews({
            appId: target, 
            sort: gplay.sort.NEWEST, 
            num: 40, 
            lang: targetLang, 
            country: targetCountry,
            nextPaginationToken: targetToken
        });

        saveJSON('more_reviews.json', { 
            comments: reviewsResult.data || [], 
            nextToken: reviewsResult.nextPaginationToken 
        });

    } catch (e) {
        console.error(`⚠️ Soft Error: ${e.message}`);
        // QUAN TRỌNG: Không exit(1). Lưu kết quả lỗi để Python đọc và xử lý.
        saveJSON('more_reviews.json', { 
            comments: [], 
            nextToken: null, 
            error: e.message // Gửi kèm thông báo lỗi
        });
    }
}

async function scrapeAppDetail() {
    const d = await gplay.app({ appId: target, lang: targetLang, country: targetCountry });
    try {
        const reviews = await gplay.reviews({ appId: target, sort: gplay.sort.NEWEST, num: 40, lang: targetLang, country: targetCountry });
        d.comments = reviews.data || [];
        d.nextToken = reviews.nextPaginationToken;
    } catch (e) { d.comments = []; }
    
    try {
        const perms = await gplay.permissions({ appId: target, lang: targetLang, short: true });
        d.permissions = perms;
    } catch (e) {}

    saveJSON('app_detail.json', d);
}

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

async function scrapeCategoryList() {
    let allApps = [];
    const fetch = async (c) => { try { return await gplay.list({ category: target, collection: c, num: 20, country: targetCountry, lang: targetLang }); } catch(e){return[]} };
    const [free, paid, gross] = await Promise.all([
        fetch(gplay.collection.TOP_FREE || 'top_free'),
        fetch(gplay.collection.TOP_PAID || 'top_paid'),
        fetch(gplay.collection.GROSSING || 'grossing')
    ]);
    const push = (l, t) => l?.forEach((a, i) => allApps.push({...a, category: target, country: targetCountry, collection_type: t, rank: i+1, icon: a.icon||""}));
    push(free, 'top_free'); push(paid, 'top_paid'); push(gross, 'top_grossing');
    saveJSON('raw_data.json', allApps);
}

// Helpers
function saveJSON(file, data) {
    if (!fs.existsSync('data')) fs.mkdirSync('data');
    fs.writeFileSync(`data/${file}`, JSON.stringify(data, null, 2));
}

function handleError(e) { 
    console.error(`FATAL: ${e.message}`); 
    process.exit(1); 
}

main();