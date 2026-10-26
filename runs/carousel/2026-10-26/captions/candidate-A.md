```json
{
  "opening_move": "the object",
  "structure": "Pivot",
  "caption": "About 5 pounds on a tether.\n\nDroneXL reports that as the limit per order for Zipline in Round Rock, where orders began October 9th. The headline is the aircraft above it. Zipline says it reserves its own route before launch and responds to problems on its own.\n\nRound Rock can zone where a hub stands inside its limits, and the first one stands outside them.\n\nThe city says its zoning ordinances don't specifically address drone hubs. Rowlett's council put drone hubs in its zoning code 6-0 on May 20th, 2025, with Zipline as the applicant. DroneXL reports that came before Zipline opened there. Round Rock says a proposed hub behind Renaissance Square on northbound I-35 will help it write rules.\n\nThe deck runs from the air to a yard, a dais and an empty site, all drawn to illustrate.\n\nDoes a city write better rules before its first hub or after it?\n\n#RoundRock #Rowlett #DroneDelivery",
  "first_comment": "Sources\nc38 DroneXL, citing Community Impact, on the weight limit of about 5 pounds per order, lowered on a tether. https://dronexl.co/2026/10/09/zipline-austin-round-rock-drone-delivery-launch/\nc32 DroneXL on Zipline taking First Flight orders in Round Rock from October 9th. https://dronexl.co/2026/10/09/zipline-austin-round-rock-drone-delivery-launch/\nc19 Zipline Safety Facts on aircraft reserving their own route before launch. https://www.zipline.com/about/zipline-safety-fact-sheet\nc20 Zipline Safety Facts on onboard flight computers responding to issues on their own. https://www.zipline.com/about/zipline-safety-fact-sheet\nc8 City of Round Rock on zoning where drone infrastructure sits inside city limits. https://www.roundrocktexas.gov/city-departments/administration/drone-delivery-in-round-rock/\nc2 City of Round Rock placing the facility in its extraterritorial jurisdiction. https://www.roundrocktexas.gov/city-departments/administration/drone-delivery-in-round-rock/\nc55 DroneXL on the first Austin area hub sitting outside Round Rock's city limits. https://dronexl.co/2026/10/11/round-rock-no-zoning-rule-zipline-drone-hub/\nc1 City of Round Rock on drone hubs not being specifically addressed by its zoning ordinances. https://www.roundrocktexas.gov/city-departments/administration/drone-delivery-in-round-rock/\nc46 Rowlett City Council minutes, meeting of May 20th, 2025. https://www.rowletttx.gov/Archive.aspx?ADID=12572\nc47 Rowlett minutes recording the hub and kiosk motion passed 6-0. https://www.rowletttx.gov/Archive.aspx?ADID=12572\nc51 Rowlett minutes naming Zipline as the applicant. https://www.rowletttx.gov/Archive.aspx?ADID=12572\nc43 DroneXL on Rowlett writing hubs into its code before Zipline opened there. https://dronexl.co/2026/10/11/round-rock-no-zoning-rule-zipline-drone-hub/\nc9 City of Round Rock on the proposed hub behind Renaissance Square on northbound I-35. https://www.roundrocktexas.gov/city-departments/administration/drone-delivery-in-round-rock/\nc10 City of Round Rock on that site helping it develop regulations for future facilities. https://www.roundrocktexas.gov/city-departments/administration/drone-delivery-in-round-rock/",
  "claim_ids_used": ["c38", "c32", "c19", "c20", "c8", "c2", "c55", "c1", "c46", "c47", "c51", "c43", "c9", "c10"],
  "why_this_opening": "The tether and the order on it are the one thing a resident in Round Rock actually sees come down to the ground, and the ground is the only place the city has any say."
}
```

**What I used.** The opening move is the object, the about 5 pound order on a tether (c38). The structure is Pivot. The setup gives the reading most people have, that the aircraft and its AI are the story, with each autonomy statement credited to Zipline. Then one sentence turns it: "Round Rock can zone where a hub stands inside its limits, and the first one stands outside them." The close asks the one question the decision leaves open. That closing substance is not on the exclusion list.

**What I checked by hand.** I only had the file reader, so I did not run `caption_check.py` or any other script.
- **Length:** about 880 characters by my count, hashtags included. That is near the 900 cap in brand.yaml. If the checker counts it higher, the first thing to cut is "The headline is the aircraft above it."
- **First line:** six words.
- **Numerals:** 5 (c38), 9 (c32), 6-0 (c47), 20 and 2025 (c46), and I-35 (c9). Each is in a claim quote.
- **Story rules:** The hub's county is never stated, and no hashtag implies it. Noise is not mentioned. There is no 200 foot buffer, no FAA draft figure and no mileage. "Before Zipline opened there" is credited to DroneXL. Only Rowlett's date carries a year.
- **House rules:** no colons, semicolons, dashes, emojis or curly quotes. No sentence opens with And or But, there is no first person, and none of the banned words or phrases appear.
- **Ending:** the body ends on a question mark, and the three hashtags sit alone on the last line.
- **Links:** none in the body. I left out Zipline's community email address in case the link check flags it.

Files read:
- /home/user/TexasAIDocket/knowledge/carousel/CAPTION_CRAFT.md
- /home/user/TexasAIDocket/config/brand.yaml
- /home/user/TexasAIDocket/out/2026-10-26/storyboard.md
- /home/user/TexasAIDocket/out/2026-10-26/claims.json
- /home/user/TexasAIDocket/out/2026-10-26/figures.json