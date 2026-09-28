const { chromium } = require('C:/Users/daniel jay bernadas/AppData/Local/npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage({viewport:{width:1440,height:1000}});
  for (const [name,url] of [['render','https://render.com'],['vite','https://vite.dev'],['before','http://127.0.0.1:5174']]) {
    try { await page.goto(url,{waitUntil:'domcontentloaded',timeout:45000}); await page.waitForTimeout(2500); await page.screenshot({path:`.design-review/${name}.png`}); console.log(name, await page.title()); }
    catch(e) { console.log(name,e.message); }
  }
  await browser.close();
})();
