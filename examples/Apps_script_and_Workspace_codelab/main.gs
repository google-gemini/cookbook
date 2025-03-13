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

function main() {
  // const userQuery = "Set up a meeting at 5PM with Helen to discuss the news in the Gemini-1.5-blog.txt file.";  
  // const userQuery = "Draft an email for Mary with insights from the chart in the CollegeExpenses sheet.";
  const userQuery = "Help me put together a deck about water conservation.";

  var tool_use = callGeminiWithTools(userQuery, WORKSPACE_TOOLS);
  Logger.log(tool_use);
  
  if(tool_use['name'] == "setupMeeting") {
    setupMeeting(tool_use['args']['time'], tool_use['args']['recipient'], tool_use['args']['filename']);
    Logger.log("Your meeting has been set up.");
  }
  else if(tool_use['name'] == "draftEmail") {
    draftEmail(tool_use['args']['sheet_name'], tool_use['args']['recipient']);
    Logger.log("Check your Gmail to review the draft");
  }
  else if(tool_use['name'] == 'createDeck') {
    deckURL = createDeck(tool_use['args']['topic']);
    Logger.log("Deck URL: " + deckURL);
  }
  else
    Logger.log("no proper tool found");
}

