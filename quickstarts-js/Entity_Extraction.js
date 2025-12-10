/* Markdown (render)
# Gemini API: Entity extraction

Use Gemini API to speed up some of your tasks, such as searching through text to extract needed information. Entity extraction with a Gemini model is a simple query, and you can ask it to retrieve its answer in the form that you prefer.

This notebook shows how to extract entities into a list.

## Setup
### Install SDK and set-up the client

### API Key Configuration

To ensure security, avoid hardcoding the API key in frontend code. Instead, set it as an environment variable on the server or local machine.

When using the Gemini API client libraries, the key will be automatically detected if set as either `GEMINI_API_KEY` or `GOOGLE_API_KEY`. If both are set, `GOOGLE_API_KEY` takes precedence.

For instructions on setting environment variables across different operating systems, refer to the official documentation: [Set API Key as Environment Variable](https://ai.google.dev/gemini-api/docs/api-key#set-api-env-var)

In code, the key can then be accessed as:

```js
ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
```
*/

// [CODE STARTS]
module = await import("https://esm.sh/@google/genai@1.4.0");
GoogleGenAI = module.GoogleGenAI;
ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

MODEL_ID = "gemini-2.5-flash" // ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"]
// [CODE ENDS]

/* Markdown (render)
### Extracting few entities at once

This block of text is about possible ways to travel from the airport to the Colosseum.  

Let's extract all street names and proposed forms of transportation from it.
*/

// [CODE STARTS]
directions = `
To reach the Colosseum from Rome's Fiumicino Airport (FCO),
your options are diverse. Take the Leonardo Express train from FCO
to Termini Station, then hop on metro line A towards Battistini and
alight at Colosseo station.
Alternatively, hop on a direct bus, like the Terravision shuttle, from
FCO to Termini, then walk a short distance to the Colosseum on
Via dei Fori Imperiali.
If you prefer a taxi, simply hail one at the airport and ask to be taken
to the Colosseum. The taxi will likely take you through Via del Corso and
Via dei Fori Imperiali.
A private transfer service offers a direct ride from FCO to the Colosseum,
bypassing the hustle of public transport.
If you're feeling adventurous, consider taking the train from
FCO to Ostiense station, then walking through the charming
Trastevere neighborhood, crossing Ponte Palatino to reach the Colosseum,
passing by the Tiber River and Via della Lungara.
Remember to validate your tickets on the metro and buses,
and be mindful of pickpockets, especially in crowded areas.
No matter which route you choose, you're sure to be awed by the
grandeur of the Colosseum.
`;
// [CODE ENDS]

/* Markdown (render)
You will use Gemini Flash model for fast responses.
*/

// [CODE STARTS]
directionsPrompt = `
From the given text, extract the following entities and return a list of them.
Entities to extract: street name, form of transport.
Text: ${directions}
Street = []
Transport = []
`;

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [directionsPrompt],
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

Street = [
    &quot;Via dei Fori Imperiali&quot;,
    &quot;Via del Corso&quot;,
    &quot;Via della Lungara&quot;
]
Transport = [
    &quot;Leonardo Express train&quot;,
    &quot;metro line A&quot;,
    &quot;bus&quot;,
    &quot;Terravision shuttle&quot;,
    &quot;walking&quot;,
    &quot;taxi&quot;,
    &quot;private transfer service&quot;,
    &quot;public transport&quot;,
    &quot;train&quot;,
    &quot;metro&quot;
]

*/

/* Markdown (render)
You can modify the form of the answer for your extracted entities even more:
*/

// [CODE STARTS]
directionsListPrompt = `
From the given text, extract the following entities and
return a list of them.
Entities to extract: street name, form of transport.
Text: ${directions}
Return your answer as two lists:
Street = [street names]
Transport = [forms of transport]
`;

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [directionsListPrompt],
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

Street = [&#x27;Via dei Fori Imperiali&#x27;, &#x27;Via del Corso&#x27;, &#x27;Via della Lungara&#x27;]
Transport = [&#x27;Leonardo Express train&#x27;, &#x27;metro line A&#x27;, &#x27;bus&#x27;, &#x27;Terravision shuttle&#x27;, &#x27;taxi&#x27;, &#x27;private transfer service&#x27;, &#x27;train&#x27;, &#x27;walking&#x27;, &#x27;metro&#x27;]

*/

/* Markdown (render)
### Numbers

Try entity extraction of phone numbers
*/

// [CODE STARTS]
customerServiceEmail = `
Hello,
Thank you for reaching out to our customer support team regarding your
recent purchase of our premium subscription service.
Your activation code has been sent to +87 668 098 344
Additionally, if you require immediate assistance, feel free to contact us
directly at +1 (800) 555-1234.
Our team is available Monday through Friday from 9:00 AM to 5:00 PM PST.
For after-hours support, please call our
dedicated emergency line at +87 455 555 678.
Thanks for your business and look forward to resolving any issues
you may encounter promptly.
Thank you.
`;

// [CODE ENDS]

// [CODE STARTS]
phonePrompt = `
From the given text, extract the following entities and return a list of them.
Entities to extract: phone numbers.
Text: ${customerServiceEmail}
Return your answer in a list:
`;

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [phonePrompt],
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

```json
[
  &quot;+87 668 098 344&quot;,
  &quot;+1 (800) 555-1234&quot;,
  &quot;+87 455 555 678&quot;
]
```

*/

/* Markdown (render)
### URLs


Try entity extraction of URLs and get response as a clickable link.
*/

// [CODE STARTS]
urlText = `
Gemini API billing FAQs

This page provides answers to frequently asked questions about billing
for the Gemini API. For pricing information, see the pricing page
https://ai.google.dev/pricing.
For legal terms, see the terms of service
https://ai.google.dev/gemini-api/terms#paid-services.

What am I billed for?
Gemini API pricing is based on total token count, with different prices
for input tokens and output tokens. For pricing information,
see the pricing page https://ai.google.dev/pricing.

Where can I view my quota?
You can view your quota and system limits in the Google Cloud console
https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas.

Is GetTokens billed?
Requests to the GetTokens API are not billed,
and they don't count against inference quota.
`;

// [CODE ENDS]

// [CODE STARTS]
urlPrompt = `
From the given text, extract the following entities and return a list of them.
Entities to extract: URLs.
Text: ${urlText}
Do not duplicate entities.
Return your answer in a markdown format:
`;

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [urlPrompt],
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

- `https://ai.google.dev/pricing`
- `https://ai.google.dev/gemini-api/terms#paid-services`
- `https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas`

*/