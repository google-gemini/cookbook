# Gemini examples for TypeScript

This folder contains a collection of examples for the Gemini API, with TypeScript. These are advanced examples and might be quite complex as they often use one of more Gemini capabilities.

To try out these samples, you'll need Node.js v18+ and `tsx`.

## Setup
Install the dependencies by running the following command:

```
npm install
```

## Requirements

Follow the instructions on Google AI Studio [setup page](https://makersuite.google.com/app/apikey) to obtain an API key. This sample assumes that you're providing an `API_KEY` environment variable.

Input your API key into the `API_KEY` environment variable and run the following command in your command line:

```
export API_KEY=<your-api-key>
```
## Table of contents

Each of these sample files can be run using Node.js and `tsx` from the command line.  You can run the file by typing `npx tsx <file-name>.ts`.

| File                                                     | Description | Features | Open |
|----------------------------------------------------------| ----------- | -------- | ---- |
| [castle_detection_with_explicit_types.ts](./castle_detection_with_explicit_types.ts)    | Ask Gemini to describe a medieval castle | Explicitly typed chat, Image detection | `npx tsx castle_detection_with_explicit_types.ts` |