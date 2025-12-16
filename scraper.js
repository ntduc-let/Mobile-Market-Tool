// --- 1. POLYFILL FIX NODE 18 (BẮT BUỘC ĐỂ TRÁNH LỖI FILE API) ---
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
} catch (e) {
    console.warn("Polyfill warning:", e.message);
}

const fs = require('fs');

// --- 2. CONFIG ---
const mode = process.argv[2]; 
const target = process.argv[3];
const targetCountry = process.argv[4] || 'vn';
const targetToken = process.argv[5];
const targetLang = targetCountry === 'vn' ? 'vi' : 'en';

let gplay;

// --- 3. MAIN ROUTER ---
async function main() {
    try {
        const gplayModule = await import('google-play-scraper');
        gplay = gplayModule.default;

        // [UPDATE] Đã bổ sung MORE_REVIEWS vào router
        if (mode === 'LIST') {
            await scrapeCategoryList();
        } else if (mode === 'DETAIL') {
            await scrapeAppDetail();
        } else if (mode === 'SEARCH') {
            await scrapeSearch();
        } else if (mode === 'SIMILAR') {
             await scrapeSimilar();
        } else if (mode === 'DEVELOPER') {
             await scrapeDeveloper();
        } else if (mode === 'MORE_REVIEWS') {
             await scrapeMoreReviews();
        }

    } catch (e) {
        console.error("FATAL ERROR:", e.message);
        process.exit(1);
    }
}

// --- CÁC HÀM XỬ LÝ LOGIC ---

async function scrapeCategoryList() {
    console.log(`Scraping List: ${target} in ${targetCountry}`);
    const fetchList = async (collection) => {
        try {
            return await gplay.list({
                category: target, collection: collection, num: 20, country: targetCountry, lang: targetLang
            });
        } catch (e) { return []; }
    };

    const [free, paid, gross] = await Promise.all([
        fetchList(gplay.collection.TOP_FREE),
        fetchList(gplay.collection.TOP_PAID),
        fetchList(gplay.collection.GROSSING)
    ]);

    let allApps = [];
    const push = (l, t) => l?.forEach((a, i) => allApps.push({
        ...a, category: target, country: targetCountry, collection_type: t, rank: i+1, icon: a.icon || "" 
    }));

    push(free, 'top_free');
    push(paid, 'top_paid');
    push(gross, 'top_grossing');
    
    fs.writeFileSync('data/raw_data.json', JSON.stringify(allApps));
}

async function scrapeAppDetail() {
    // 1. Lấy thông tin cơ bản
    const d = await gplay.app({ appId: target, lang: targetLang, country: targetCountry });
    
    // 2. Lấy thêm Reviews (vì mặc định trả về ít)
    try {
        const reviews = await gplay.reviews({
            appId: target, sort: gplay.sort.NEWEST, num: 40, lang: targetLang, country: targetCountry
        });
        d.comments = reviews.data || [];
        d.nextToken = reviews.nextPaginationToken;
    } catch (e) { d.comments = []; }
    
    // 3. Lấy Permissions (ngắn gọn)
    try {
        const perms = await gplay.permissions({ appId: target, lang: targetLang, short: true });
        d.permissions = perms;
    } catch (e) {}

    // [UPDATE] 4. Lấy Data Safety (Quan trọng cho Full Features)
    try {
        const safety = await gplay.datasafety({ appId: target, lang: targetLang, country: targetCountry });
        d.dataSafety = safety;
    } catch (e) { 
        d.dataSafety = { sharedData: [], collectedData: [] }; // Fallback
    }

    fs.writeFileSync('data/app_detail.json', JSON.stringify(d));
}

async function scrapeSearch() {
    const s = await gplay.search({ term: target, num: 20, country: targetCountry, lang: targetLang });
    fs.writeFileSync('data/search_results.json', JSON.stringify(s));
}

async function scrapeSimilar() {
    const s = await gplay.similar({ appId: target, lang: targetLang, country: targetCountry });
    fs.writeFileSync('data/similar_apps.json', JSON.stringify(s));
}

async function scrapeDeveloper() {
    const s = await gplay.developer({ devId: target, lang: targetLang, country: targetCountry, num: 20 });
    fs.writeFileSync('data/developer_apps.json', JSON.stringify(s));
}

async function scrapeMoreReviews() {
    console.log(`🚀 More Reviews: Token length ${targetToken ? targetToken.length : 0}`);
    try {
        if (!targetToken) throw new Error("Token phân trang bị rỗng (Undefined)");

        const reviewsResult = await gplay.reviews({
            appId: target, sort: gplay.sort.NEWEST, num: 40, lang: targetLang, country: targetCountry, nextPaginationToken: targetToken
        });

        const output = { comments: reviewsResult.data || [], nextToken: reviewsResult.nextPaginationToken };
        fs.writeFileSync('data/more_reviews.json', JSON.stringify(output));

    } catch (e) { 
        console.error(`⚠️ Lỗi tải review: ${e.message}`);
        fs.writeFileSync('data/more_reviews.json', JSON.stringify({ comments: [], nextToken: null, error: e.message }));
    }
}

main();