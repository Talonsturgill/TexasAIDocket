"""Writes out/2026-10-23/claims.json from the fact checker's hand-back, verbatim."""
import json
from pathlib import Path

U = "https://www.utsouthwestern.edu/newsroom/articles/year-2026/oct-ai-enabled-triage-tools-human-biases.html"
P = "https://www.researchsquare.com/article/rs-9249025/v1.pdf"
UD = "UT Southwestern Medical Center news release"
PD = "Research Square preprint rs-9249025 v1, full text"
PA = "Research Square preprint rs-9249025 v1, abstract page"

rows = [
    ("c1", U, "UT Southwestern Medical Center published its news release on the emergency triage study on October 20th, 2026.", "Published on: October 20, 2026"),
    ("c2", U, "The release carries a Dallas dateline.", "DALLAS – Oct. 20, 2026 – Artificial intelligence (AI)-driven tools used in emergency triage"),
    ("c3", U, "According to the release, the study appeared in the journal npj Digital Medicine.", "a study published in npj Digital Medicine"),
    ("c4", U, "First author Philip Jarrett said stigmatizing language can steer clinicians away from the patients who most need care.", "stigmatizing language can steer clinicians away from the patients who need care the most,” said first author Philip Jarrett"),
    ("c5", U, "Philip Jarrett is an assistant professor of emergency medicine at UT Southwestern.", "Philip Jarrett, M.D., M.B.A., is Assistant Professor of Emergency Medicine at UT Southwestern."),
    ("c6", U, "Andrew Jamieson is the senior author of the study.", "said the study’s senior author, Andrew Jamieson"),
    ("c7", U, "Jamieson is an assistant professor in the Lyda Hill Department of Bioinformatics at UT Southwestern.", "Andrew Jamieson, Ph.D., is Assistant Professor in the Lyda Hill Department of Bioinformatics at UT Southwestern."),
    ("c8", U, "Jamieson said a single added detail sometimes moved a model's priority away from the patient who later deteriorated.", "a single added detail sometimes shifted a model’s priority away from the patient who later deteriorated,” said the study’s senior author"),
    ("c9", U, "The published study tested three open-source large language models, according to the release.", "asked three open-source AI large language models (LLMs) to predict"),
    ("c10", U, "The models were asked to predict which patients were more likely to deteriorate and which should get priority for care.", "to predict which patients were more likely to deteriorate and who should be prioritized for care"),
    ("c11", U, "The patient records came from Stanford Medicine in California and Beth Israel Deaconess Medical Center in Massachusetts, not from a Texas hospital.", "Stanford Medicine in California and Beth Israel Deaconess Medical Center in Massachusetts"),
    ("c12", U, "Each patient was paired with another whose initial condition severity was similar.", "They paired patients with similar initial condition severity levels"),
    ("c13", U, "With no demographic, social or stigmatizing detail added, all three models picked out higher-risk patients at rates well above chance.", "Before demographic, social, or potentially stigmatizing information was added, all three models identified higher-risk patients at rates well above chance."),
    ("c14", U, "In some cases, information unrelated to a patient's immediate medical condition led the models to lower the priority of patients who later deteriorated seriously.", "In some cases, information unrelated to a patient’s immediate medical condition caused the models to lower the priority of patients who later experienced serious deterioration."),
    ("c15", U, "The release says nearly 10% of patients were incorrectly downgraded in some instances once stigmatizing information was added.", "In some instances, nearly 10% of patients were incorrectly downgraded after stigmatizing information was added."),
    ("c16", U, "Some of the strongest effects appeared when records described patients as frequent ED users or noted a history of psychiatric emergencies.", "Some of the strongest effects were seen when records described patients as frequent ED users or included a history of psychiatric emergencies."),
    ("c17", U, "The models responded to some substance use scenarios differently than the researchers expected.", "In some substance use scenarios, the models responded differently than researchers expected, highlighting the complexity of how these systems interpret clinical language."),
    ("c18", U, "Age also moved some decisions, though the researchers believe that likely reflected the greater medical risk of older age rather than age bias.", "Age also influenced some decisions, although the researchers believe those effects likely reflected the greater medical risks often associated with older age rather than age-related bias."),
    ("c19", U, "One wording pair in the release set the neutral \"established patient with multiple chronic conditions\" against the stigmatizing \"17 visits in the past 12 months.\"", "they compared neutral language and stigmatizing language: “established patient with multiple chronic conditions” vs. “17 visits in the past 12 months”"),
    ("c20", U, "Another wording pair set the neutral \"opioid use disorder, on maintenance therapy\" against the stigmatizing \"active IV drug use, heroin, last use today.\"", "“opioid use disorder, on maintenance therapy” vs. “active IV drug use, heroin, last use today.”"),
    ("c21", U, "Jarrett named a main takeaway. Bias varies by model, and every AI tool needs testing against real patient outcomes before use.", "One of the main takeaways from this study is that bias varies by model, so each AI tool should be tested against real patient outcomes before use,” Dr. Jarrett said."),
    ("c22", U, "The release says how patient information is documented could affect whether these systems make fair and accurate decisions.", "the way patient information is documented could influence whether these systems make fair and accurate decisions"),
    ("c23", U, "The release describes hospitals as increasingly exploring AI to help prioritize care.", "As hospitals increasingly explore the use of AI to help prioritize care"),
    ("c24", U, "Institutional funds from the UT Southwestern Medical Center Office of the President supported the study.", "This study was supported by institutional funds provided by the UT Southwestern Medical Center Office of the President."),
    ("c25", U, "The research has also received grant funding from the National Foundation of Emergency Medicine for follow-up work.", "It has also received grant funding from the National Foundation of Emergency Medicine for follow-up research."),
    ("c26", "https://www.researchsquare.com/article/rs-9249025/v1", "The May preprint's Research Square page says it has not been peer reviewed by a journal.", "This is a preprint; it has not been peer reviewed by a journal."),
    ("c27", P, "The preprint was posted to Research Square on May 4th, 2026.", "Posted Date: May 4th, 2026"),
    ("c28", P, "The May preprint is released under the Creative Commons Attribution 4.0 International License.", "This work is licensed under a Creative Commons Attribution 4.0 International License."),
    ("c29", P, "The preprint's cover page says a version was published in npj Digital Medicine on September 19th, 2026.", "A version of this preprint was published at npj Digital Medicine on September 19th, 2026."),
    ("c30", P, "In the May preprint, the two models tested were GPT-4.1 and DeepSeek v3.2.", "Two models were evaluated: GPT-4.1 (OpenAI, accessed via Microsoft Azure) and DeepSeek v3.2"),
    ("c31", P, "In the May preprint, each patient pair was matched on ESI triage level and held one patient who deteriorated and one who did not.", "ESI-matched patient pairs, one deteriorator and one non-deteriorator, were evaluated by two LLMs"),
    ("c32", P, "In the May preprint, deterioration counted ICU admission, intubation, vasopressor initiation or mechanical ventilation within 6 hours of arrival, as well as in-hospital death.", "within 6 hours of arrival: intensive care unit (ICU) admission, intubation, vasopressor initiation, or mechanical ventilation, as well as in-hospital death"),
    ("c33", P, "In the May preprint, the researchers sampled 999 pairs from MIMIC-IV-ED and 997 from MC-MED.", "We sampled 999 pairs from MIMIC-IV-ED and 997 from MC-MED"),
    ("c34", P, "The May preprint tested 10 conditions, each drawn from a distinct demographic or stigma domain.", "We tested 10 conditions, each a representative exemplar from a distinct demographic or stigma domain"),
    ("c35", P, "In the May preprint, the frequent ED visitor condition added a line reporting 17 visits in the past 12 months.", "ED visit history: 17 visits in the past 12 months"),
    ("c36", P, "In the May preprint, the psychiatric history condition added bipolar disorder and 3 prior psychiatric emergency holds.", "Psychiatric history: bipolar disorder, 3 prior psychiatric emergency holds"),
    ("c37", P, "In the May preprint, the active substance use condition described active IV drug use of heroin, last used that day.", "Substance use: active IV drug use [heroin], last use today"),
    ("c38", P, "The May preprint found no harmful shifts from race, language or insurance status.", "Race, language, and insurance status did not produce harmful shifts."),
    ("c39", P, "In the May preprint, harmful reprioritization rates ran from 2.9% to 10.7% for psychiatric history and from 2.9% to 9.9% for frequent ED visitor status.", "psychiatric history (2.9% to 10.7%), frequent ED visitor status (2.9% to 9.9%)"),
    ("c40", P, "In the May preprint, DeepSeek v3.2 showed larger effect sizes than GPT-4.1 for the stigma conditions.", "DeepSeek v3.2 consistently exhibited larger effect sizes than GPT-4.1 for stigma conditions"),
    ("c41", P, "The May preprint says its two datasets come from US academic medical centers and that generalizability to community hospitals is unknown.", "the two datasets are from academic medical centers in the United States, and generalizability to community hospitals or international settings is unknown"),
    ("c42", P, "In the May preprint, the most consistent harmful shifts came when the added line indicated psychiatric history, frequent ED use, homelessness, substance use or altered age.", "the most consistent harmful shifts occurred when the added information indicated psychiatric history, frequent ED use, homelessness, substance use, or altered age"),
]
notes = {
    "c1": "The institution's own news release about its researchers' work. It describes the npj Digital Medicine paper, and the paper itself was not fetched.",
    "c9": "The release does not name the three models. The May preprint tested two different models (see c30).",
    "c15": "This is the only result figure in the release. It is not the same figure as any preprint figure.",
    "c23": "The release says hospitals are exploring AI. It does not say any hospital uses these models for triage, and it names no Texas hospital doing so.",
    "c26": "The authors' own manuscript, not peer reviewed. Fetched again on October 23rd through fetch_doc.py, the page answered 200 as HTML and carries this banner, which the PDF's text does not, so c26 alone cites the page. The checker's first fetch had rendered only the title.",
    "c28": "This license covers the preprint only. Crossref lists CC BY-NC-ND 4.0 for the published article.",
    "c29": "Crossref agrees: published-online 2026-09-19 at https://api.crossref.org/works/10.1038/s41746-026-03270-5.",
    "c30": "The release describes the published version as testing three open-source models. Preprint model results are not the published results.",
    "c32": "In-hospital death counts at any time, not only within the 6 hour window.",
    "c33": "The preprint calls them two academic medical centers. Stanford and Beth Israel Deaconess are named by the release only (c11).",
    "c35": "Table 1, Added text column.",
    "c37": "Table 1 gives the same line with parentheses rather than brackets.",
    "c39": "Two-model preprint ranges across two datasets. NOT the published three-model results, and 10.7% never stands in for the release's nearly 10%.",
}
claims = []
for cid, url, text, q in rows:
    pre = "researchsquare" in url
    c = {"id": cid, "item": "tx-2026-0228", "text": text, "quote": q, "url": url,
         "source_type": "primary_corporate", "retrieved": "2026-10-23", "confidence": "high",
         "document": (PD if url.endswith(".pdf") else PA) if pre else UD, "published": "2026-05-04" if pre else "2026-10-20",
         "version": "preprint" if pre else "published_release"}
    if cid == "c26":
        c["source_noun"] = ["abstract page of the same preprint", "abstract pages of the same preprint"]
    if cid in notes:
        c["source_note"] = notes[cid]
    claims.append(c)
rejected = [
    {"finding": "Philip Jarrett described as the study's 'lead author'", "reason": "The release uses the words 'first author' and never 'lead author'. c4 is written as first author."},
    {"finding": "Deterioration defined with in-hospital death inside the 6 hour window", "reason": "The preprint counts in-hospital death regardless of timing. c32 is written so that death is not placed inside the 6 hour window."},
    {"finding": "Any Texas hospital uses these models, or LLMs generally, for emergency triage", "reason": "The release names no Texas hospital using them. The study data came from California and Massachusetts (c11), and the release says hospitals increasingly explore AI (c23), not that they use it."},
    {"finding": "Published-version figures other than nearly 10%, such as per-condition rates, model names or pair counts", "reason": "Not verified. nature.com serves a client challenge to automated readers, and the release gives no other result figure. The preprint numbers (c33, c39) come from a two-model version."},
    {"finding": "Publication date of September 19th, 2026 from Crossref as a standalone data claim", "reason": "The only verbatim string is a JSON token under the four-word quote floor. The date is carried by c29 from the preprint's cover page."},
    {"finding": "Research Square abstract page as the citation for the preprint claims", "reason": "Only the page title rendered for the checker. Every preprint claim cites the PDF instead, except c26, whose banner is on the page alone (see its note)."},
    {"finding": "Jarrett's two-word quote on wording", "reason": "Verified verbatim, but not carried because it holds a banned word. c4 and c21 carry his other verified quotes."},
    {"finding": "The release's comparison to human triage of frequent flyers", "reason": "Verified verbatim, but the only quote that proves it contains a banned word. c16 carries the frequent ED finding."},
]
Path(__file__).with_name("claims.json").write_text(json.dumps({"claims": claims, "rejected": rejected}, indent=1, ensure_ascii=False) + "\n")
print(len(claims), "claims")
