const fs = require('fs');
// Import bản 8.0.0
const gplay = require('google-play-scraper');

const mode = process.argv[2]; 
const target = process.argv[3];
const targetCountry = process.argv[4] || 'vn';
const targetLang = targetCountry === 'vn' ? 'vi' : 'en';

async function main() {
    try {
        if (mode === 'LIST') {
            console.log("Scraping List...");
            // Hàm helper để tránh lỗi nếu 1 danh sách bị trống
            const safeList = async (collection) => {
                try {
                    return await gplay.list({
                        category: target,
                        collection: collection,
                        num: 20,
                        country: targetCountry,
                        lang: targetLang
                    });
                } catch (e) { return []; }
            };

            // v8.0.0 dùng string cho collection
            const [free, paid, gross] = await Promise.all([
                safeList(gplay.collection.TOP_FREE),
                safeList(gplay.collection.TOP_PAID),
                safeList(gplay.collection.GROSSING)
            ]);

            let allApps = [];
            const push = (list, type) => {
                if(list && Array.isArray(list)) {
                    list.forEach((app, index) => {
                        allApps.push({
                            ...app,
                            category: target,
                            country: targetCountry,
                            collection_type: type,
                            rank: index + 1
                        });
                    });
                }
            };

            push(free, 'top_free');
            push(paid, 'top_paid');
            push(gross, 'top_grossing');

            fs.writeFileSync('data/raw_data.json', JSON.stringify(allApps));

        } else if (mode === 'DETAIL') {
            console.log("Scraping Detail...");
            const d = await gplay.app({ appId: target, lang: targetLang, country: targetCountry });
            
            // Lấy comment riêng (nếu lỗi thì bỏ qua)
            try {
                const reviews = await gplay.reviews({
                    appId: target, sort: gplay.sort.NEWEST, num: 40, lang: targetLang, country: targetCountry
                });
                d.comments = reviews.data || [];
            } catch (e) { d.comments = []; }

            fs.writeFileSync('data/app_detail.json', JSON.stringify(d));

        } else if (mode === 'SEARCH') {
            console.log("Scraping Search...");
            const s = await gplay.search({ term: target, num: 20, country: targetCountry, lang: targetLang });
            fs.writeFileSync('data/search_results.json', JSON.stringify(s));
        }
    } catch (e) {
        // Ghi lỗi ra file để Python đọc được nếu cần
        console.error("FATAL JS ERROR:", e.message);
        process.exit(1);
    }
}

main();