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
const geminiEndpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${geminiApiKey}`;

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
  try {
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
      'payload': JSON.stringify(payload),
      'muteHttpExceptions': true,
      'timeoutInSeconds': 0.0 
    };

    const response = UrlFetchApp.fetch(geminiEndpoint, options);
    const statusCode = response.getResponseCode();
    
    if (statusCode !== 200) {
      console.error(`Gemini API request failed with status code: ${statusCode}`);
      return `Error: API request failed with status code ${statusCode}`;
    }
    
    const responseText = response.getContentText();
    let data;
    try {
      data = JSON.parse(responseText);
    } catch (parseError) {
      console.error("Failed to parse API response:", parseError);
      return "Error: Failed to parse API response";
    }
    
    if (!data.candidates || !data.candidates[0] || 
        !data.candidates[0].content || !data.candidates[0].content.parts || 
        !data.candidates[0].content.parts[0]) {
      console.error("Unexpected API response format:", responseText);
      return "Error: Unexpected API response format";
    }
    
    const content = data.candidates[0].content.parts[0].text;
    return content;
  } catch (error) {
    console.error("Error in callGemini:", error);
    return `Error: ${error.message}`;
  }
}

function testGemini() {
  try {
    const prompt = "The best thing since sliced bread is";
    const output = callGemini(prompt);
    
    if (typeof output === 'string' && output.startsWith("Error:")) {
      console.error("Gemini API test failed:", output);
    } else {
      console.log(prompt, output);
    }
  } catch (error) {
    console.error("Error in testGemini:", error);
  }
}


function callGeminiProVision(prompt, image, temperature=0) {
  try {
    let imageData;
    try {
      imageData = Utilities.base64Encode(image.getAs('image/png').getBytes());
    } catch (imgError) {
      console.error("Error encoding image:", imgError);
      return "Error: Failed to encode image data";
    }

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
      'payload': JSON.stringify(payload),
      'muteHttpExceptions': true
    };

    const response = UrlFetchApp.fetch(geminiEndpoint, options);
    const statusCode = response.getResponseCode();
    
    if (statusCode !== 200) {
      console.error(`Gemini Vision API request failed with status code: ${statusCode}`);
      return `Error: API request failed with status code ${statusCode}`;
    }
    
    const responseText = response.getContentText();
    let data;
    try {
      data = JSON.parse(responseText);
    } catch (parseError) {
      console.error("Failed to parse API response:", parseError);
      return "Error: Failed to parse API response";
    }
    
    if (!data.candidates || !data.candidates[0] || 
        !data.candidates[0].content || !data.candidates[0].content.parts || 
        !data.candidates[0].content.parts[0]) {
      console.error("Unexpected API response format:", responseText);
      return "Error: Unexpected API response format";
    }
    
    const content = data.candidates[0].content.parts[0].text;
    return content;
  } catch (error) {
    console.error("Error in callGeminiProVision:", error);
    return `Error: ${error.message}`;
  }
}


function testGeminiVision() {
  try {
    const prompt = "Provide a fun fact about this object.";
    
    let image;
    try {
      image = UrlFetchApp.fetch('https://storage.googleapis.com/generativeai-downloads/images/instrument.jpg').getBlob();
    } catch (fetchError) {
      console.error("Failed to fetch test image:", fetchError);
      return;
    }
    
    const output = callGeminiProVision(prompt, image);
    
    if (typeof output === 'string' && output.startsWith("Error:")) {
      console.error("Gemini Vision API test failed:", output);
    } else {
      console.log(prompt, output);
    }
  } catch (error) {
    console.error("Error in testGeminiVision:", error);
  }
}

function callGeminiWithTools(prompt, tools, temperature=0) {
  try {
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
      'payload': JSON.stringify(payload),
      'muteHttpExceptions': true
    };

    const response = UrlFetchApp.fetch(geminiEndpoint, options);
    const statusCode = response.getResponseCode();
    
    if (statusCode !== 200) {
      console.error(`Gemini Tools API request failed with status code: ${statusCode}`);
      return `Error: API request failed with status code ${statusCode}`;
    }
    
    const responseText = response.getContentText();
    let data;
    try {
      data = JSON.parse(responseText);
    } catch (parseError) {
      console.error("Failed to parse API response:", parseError);
      return "Error: Failed to parse API response";
    }
    
    if (!data.candidates || !data.candidates[0] || 
        !data.candidates[0].content || !data.candidates[0].content.parts || 
        !data.candidates[0].content.parts[0]) {
      console.error("Unexpected API response format:", responseText);
      return "Error: Unexpected API response format";
    }
    
    const content = data.candidates[0].content.parts[0].functionCall;
    if (!content) {
      console.error("No function call found in response:", responseText);
      return "Error: No function call returned from API";
    }
    
    return content;
  } catch (error) {
    console.error("Error in callGeminiWithTools:", error);
    return `Error: ${error.message}`;
  }
}

function testGeminiTools() {
  try {
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
    
    if (typeof output === 'string' && output.startsWith("Error:")) {
      console.error("Gemini Tools API test failed:", output);
    } else {
      console.log(prompt, output);
    }
  } catch (error) {
    console.error("Error in testGeminiTools:", error);
  }
}

function attachFileToMeeting(event, file, fileName) {
  try {
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
  } catch (error) {
    console.error("Error in attachFileToMeeting:", error);
    throw error; // Re-throw to maintain original behavior
  }
}

function setupMeeting(time, recipient, filename) {
  try {
    const files = DriveApp.getFilesByName(filename);
    if (!files.hasNext()) {
      console.error(`File not found: ${filename}`);
      return `Error: File not found: ${filename}`;
    }
    
    const file = files.next();
    const blogContent = file.getAs("text/*").getDataAsString();
    
    var geminiOutput = callGemini("Give me a really short title of this blog and a summary with less than three sentences. Please return the result as a JSON with two fields: title and summary. \n" +  blogContent);
    
    if (typeof geminiOutput === 'string' && geminiOutput.startsWith("Error:")) {
      console.error("Failed to generate meeting content:", geminiOutput);
      return geminiOutput;
    }

    // The Gemini model likes to enclose the JSON with ```json and ```
    try {
      geminiOutput = JSON.parse(geminiOutput.replace(/```(?:json|)/g, ""));  
    } catch (parseError) {
      console.error("Failed to parse Gemini output as JSON:", parseError);
      return "Error: Failed to parse Gemini output as JSON";
    }
    
    const title = geminiOutput['title'];
    const fileSummary = geminiOutput['summary'];

    const event = CalendarApp.getDefaultCalendar().createEventFromDescription(`meet ${recipient} at ${time} to discuss "${title}"`); 
    event.setDescription(fileSummary);
    attachFileToMeeting(event, file, filename);
    
    return "Meeting created successfully";
  } catch (error) {
    console.error("Error in setupMeeting:", error);
    return `Error: ${error.message}`;
  }
}

function draftEmail(sheet_name, recipient) {
  try {
    const prompt = `Compose the email body for ${recipient} with your insights for this chart. Use information in this chart only and do not do historical comparisons. Be concise.`;

    var files = DriveApp.getFilesByName(sheet_name);
    if (!files.hasNext()) {
      console.error(`Sheet not found: ${sheet_name}`);
      return `Error: Sheet not found: ${sheet_name}`;
    }
    
    var sheet;
    try {
      sheet = SpreadsheetApp.openById(files.next().getId()).getSheetByName("Sheet1");
      if (!sheet) {
        console.error("Sheet1 not found in the spreadsheet");
        return "Error: Sheet1 not found in the spreadsheet";
      }
    } catch (sheetError) {
      console.error("Error opening spreadsheet:", sheetError);
      return `Error: ${sheetError.message}`;
    }
    
    var charts = sheet.getCharts();
    if (charts.length === 0) {
      console.error("No charts found in the sheet");
      return "Error: No charts found in the sheet";
    }
    
    var expenseChart = charts[0];
    
    var chartFile;
    try {
      chartFile = DriveApp.createFile(expenseChart.getBlob().setName("ExpenseChart.png"));
    } catch (chartError) {
      console.error("Error creating chart file:", chartError);
      return `Error: ${chartError.message}`;
    }
    
    var emailBody = callGeminiProVision(prompt, expenseChart);
    if (typeof emailBody === 'string' && emailBody.startsWith("Error:")) {
      console.error("Failed to generate email content:", emailBody);
      return emailBody;
    }
    
    try {
      GmailApp.createDraft(recipient+"@demo-email-provider.com", "College expenses", emailBody, {
          attachments: [chartFile.getAs(MimeType.PNG)],
          name: 'myname'
      });
    } catch (emailError) {
      console.error("Error creating email draft:", emailError);
      return `Error: ${emailError.message}`;
    }
    
    return "Email draft created successfully";
  } catch (error) {
    console.error("Error in draftEmail:", error);
    return `Error: ${error.message}`;
  }
}

function createDeck(topic) {
  try {
    const prompt = `I'm preparing a ${NUM_SLIDES}-slide deck to discuss ${topic}. Please help me brainstorm and generate main bullet points for each slide. Keep the title of each slide short. Please produce the result as a valid JSON so that I can pass it to other APIs.`;
    
    var geminiOutput = callGemini(prompt, 0.4);
    if (typeof geminiOutput === 'string' && geminiOutput.startsWith("Error:")) {
      console.error("Failed to generate deck content:", geminiOutput);
      return geminiOutput;
    }
    
    // The Gemini model likes to enclose the JSON with ```json and ```
    geminiOutput = geminiOutput.replace(/```(?:json|)/g, "");
    
    let bulletPoints;
    try {
      bulletPoints = JSON.parse(geminiOutput);
    } catch (parseError) {
      console.error("Failed to parse Gemini output as JSON:", parseError);
      return "Error: Failed to parse Gemini output as JSON";
    }
      
    // Create a Google Slides presentation.
    let presentation;
    try {
      presentation = SlidesApp.create("My New Presentation");
    } catch (slideError) {
      console.error("Error creating presentation:", slideError);
      return `Error: ${slideError.message}`;
    }

    // Set up the opening slide.
    var slide = presentation.getSlides()[0]; 
    var shapes = slide.getShapes();
    shapes[0].getText().setText(topic);

    var body;
    try {
      for (var i = 0; i < NUM_SLIDES; i++) {
          slide = presentation.appendSlide(SlidesApp.PredefinedLayout.TITLE_AND_BODY);
          shapes = slide.getShapes();
          // Set title.
          shapes[0].getText().setText(bulletPoints['slides'][i]['title']);
      
          // Set body.
          body = "";
          for (var j = 0; j < bulletPoints['slides'][i]['bullets'].length; j++) {
            body += '* ' + bulletPoints['slides'][i]['bullets'][j] + '\n';
          }
          shapes[1].getText().setText(body);
      } 
    } catch (slideContentError) {
      console.error("Error populating slides:", slideContentError);
      return `Error: ${slideContentError.message}`;
    }

    return presentation.getUrl();
  } catch (error) {
    console.error("Error in createDeck:", error);
    return `Error: ${error.message}`;
  }
}