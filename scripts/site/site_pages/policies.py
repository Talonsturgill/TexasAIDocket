"""Public information about the site's contact and question routes."""
from site_context import *


def privacy_page(today: str) -> str:
    body = """
<h1>Privacy</h1>
<div class="prose">
  <p>Texas AI Docket publishes a public record and operates the contact forms and Scanner on this site.</p>
  <p>This page explains what happens when a reader sends information. Public records and private enquiries are handled separately.</p>
  <h2>Messages and service enquiries</h2>
  <p>The forms send the details entered to the desk through FormSubmit. These can include a name, company, email address and message.</p>
  <p>The desk uses those details to read the enquiry and respond. A reply address is optional in the general contact form.</p>
  <p>FormSubmit processes submissions and keeps a temporary submission archive under its own policy. Delivered messages also remain in the desk's Google-hosted inbox.</p>
  <p>See <a href="https://formsubmit.co/privacy.pdf">FormSubmit's privacy policy</a> and <a href="https://policies.google.com/privacy">Google's privacy policy</a>.</p>
  <p>Ask feedback uses the same route. A reader can choose whether to attach the last question and answer before submitting feedback.</p>
  <h2 id="scanner">Scanner requests</h2>
  <p>Scanner receives the website and any optional details submitted with a request. It also records connection information for abuse prevention.</p>
  <p>Cloudflare stores request details and progress. An automated research process reads public business information to prepare the report.</p>
  <p>The research process uses AI services. The free-text note is held for a person to read and is not passed into the automated trigger.</p>
  <p>Request details are not added to the public Docket. The progress link acts as an access key, so share it only with intended readers.</p>
  <p>A report can be prepared as an email draft for a person to review. Requesting a scan does not automatically send that email.</p>
  <h2 id="ask">Questions to Ask</h2>
  <p>Typing a question does not send it. Submitting sends the question and the current conversation through Cloudflare.</p>
  <p>Questions that need a generated answer are processed by Anthropic alongside relevant public records. Answers may be cached for reuse.</p>
  <p>Cloudflare may also process the question to rank relevant records. Usage counters and a salted connection identifier help limit automated abuse.</p>
  <p>Keep confidential information and personal details out of questions. A cached answer can be returned to another reader asking the same question.</p>
  <p>See <a href="https://www.anthropic.com/legal/privacy">Anthropic's privacy policy</a> and <a href="https://www.cloudflare.com/privacypolicy/">Cloudflare's privacy policy</a>.</p>
  <h2>Browser storage and other services</h2>
  <p>Scanner uses temporary browser storage to help a reader resume a request. Cloudflare Turnstile processes connection and browser information for its human check.</p>
  <p>Dictation uses the browser's speech service when available. That service may process audio remotely under the browser provider's privacy practices.</p>
  <p>The site does not install advertising or visitor-tracking analytics. Hosting and form providers can keep operational logs under their own policies.</p>
  <p>Booking links open Calendly. Social links open their respective services. Those services apply their own privacy practices after a reader follows the link.</p>
  <h2>Retention and deletion</h2>
  <p>Contact messages and Scanner reports are kept until manually deleted. There is no fixed automatic deletion schedule for those records.</p>
  <p>Provider archives and backups follow the provider's own retention practices. Deleting a message from the desk does not automatically remove every provider copy.</p>
  <p>To ask what is held or request a correction or deletion, <a href="../services/#start">contact the desk</a>.</p>
  <p>Describe the request and give an email address for the response. Avoid including sensitive documents in the initial message.</p>
</div>
"""
    return page(title=f"Privacy · {SITE_NAME}", desc="How Texas AI Docket handles contact messages, Scanner requests and Ask questions, including retention and requests for deletion.", body=body, depth=1, active=None, today=today, canonical="privacy/")


def services_thanks_page(today: str) -> str:
    return page(title=f"Thank you · {SITE_NAME}",
                desc="The next step after contacting the Texas AI Docket desk about a business enquiry or a question about the record.",
                body='''<h1>Thank you for getting in touch.</h1>
<div class="prose"><p>The desk replies to the email address supplied with the message.</p>
<p><a href="../">Return to Services</a> or <a href="../../record/">explore the Docket</a>.</p></div>''',
                depth=2, active="services/", today=today, canonical="services/thanks/")
