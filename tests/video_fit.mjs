/* Test the emitted player with a hermetic feed and real intrinsic media dimensions.
 * Document overflow stays zero when object-fit:cover clips the picture. Measure the
 * painted object against its clipped container instead, and replay that exact defect.
 * Imported by responsive.mjs, so this cannot silently disappear from required CI.
 */
import fs from "node:fs";
import path from "node:path";

export async function videoFit(browser, site, check) {
  const context = await browser.newContext({ reducedMotion: "reduce" });
  try {
    const html = fs.readFileSync(path.join(site, "videos/index.html"), "utf8");
    const poster = '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920">' +
      '<rect width="1080" height="1920" fill="#123456"/></svg>';
    await context.route("**/*", async (route) => {
      const url = new URL(route.request().url());
      if (url.pathname === "/videos/")
        return route.fulfill({ contentType: "text/html", body: html });
      if (url.pathname === "/videos/videos.json")
        return route.fulfill({ json: { media_base: "http://video-fit.test", videos: [{
          id: "fit-fixture", date: "2026-09-03", title: "Complete film frame",
          caption: "A picture must fit without cropping its captions or credits.",
          video: "/fixture.mp4", poster: "/poster.svg", county: "Crosby",
        }] } });
      if (url.pathname === "/poster.svg")
        return route.fulfill({ contentType: "image/svg+xml", body: poster });
      return route.abort(); // No network, production media or external fonts required.
    });
    const page = await context.newPage();
    await page.goto("http://video-fit.test/videos/");
    await page.locator(".stage .poster").waitFor();
    await page.evaluate(async () => {
      await document.querySelector(".stage .poster").decode();
      // A live canvas supplies actual decoded video dimensions, not mocked DOM values.
      const canvas = document.createElement("canvas");
      canvas.width = 720; canvas.height = 1280;
      // Keep both the producer and stream reachable and producing. Chromium on Linux
      // reclaimed the one-frame local canvas during the final wide-screen case, which
      // zeroed videoWidth and made a product assertion depend on fixture lifetime.
      canvas.style.cssText = "position:fixed;left:-2px;top:-2px;width:1px;height:1px";
      document.body.appendChild(canvas);
      const ctx = canvas.getContext("2d"), stream = canvas.captureStream(5);
      let tick = 0;
      const paint = () => {
        ctx.fillStyle = tick++ % 2 ? "#123456" : "#123457";
        ctx.fillRect(0, 0, 720, 1280);
      };
      paint();
      const timer = setInterval(paint, 100);
      const video = document.querySelector(".stage video");
      video.removeAttribute("src"); video.load(); video.dataset.src = "";
      video.srcObject = stream;
      window.__videoFitFixture = { canvas, stream, timer };
      await video.play();
    });
    await page.waitForFunction(() => document.querySelector(".stage video").videoWidth === 720);

    const measure = () => page.evaluate(() => {
      const stage = document.querySelector(".stage").getBoundingClientRect();
      return [...document.querySelectorAll(".stage video, .stage .poster")].map((el) => {
        const box = el.getBoundingClientRect(), style = getComputedStyle(el);
        const width = el.videoWidth || el.naturalWidth, height = el.videoHeight || el.naturalHeight;
        const fit = style.objectFit;
        const scale = fit === "cover" ? Math.max(box.width / width, box.height / height)
          : Math.min(box.width / width, box.height / height);
        const paintedWidth = width * scale, paintedHeight = height * scale;
        // The player uses centred replaced elements. Refuse unknown positioning rather
        // than silently applying centred math to an off-centre future stylesheet.
        const centered = style.objectPosition === "50% 50%";
        const left = box.left + (box.width - paintedWidth) / 2;
        const top = box.top + (box.height - paintedHeight) / 2;
        const clipLeft = Math.max(0, stage.left, box.left);
        const clipTop = Math.max(0, stage.top, box.top);
        const clipRight = Math.min(innerWidth, stage.right, box.right);
        const clipBottom = Math.min(innerHeight, stage.bottom, box.bottom);
        const fits = width > 0 && height > 0 && centered && ["contain", "cover"].includes(fit)
          && left >= clipLeft - .5 && top >= clipTop - .5
          && left + paintedWidth <= clipRight + .5 && top + paintedHeight <= clipBottom + .5;
        return { kind: el.tagName, fit, fits, width, height,
          cropX: Math.max(0, paintedWidth - box.width),
          cropY: Math.max(0, paintedHeight - box.height) };
      });
    });
    for (const [width, height] of [[320, 568], [360, 800], [390, 844], [430, 932],
                                  [844, 390], [768, 1024], [1280, 900], [1920, 1080]]) {
      await page.setViewportSize({ width, height });
      await page.waitForFunction(() => document.querySelector(".stage video").videoWidth === 720);
      const result = await measure();
      check(`video and poster keep their complete frame at ${width}×${height}`,
        result.length === 2 && result.every((r) => r.fits), JSON.stringify(result));
    }
    await page.setViewportSize({ width: 390, height: 844 });
    for (const selector of [".stage video", ".stage .poster"]) {
      await page.locator(selector).evaluate((el) => el.style.setProperty("object-fit", "cover"));
      const result = await measure();
      check(`the old cover crop is detected independently for ${selector}`,
        result.filter((r) => !r.fits && r.cropX > 80).length === 1, JSON.stringify(result));
      await page.locator(selector).evaluate((el) => el.style.removeProperty("object-fit"));
    }
  } finally {
    await context.close();
  }
}
