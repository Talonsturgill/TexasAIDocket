# An MD Anderson and UT Medical Branch MRI model scored lower on patients it was not built on

The authors include radiologists at the University of Texas MD Anderson Cancer Center in Houston and at the University of Texas Medical Branch in Galveston. They built a machine learning survival model from MRI radiomic features and tested it on a separate patient group without refitting it. Its discrimination score was lower on the group it was tested on than on the group it was built on. The paper reports overlapping confidence intervals for the two and no test that the difference is real. The authors conclude that the approach showed limited standalone discrimination and support cautious use of it as an exploratory imaging biomarker. The paper is a research result rather than a deployment, and neither institution has published a statement that the model is used in patient care.

- Topic: health-and-education
- Decided by: The University of Texas MD Anderson Cancer Center, with The University of Texas Medical Branch (state-agency)
- Where: Harris, Galveston
- Statistical areas:
  - Houston-Pasadena-The Woodlands, TX
- Status: decided
- Public access: Write to the decider
- Take part: https://pubmed.ncbi.nlm.nih.gov/42716711/

- Last checked: 2026-09-26

## Dates

- 2026-09-09 · filed: Article date recorded by the National Library of Medicine for the online publication

## How this decision moved

One dated line per check, oldest first. A line that says nothing changed means somebody looked and it had not.

- 2026-09-13 · Admitted to the record. A model built at a Texas cancer center scored lower on patients it had not been fitted to. The authors call that limited standalone discrimination and ask for cautious use, and they report no test that the difference is real.
- 2026-09-16 · The MRI model still scored lower on patients it was not built on, and the authors' own reading of that result is unchanged. Nothing has been retracted.
- 2026-09-19 · The result stands as published, and the model has not been reported as refitted to the patients it scored lower on.
- 2026-09-23 · The model still scored lower on the patients it was not built on, which is what the paper reported.
- 2026-09-26 · The paper still reports the model scoring lower on the patients it was not built on.

## Evidence

Every fact above rests on one of these. The words are the source's own.

### The study built the model on one cohort and tested the fixed model on another without refitting it.

> This retrospective study developed a T1 postcontrast MRI radiomics survival model in a public brain metastasis cohort of 198 patients and externally validated the fixed radiomics model, without refitting or recalibration, in an independent cohort of 69 patients.

Source (primary_official): https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=42716711&rettype=abstract&retmode=xml

### The model's discrimination was lower on the outside cohort than on the cohort it was built on.

> The radiomics score had a C-index of 0.615 (95% CI, 0.543-0.687) in the training cohort and 0.574 (95% CI, 0.491-0.658) in external validation.

Source (primary_official): https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=42716711&rettype=abstract&retmode=xml

### The authors state the conclusion as a limit rather than as a result.

> T1 postcontrast MRI radiomics showed limited standalone discrimination for overall survival in patients with brain metastases.

Source (primary_official): https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=42716711&rettype=abstract&retmode=xml

### The authors ask for cautious use and for models that carry more than imaging.

> These results support cautious use of radiomics as an exploratory imaging biomarker and emphasize the need for integrated prognostic models that include clinical, treatment, molecular, and systemic disease variables.

Source (primary_official): https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=42716711&rettype=abstract&retmode=xml

### The neuroradiology authors are at MD Anderson in Houston and the radiology authors at the Medical Branch in Galveston.

> From the Department of Neuroradiology (R.E., H.A.Q., S.A., A.M., P.K.), The University of Texas MD Anderson Cancer Center, Houston, TX 77030, USA; Department of Radiology (E.C.), Duke University Medical Center, Durham, NC, USA; Department of Radiology (H.A.S., A.N., M.W.), The University of Texas Medical Branch, Galveston, TX, USA

Source (primary_official): https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=42716711&rettype=abstract&retmode=xml

### The final model kept a small number of imaging features after selection.

> The final model retained 7 nonzero T1 postcontrast radiomics features after correlation filtering and elastic-net selection.

Source (primary_official): https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=42716711&rettype=abstract&retmode=xml

### Adding the established clinical score did not lift the model above its training figure.

> In the external-validation subset with available Graded Prognostic Assessment, the combined radiomics plus Graded Prognostic Assessment model had a C-index of 0.591 (95% CI, 0.509-0.672).

Source (primary_official): https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=42716711&rettype=abstract&retmode=xml

