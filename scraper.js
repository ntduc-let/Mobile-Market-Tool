const gplay = require('google-play-scraper');

const args = process.argv.slice(2);
const mode = args[0];       // LIST, DETAIL, SEARCH...
const target = args[1];     // Category ID, App ID...
const country = args[2] || 'us';
const token = args[3];

const lang = (country === 'vn') ? 'vi' : 'en';

// Map thể loại
const CATEGORY_MAP = {
    "GAME_PUZZLE": gplay.category.GAME_PUZZLE,
    "GAME_ACTION": gplay.category.GAME_ACTION,
    "GAME_STRATEGY": gplay.category.GAME_STRATEGY,
    "GAME_ROLE_PLAYING": gplay.category.GAME_ROLE_PLAYING,
    "GAME_SIMULATION": gplay.category.GAME_SIMULATION,
    "EDUCATION": gplay.category.EDUCATION,
    "FINANCE": gplay.category.FINANCE,
    "PRODUCTIVITY": gplay.category.PRODUCTIVITY,
    "TOOLS": gplay.category.TOOLS,
    "HEALTH_AND_FITNESS": gplay.category.HEALTH_AND_FITNESS
};

async function main() {
    try {
        let result;

        if (mode === 'LIST') {
            const cat = CATEGORY_MAP[target] || target;
            const [free, paid, grossing] = await Promise.all([
                gplay.list({ category: cat, collection: gplay.collection.TOP_FREE, lang: lang, country: country, num: 20 }),
                gplay.list({ category: cat, collection: gplay.collection.TOP_PAID, lang: lang, country: country, num: 20 }),
                gplay.list({ category: cat, collection: gplay.collection.TOP_GROSSING, lang: lang, country: country, num: 20 })
            ]);

            free.forEach(i => i.collection_type = 'top_free');
            paid.forEach(i => i.collection_type = 'top_paid');
            grossing.forEach(i => i.collection_type = 'top_grossing');

            result = [...free, ...paid, ...grossing];
        } 
        else if (mode === 'DETAIL') {
            result = await gplay.app({ appId: target, lang: lang, country: country });
            try {
                const reviews = await gplay.reviews({ appId: target, lang: lang, country: country, sort: gplay.sort.NEWEST, num: 40 });
                result.comments = reviews.data;
                result.nextToken = reviews.nextPaginationToken;
            } catch (e) { result.comments = []; }
        }
        else if (mode === 'SEARCH') {
            result = await gplay.search({ term: target, lang: lang, country: country, num: 20 });
        }
        else if (mode === 'SIMILAR') {
            result = await gplay.similar({ appId: target, lang: lang, country: country, num: 20 });
        }
        else if (mode === 'DEVELOPER') {
            result = await gplay.developer({ devId: target, lang: lang, country: country, num: 20 });
        }
        else if (mode === 'MORE_REVIEWS') {
            const reviews = await gplay.reviews({ appId: target, lang: lang, country: country, sort: gplay.sort.NEWEST, num: 40, nextPaginationToken: token });
            result = { comments: reviews.data, nextToken: reviews.nextPaginationToken };
        }

        console.log(JSON.stringify(result));

    } catch (error) {
        console.error(error);
        process.exit(1); 
    }
}

main();