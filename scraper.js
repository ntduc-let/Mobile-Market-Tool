const gplay = require('google-play-scraper');

// Lấy tham số từ dòng lệnh (Python truyền vào)
const args = process.argv.slice(2);
const mode = args[0];       // DETAIL, LIST, SEARCH...
const target = args[1];     // App ID, Category, Term...
const country = args[2] || 'us';
const token = args[3];      // Token cho trang tiếp theo (nếu có)

const lang = (country === 'vn') ? 'vi' : 'en';

async function main() {
    try {
        let result;
        
        if (mode === 'DETAIL') {
            result = await gplay.app({ appId: target, lang: lang, country: country });
            // Lấy thêm review
            const reviews = await gplay.reviews({ appId: target, lang: lang, country: country, sort: gplay.sort.NEWEST, num: 40 });
            result.comments = reviews.data;
            result.nextToken = reviews.nextPaginationToken;
        } 
        else if (mode === 'SEARCH') {
            result = await gplay.search({ term: target, lang: lang, country: country, num: 20 });
        }
        else if (mode === 'LIST') {
            // Map category string sang constant của thư viện nếu cần, hoặc dùng bộ sưu tập
            // Ở đây dùng collection cơ bản
            const collectionMap = {
                'GAME_ACTION': gplay.category.GAME_ACTION,
                // ... (Các category khác map tương tự, hoặc truyền trực tiếp nếu lib hỗ trợ)
            };
            
            // Chạy 3 luồng lấy Top Free, Paid, Grossing
            const [free, paid, grossing] = await Promise.all([
                gplay.list({ category: target !== 'ALL' ? target : undefined, collection: gplay.collection.TOP_FREE, lang: lang, country: country, num: 20 }),
                gplay.list({ category: target !== 'ALL' ? target : undefined, collection: gplay.collection.TOP_PAID, lang: lang, country: country, num: 20 }),
                gplay.list({ category: target !== 'ALL' ? target : undefined, collection: gplay.collection.TOP_GROSSING, lang: lang, country: country, num: 20 })
            ]);
            
            // Gán nhãn để Python xử lý
            free.forEach(i => i.collection_type = 'top_free');
            paid.forEach(i => i.collection_type = 'top_paid');
            grossing.forEach(i => i.collection_type = 'top_grossing');
            
            result = [...free, ...paid, ...grossing];
        }
        else if (mode === 'SIMILAR') {
            result = await gplay.similar({ appId: target, lang: lang, country: country, num: 20 });
        }
        else if (mode === 'DEVELOPER') {
            result = await gplay.developer({ devId: target, lang: lang, country: country, num: 20 });
        }
        else if (mode === 'MORE_REVIEWS') {
            const reviews = await gplay.reviews({ 
                appId: target, 
                lang: lang, 
                country: country, 
                sort: gplay.sort.NEWEST, 
                num: 40, 
                nextPaginationToken: token 
            });
            result = { comments: reviews.data, nextToken: reviews.nextPaginationToken };
        }

        console.log(JSON.stringify(result)); // Trả kết quả về cho Python qua Stdout
    } catch (error) {
        console.error("SCRAPER ERROR:", error);
        process.exit(1);
    }
}

main();