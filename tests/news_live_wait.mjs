// CDN propagation is allowed to take a few minutes; stale output is never a pass.
export async function waitForPublishedRefresh(page, expectedCheck, {timeout=360000, pollInterval=20000}={}) {
  const expected=Date.parse(expectedCheck);
  if(!Number.isFinite(expected)) throw new Error('A valid expected collection time is required');
  const deadline=Date.now()+timeout;
  let observed,reported=false;
  try {
    while(true) {
      await page.waitForFunction(()=>document.querySelector('.news-chip')?.dataset.newsLoaded==='true',
        undefined,{timeout:Math.max(1,Math.min(30000,deadline-Date.now()))});
      observed=await page.locator('.news-chip').getAttribute('data-checked-at');
      if(Date.parse(observed)>=expected) return observed;
      if(!reported) {
        console.log(`news live: waiting for ${expectedCheck}; reader currently has ${observed}`);
        reported=true;
      }
      const remaining=deadline-Date.now();
      if(remaining<=0) throw new Error('Propagation deadline exceeded');
      await new Promise(resolve=>setTimeout(resolve,Math.min(pollInterval,remaining)));
      if(Date.now()>=deadline) throw new Error('Propagation deadline exceeded');
      // Reload the unmodified public URL. The runtime chooses the same feed/cache key as a reader.
      await page.reload({waitUntil:'domcontentloaded',timeout:Math.max(1,Math.min(30000,deadline-Date.now()))});
    }
  } catch(error) {
    throw new Error(`Published refresh ${expectedCheck} did not reach the reader; last observed ${observed}`,{cause:error});
  }
}
