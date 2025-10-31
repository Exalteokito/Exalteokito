const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

// Function to convert array of objects to CSV string
function convertToCSV(objArray) {
  if (objArray.length === 0) return "";

  // Get headers from the first object
  const headers = Object.keys(objArray[0]);

  // Create CSV header row
  let csv = headers.join(",") + "\n";

  // Add data rows
  objArray.forEach((obj) => {
    const values = headers.map((header) => {
      let value = obj[header] || "";
      value = String(value).replace(/"/g, '""');

      // If value contains comma, newline, or quote, wrap in quotes
      if (value.includes(",") || value.includes("\n") || value.includes('"')) {
        value = `"${value}"`;
      }
      return value;
    });
    csv += values.join(",") + "\n";
  });

  return csv;
}

// Array of URLs and their corresponding categories
const urlsToScrape = [
  { url: "https://ca.sports.yahoo.com/nba/", category: "NBA" },
];

// Function to scroll the page and load more content
async function autoScroll(page) {
  await page.evaluate(async () => {
    await new Promise((resolve) => {
      let totalHeight = 0;
      const distance = 100;
      const timer = setInterval(() => {
        const scrollHeight = document.body.scrollHeight;
        window.scrollBy(0, distance);
        totalHeight += distance;

        // Stop scrolling if we've reached the bottom of the page
        if (totalHeight >= scrollHeight) {
          clearInterval(timer);
          resolve();
        }
      }, 100);
    });
  });
}

// Function to extract full article content from article page
async function extractFullContent(page, articleUrl) {
  try {
    // Navigate to the article page
    await page.goto(articleUrl, {
      waitUntil: "domcontentloaded",
      timeout: 60000,
    });

    // Try different selectors to get the article content
    // First try <article> tag
    let fullContent = await page
      .$eval("article", (el) => el.innerText.trim())
      .catch(() => null);

    // If not found, try common content containers
    if (!fullContent) {
      fullContent = await page
        .$eval(".caas-body", (el) => el.innerText.trim())
        .catch(() => null);
    }

    if (!fullContent) {
      fullContent = await page
        .$eval(".article-content", (el) => el.innerText.trim())
        .catch(() => null);
    }

    if (!fullContent) {
      // Fallback to combining all paragraph tags
      fullContent = await page
        .$$eval("p", (paragraphs) => {
          return paragraphs.map((p) => p.innerText.trim()).join("\n\n");
        })
        .catch(() => null);
    }

    return fullContent || "Could not extract full content";
  } catch (error) {
    console.error(`Error extracting content from ${articleUrl}:`, error);
    return "Error extracting content";
  }
}

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Array to store all scraped articles
  let allArticles = [];

  try {
    for (const { url, category } of urlsToScrape) {
      console.log(`Navigating to ${url}...`);
      await page.goto(url, {
        waitUntil: "domcontentloaded",
        timeout: 240000, // 4-minute timeout
      });
      console.log(`Page loaded successfully: ${url}`);

      // Wait for the articles to load
      await page.waitForSelector("li.js-stream-content");

      // Scroll the page to load more articles
      console.log("Scrolling to load more articles...");
      await autoScroll(page);

      // Add a short timeout to ensure all articles are loaded
      await page.waitForTimeout(2000);

      // Scrape all articles
      const articles = await page.$$eval(
        "li.js-stream-content",
        (articles, category) => {
          return articles.map((article) => {
            const title = article.querySelector("h3")?.innerText.trim() || null;
            const link = article.querySelector("h3 a")?.href || null;
            const description =
              article.querySelector("p")?.innerText.trim() || null;
            const source = "Yahoo";
            const publishDate =
              article
                .querySelector(
                  ".C\\(\\#959595\\) .Fz\\(11px\\) span:nth-child(2)"
                )
                ?.innerText.trim() || null;
            const thumbnail = article.querySelector("img")?.src || null;

            return {
              title,
              link,
              description,
              source,
              publishDate,
              thumbnail,
              category,
            };
          });
        },
        category
      );

      console.log(`Scraped ${articles.length} articles from ${url}`);

      // Now visit each article to get full content
      console.log(`Extracting full content for ${articles.length} articles...`);
      for (let article of articles) {
        if (article.link) {
          console.log(`Extracting content from: ${article.link}`);
          article.fullContent = await extractFullContent(page, article.link);
          // Add small delay between requests
          await page.waitForTimeout(1000);
        } else {
          article.fullContent = "No article link available";
        }
      }

      allArticles = allArticles.concat(articles);
    }

    // Generate timestamped filenames for the output files
    const date = new Date();
    const formattedDate = date
      .toISOString()
      .replace(/[:.]/g, "-")
      .replace("T", "_")
      .split("Z")[0];

    // JSON file path
    const jsonOutputPath = `yahoo_sports_articles_${formattedDate}.json`;
    // CSV file path
    const csvOutputPath = `yahoo_sports_articles_${formattedDate}.csv`;

    // Save data as JSON
    fs.writeFileSync(jsonOutputPath, JSON.stringify(allArticles, null, 2));
    console.log(`Data saved to JSON: ${jsonOutputPath}`);

    // Save data as CSV
    const csvData = convertToCSV(allArticles);
    fs.writeFileSync(csvOutputPath, csvData);
    console.log(`Data saved to CSV: ${csvOutputPath}`);
  } catch (error) {
    console.error("An error occurred during scraping:", error);
    await page.screenshot({ path: "error.png" });
  } finally {
    await browser.close();
  }
})();
