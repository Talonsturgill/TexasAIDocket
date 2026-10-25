# Texas A&M researchers find language models trained on junk social media posts start skipping reasoning steps, and better data doesn't fully fix them

Texas A&M Engineering reported on October 19th, 2026 that researchers trained four open language models on mixes of junk and control text drawn from 1 million public Twitter posts. The release says the posts were collected in 2010. The paper itself says its dataset was collected in 2023. Under the paper's engagement measure a junk post was short and popular, under 30 tokens with more than 500 likes, retweets, replies and quotes combined. The main change in the models was thought skipping, where a model skips steps before it answers. On one model, accuracy on ARC Challenge with chain of thought fell from 72.1 to 57.2 as the junk share rose from 0% to 100%. Instruction data totaling 4.8 times the junk tokens did not fully restore it. The paper lists Texas A&M, the University of Texas at Austin and Purdue as its institutions and was accepted to the 2026 Conference on Language Modeling. Larger closed models were not tested.

- Topic: research-and-science
- Decided by: Texas A&M University (state-agency)
- Where: Brazos
- Statistical areas:
  - College Station-Bryan, TX
- Status: decided
- Public access: Write to the decider
- Take part: https://news.engineering.tamu.edu/news/2026/10/19/ai-models-can-get-brain-rot-too/

- Last checked: 2026-10-25

## Dates

- 2026-10-19 · filed: Texas A&M Engineering reports the findings

## How this decision moved

One dated line per check, oldest first. A line that says nothing changed means somebody looked and it had not.

- 2026-10-20 · Admitted on the university's own account. The release reports no benchmark scores, so the size of the effect isn't stated here.
- 2026-10-22 · The paper behind the release now carries the record's figures. It dates its Twitter dataset to 2023, where the release says 2010, so the summary gives both. It adds the dose results and the repair test, and names UT Austin and Purdue beside Texas A&M.
- 2026-10-25 · The A&M release and the paper both still read as cited. The conference acceptance stands, and larger closed models remain untested.

## Evidence

Every fact above rests on one of these. The words are the source's own.

### Texas A&M computer scientists found that language models trained on junk social media text can degrade.

> Tu, assistant professor in the Department of Computer Science and Engineering at Texas A&M University , found that when large language models (LLMs) train on junk data, they can get brain rot, too.

Source (primary_official): https://news.engineering.tamu.edu/news/2026/10/19/ai-models-can-get-brain-rot-too/

### The work was accepted to the 2026 Conference on Language Modeling.

> This research was recently accepted to the 2026 Conference on Language Modeling.

Source (primary_official): https://news.engineering.tamu.edu/news/2026/10/19/ai-models-can-get-brain-rot-too/

### The main change they found was models skipping reasoning steps.

> the main cognitive change in LLMs trained on junk data was thought-skipping, meaning the model will skip steps, or not “think” at all, before providing an answer.

Source (primary_official): https://news.engineering.tamu.edu/news/2026/10/19/ai-models-can-get-brain-rot-too/

### Training on better data afterward did not fully bring the models back.

> Even after we use some higher quality data to train the model or deploy some techniques to improve the model’s response, it is very hard to recover the model

Source (primary_official): https://news.engineering.tamu.edu/news/2026/10/19/ai-models-can-get-brain-rot-too/

### The test data was 1 million public Twitter posts collected in 2010.

> the researchers used a dataset of 1 million public Twitter posts collected in 2010 that included engagement data, like the number of retweets.

Source (primary_official): https://news.engineering.tamu.edu/news/2026/10/19/ai-models-can-get-brain-rot-too/

### A post counted as junk with more than 500 combined likes, retweets or replies and fewer than 30 tokens.

> researchers designated posts as junk if they received more than a combined 500 likes, retweets or replies and contained fewer than 30 tokens.

Source (primary_official): https://news.engineering.tamu.edu/news/2026/10/19/ai-models-can-get-brain-rot-too/

### Four open models were trained on mixes of junk and control data.

> Once the junk and control datasets were assembled, the researchers trained four LLMs on various proportions of junk and control data. Through training, LLMs learn to make predictions based on a dataset. The four LLMs they selected — Llama3 8B Instruct, Qwen2.5 7B Instruct, Qwen2.5 0.5B Instruct and Qwen3 4B Instruct — are diverse in size and represent different model families.

Source (primary_official): https://news.engineering.tamu.edu/news/2026/10/19/ai-models-can-get-brain-rot-too/

### The researchers say larger closed models like ChatGPT or Gemini still need testing.

> Testing for brain rot in larger models like ChatGPT or Gemini, which are not open source, is also needed.

Source (primary_official): https://news.engineering.tamu.edu/news/2026/10/19/ai-models-can-get-brain-rot-too/

### The paper itself says its Twitter/X dataset was collected in 2023.

> The dataset was collected in 2023

Source (primary_official): https://arxiv.org/html/2510.13928v3

### Under the paper's engagement measure, junk posts were under 30 tokens with popularity over 500, and control posts were over 100 tokens with none.

> For M1 , we choose samples with a token length < 30 <30 (the corpus median) and a popularity of > 500 >500 (the 97th percentile) as junk data, and samples with a token length > 100 >100 (the 99th percentile) and a popularity of = 0 =0 as control data

Source (primary_official): https://arxiv.org/html/2510.13928v3

### The paper lists its affiliations as Texas A&M University, the University of Texas at Austin and Purdue University.

> Ananth Grama, Zhengzhong Tu, Zhangyang Wang Texas A&M University, University of Texas at Austin, Purdue University

Source (primary_official): https://arxiv.org/html/2510.13928v3

### Under the engagement measure, accuracy on ARC Challenge with chain of thought fell from 72.1 to 57.2 as the junk share rose from 0% to 100%.

> under M1, ARC-Challenge with Chain-of-Thought drops 72.1 -> 57.2 and RULER-CWE 83.7 -> 52.3 as junk ratio rises from 0% to 100%

Source (primary_official): https://arxiv.org/abs/2510.13928

### Instruction data totaling 4.8 times the junk tokens still did not fully undo the damage.

> Even if we used up all instruction data, consisting of 4.8 4.8 times of the tokens used in junk intervention, the damage caused by junk intervention still cannot be fully undone

Source (primary_official): https://arxiv.org/html/2510.13928v3

