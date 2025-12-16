// --- 1. POLYFILL FIX NODE 18 (QUAN TRỌNG) ---
// Đoạn này vá lỗi "ReferenceError: File is not defined"
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
// Import thư viện (Bản v10 tự động detect CommonJS)
const gplay = require('google-play-scraper');

// --- 2. CONFIG ---
const mode = process.argv[2]; 
const target = process.argv[3];
const targetCountry = process.argv[4] || 'vn';
const targetToken = process.argv[5];
const targetLang = targetCountry === 'vn' ? 'vi' : 'en';

async function main() {
    try {
        if (mode === 'LIST') {
            console.log(`Scraping List: ${target} in ${targetCountry}`);
            
            // Hàm lấy list an toàn
            const fetchList = async (collection) => {
                try {
                    return await gplay.list({
                        category: target,
                        collection: collection,
                        num: 20,
                        country: targetCountry,
                        lang: targetLang
                    });
                } catch (e) { 
                    // console.error(`Error fetching ${collection}:`, e.message);
                    return []; 
                }
            };

            // v10 sử dụng gplay.collection.TOP_FREE (các biến hằng số)
            const [free, paid, gross] = await Promise.all([
                fetchList(gplay.collection.TOP_FREE),
                fetchList(gplay.collection.TOP_PAID),
                fetchList(gplay.collection.GROSSING)
            ]);

            let allApps = [];
            const push = (l, t) => l?.forEach((a, i) => allApps.push({
                ...a, 
                category: target, 
                country: targetCountry, 
                collection_type: t, 
                rank: i+1,
                // v10 đôi khi trả về icon dạng mảng hoặc object, ta lấy string
                icon: a.icon || "" 
            }));

            push(free, 'top_free');
            push(paid, 'top_paid');
            push(gross, 'top_grossing');
            
            console.log(`Found ${allApps.length} apps.`);
            fs.writeFileSync('data/raw_data.json', JSON.stringify(allApps));

        } else if (mode === 'DETAIL') {
            const d = await gplay.app({ appId: target, lang: targetLang, country: targetCountry });
            
            // Lấy reviews
            try {
                const reviews = await gplay.reviews({
                    appId: target, sort: gplay.sort.NEWEST, num: 40, lang: targetLang, country: targetCountry
                });
                d.comments = reviews.data || [];
                d.nextToken = reviews.nextPaginationToken;
            } catch (e) { d.comments = []; }
            
            // Lấy permissions (v10 hỗ trợ tốt)
            try {
                const perms = await gplay.permissions({ appId: target, lang: targetLang, short: true });
                d.permissions = perms;
            } catch (e) {}

            fs.writeFileSync('data/app_detail.json', JSON.stringify(d));
        
        } else if (mode === 'SEARCH') {
            const s = await gplay.search({ term: target, num: 20, country: targetCountry, lang: targetLang });
            fs.writeFileSync('data/search_results.json', JSON.stringify(s));
        
        } else if (mode === 'SIMILAR') {
             const s = await gplay.similar({ appId: target, lang: targetLang, country: targetCountry });
             fs.writeFileSync('data/similar_apps.json', JSON.stringify(s));
             
        } else if (mode === 'DEVELOPER') {
             const s = await gplay.developer({ devId: target, lang: targetLang, country: targetCountry, num: 20 });
             fs.writeFileSync('data/developer_apps.json', JSON.stringify(s));
        }

    } catch (e) {
        console.error("FATAL ERROR:", e.message);
        process.exit(1);
    }
}

main();