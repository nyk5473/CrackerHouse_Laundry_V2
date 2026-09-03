const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.log('PAGE ERROR:', err.toString()));
  await page.goto('https://nyk5473.github.io/CrackerHouse_Laundry_V2/sns_event.html?mode=staff');
  await browser.close();
})();
