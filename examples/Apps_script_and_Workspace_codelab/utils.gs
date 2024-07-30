/**
 * Copyright 2024 Google LLC
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *     http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

const properties = PropertiesService.getScriptProperties().getProperties();
const geminiApiKey = properties['GOOGLE_API_KEY'];
const geminiEndpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=${geminiApiKey}`;

const NUM_SLIDES = 3;

const WORKSPACE_TOOLS = {
 "function_declarations": [
   {
     "name": "setupMeeting",
     "description": "Sets up a meeting in Google Calendar.",
     "parameters": {
       "type": "object",
       "properties": {
         "time": {
           "type": "string",
           "description": "The time of the meeting."
         },
         "recipient": {
           "type": "string",
           "description": "The name of the recipient."
         },   
         "filename": {
           "type": "string",
           "description": "The name of the file."
         },                     
       },
       "required": [
         "time",
         "recipient",
         "filename"
       ]
     }
   },
      {
        "name": "draftEmail",
        "description": "Write an email by analyzing data or charts in a Google Sheets file.",
        "parameters": {
          "type": "object",
          "properties": {
            "sheet_name": {
              "type": "string",
              "description": "The name of the sheet to analyze."
            },
            "recipient": {
              "type": "string",
              "description": "The name of the recipient."
            },            
          },
          "required": [
            "sheet_name",
            "recipient"
          ]
        }
      },   
      {
        "name": "createDeck",
        "description": "Build a simple presentation deck with Google Slides and return the URL.",
        "parameters": {
          "type": "object",
          "properties": {
            "topic": {
              "type": "string",
              "description": "The topic that the presentation is about."
            },
          },
          "required": [
            "topic"
          ]
        }
      },

   // You add tools here.        
 ]
};

function callGemini(prompt, temperature=0) {
  const payload = {
    "contents": [
      {
        "parts": [
          {
            "text": prompt
          },
        ]
      }
    ], 
    "generationConfig":  {
      "temperature": temperature,
    },
  };

  const options = { 
    'method' : 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload)
  };

  const response = UrlFetchApp.fetch(geminiEndpoint, options);
  const data = JSON.parse(response);
  const content = data["candidates"][0]["content"]["parts"][0]["text"];
  return content;
}

function testGemini() {
  const prompt = "The best thing since sliced bread is";
  const output = callGemini(prompt);
  console.log(prompt, output);
}


function callGeminiProVision(prompt, image, temperature=0) {
  const imageData = Utilities.base64Encode(image.getAs('image/png').getBytes());

  const payload = {
    "contents": [
      {
        "parts": [
          {
            "text": prompt
          },
          {
            "inlineData": {
              "mimeType": "image/png",
              "data": imageData
            }
          }          
        ]
      }
    ], 
    "generationConfig":  {
      "temperature": temperature,
    },
  };

  const options = { 
    'method' : 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload)
  };

  const response = UrlFetchApp.fetch(geminiEndpoint, options);
  const data = JSON.parse(response);
  const content = data["candidates"][0]["content"]["parts"][0]["text"];
  return content;
}


function testGeminiVision() {
  const prompt = "Provide a fun fact about this object.";
  const image = UrlFetchApp.fetch('https://storage.googleapis.com/generativeai-downloads/images/instrument.jpg').getBlob();
  const output = callGeminiProVision(prompt, image);
  console.log(prompt, output);
}

function callGeminiWithTools(prompt, tools, temperature=0) {
  const payload = {
    "contents": [
      {
        "parts": [
          {
            "text": prompt
          },
        ]
      }
    ], 
    "tools" : tools,
    "generationConfig":  {
      "temperature": temperature,
    },    
  };

  const options = { 
    'method' : 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload)
  };

  const response = UrlFetchApp.fetch(geminiEndpoint, options);
  const data = JSON.parse(response);
  const content = data["candidates"][0]["content"]["parts"][0]["functionCall"];
  return content;
}

function testGeminiTools() {
  const prompt = "Tell me how many days there are left in this month.";
  const tools = {
    "function_declarations": [
      {
        "name": "datetime",
        "description": "Returns the current date and time as a formatted string.",
        "parameters": {
          "type": "string"
        }
      }
    ]
  };
  const output = callGeminiWithTools(prompt, tools);
  console.log(prompt, output);
}

function attachFileToMeeting(event, file, fileName) {
  // Get the iCal ID for the event.
  const iCalEventId = event.getId();

  // Log the ID and title for debugging.
  console.log(`iCal event ID: ${iCalEventId}`);
  console.log(`event Title: ${event.getTitle()}`);

  // Set up the options for listing the event with the advanced Google Calendar service.
  const options = {
      iCalUID: iCalEventId,
    };

  // Use the primary calendar as the calendar ID to list events.
  const calendarId = 'primary';

  // Use the advanced Google Calendar service to list the event.
  const calEvents = Calendar.Events.list(calendarId, options);

  // Get the Calendar ID used by the advanced Google Calendar service.
  const eventId = calEvents.items[0].id;

  // Get the file URL for the attachment.
  const fileUrl = file.getUrl();

    // Set up the patch options to add the file.
    var patch = {
      attachments: [{
        'fileUrl': fileUrl,
        'title': fileName
      }]
    };

    // Patch the event to add the file as an attachment.
    Calendar.Events.patch(patch, 'primary', eventId, {"supportsAttachments": true});  
}

function setupMeeting(time, recipient, filename) {
  const files = DriveApp.getFilesByName(filename);
  const file = files.next();
  const blogContent = file.getAs("text/*").getDataAsString();
  
  var geminiOutput = callGemini("Give me a really short title of this blog and a summary with less than three sentences. Please return the result as a JSON with two fields: title and summary. \n" +  blogContent);

  // The Gemini model likes to enclose the JSON with ```json and ```
  geminiOutput = JSON.parse(geminiOutput.replace(/```(?:json|)/g, ""));  
  const title = geminiOutput['title'];
  const fileSummary = geminiOutput['summary'];

  const event = CalendarApp.getDefaultCalendar().createEventFromDescription(`meet ${recipient} at ${time} to discuss "${title}"`); 
  event.setDescription(fileSummary);
  attachFileToMeeting(event, file, filename);
}

function draftEmail(sheet_name, recipient) {
  
  const prompt = `Compose the email body for ${recipient} with your insights for this chart. Use information in this chart only and do not do historical comparisons. Be concise.`;

  var files = DriveApp.getFilesByName(sheet_name);
  var sheet = SpreadsheetApp.openById(files.next().getId()).getSheetByName("Sheet1");
  var expenseChart = sheet.getCharts()[0];

  var chartFile = DriveApp.createFile(expenseChart.getBlob().setName("ExpenseChart.png"));
  var emailBody = callGeminiProVision(prompt, expenseChart);
  GmailApp.createDraft(recipient+"@demo-email-provider.com", "College expenses", emailBody, {
      attachments: [chartFile.getAs(MimeType.PNG)],
      name: 'myname'
  });
}

function createDeck(topic) {
  const prompt = `I'm preparing a ${NUM_SLIDES}-slide deck to discuss ${topic}. Please help me brainstorm and generate main bullet points for each slide. Keep the title of each slide short. Please produce the result as a valid JSON so that I can pass it to other APIs.`;
  
  var geminiOutput = callGemini(prompt, 0.4);
  // The Gemini model likes to enclose the JSON with ```json and ```
  geminiOutput = geminiOutput.replace(/```(?:json|)/g, "");
  const bulletPoints = JSON.parse(geminiOutput);
    
  // Create a Google Slides presentation.
  const presentation = SlidesApp.create("My New Presentation");

  // Set up the opening slide.
  var slide = presentation.getSlides()[0]; 
  var shapes = slide.getShapes();
  shapes[0].getText().setText(topic);

  var body;
  for (var i = 0; i < NUM_SLIDES; i++) {
      slide = presentation.appendSlide(SlidesApp.PredefinedLayout.TITLE_AND_BODY);
      shapes = slide.getShapes();
      // Set title.
      shapes[0].getText().setText(bulletPoints['slides'][i]['title']);
  
      // Set body.
      body = "";
      for (var j = 0; j < bulletPoints['slides'][i]['bullets'].length; j++) {
        // Logger.log(j);
        body += '* ' + bulletPoints['slides'][i]['bullets'][j] + '\n';
      }
      shapes[1].getText().setText(body);
  } 

  return presentation.getUrl();
}

