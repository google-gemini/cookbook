// Content of parseQueryString.js (ideally this would be imported)
// For this self-contained test, we'll assume parseQueryString is defined globally
// or paste its content here if it's not too large. For now, this test file
// will *not* include the function itself but will be written as if `parseQueryString` is accessible.

// Simple deep equal function for comparing objects and arrays in tests
function deepEqual(obj1, obj2) {
  if (obj1 === obj2) return true;
  if (typeof obj1 !== 'object' || obj1 === null || typeof obj2 !== 'object' || obj2 === null) {
    return false;
  }
  let keys1 = Object.keys(obj1);
  let keys2 = Object.keys(obj2);
  if (keys1.length !== keys2.length) return false;
  for (let key of keys1) {
    if (!keys2.includes(key) || !deepEqual(obj1[key], obj2[key])) {
      return false;
    }
  }
  return true;
}

// Test suite
const tests = [
  {
    name: 'should parse a very simple query string (key=value)',
    input: 'key=value',
    expected: { key: 'value' },
  },
  {
    name: 'should parse a basic query string with multiple parameters',
    input: 'name=John&age=30',
    expected: { name: 'John', age: '30' },
  },
  {
    name: 'should handle query string with leading ?',
    input: '?name=Jane&city=NewYork',
    expected: { name: 'Jane', city: 'NewYork' },
  },
  {
    name: 'should return an empty object for an empty string',
    input: '',
    expected: {},
  },
  {
    name: 'should return an empty object for null input',
    input: null,
    expected: {},
  },
  {
    name: 'should return an empty object for undefined input',
    input: undefined,
    expected: {},
  },
  {
    name: 'should return an empty object for a string with only ?',
    input: '?',
    expected: {},
  },
  {
    name: 'should handle URL-encoded characters',
    input: 'name=John%20Doe&occupation=Software%20Engineer',
    expected: { name: 'John Doe', occupation: 'Software Engineer' },
  },
  {
    name: 'should handle multiple values for the same parameter',
    input: 'key=value1&key=value2&other=abc',
    expected: { key: ['value1', 'value2'], other: 'abc' },
  },
  {
    name: 'should handle a key appearing multiple times, starting with a value then empty then another value',
    input: 'key=value1&key=&key=value3',
    expected: { key: ['value1', '', 'value3'] },
  },
  {
    name: 'should handle parameters with no values (empty string)',
    input: 'name=John&emptyParam=&another=value',
    expected: { name: 'John', emptyParam: '', another: 'value' },
  },
  {
    name: 'should handle parameters with no values at the end',
    input: 'name=John&emptyParam=',
    expected: { name: 'John', emptyParam: '' },
  },
  {
    name: 'should handle a single parameter with no value',
    input: 'empty=',
    expected: { empty: '' },
  },
  {
    name: 'should handle a parameter without an equals sign (current behavior: key becomes empty string)',
    input: 'flag&name=John',
    // Assuming current parseQueryString function's behavior:
    // 'flag'.split('=') -> ['flag']
    // key = decodeURIComponent('flag')
    // value = decodeURIComponent(undefined) -> "undefined" (string)
    // So, this test documents that. If 'flag' should be true or '', function needs change.
    // Based on the provided function, pair[1] would be undefined, and decodeURIComponent(undefined) is "undefined".
    // Let's re-check the function: if (pair.length > 1) { value = decodeURIComponent(pair[1] || ''); } else { value = ''; }
    // So 'flag' would result in key='flag', value=''
    expected: { flag: '', name: 'John'},
  },
  {
    name: 'should handle complex query string with mixed cases',
    input: '?name=John%20Doe&age=30&city=New%20York&hobbies=reading&hobbies=hiking&status=active&empty=&novalue',
     // As per logic for 'novalue': key='novalue', value=''
    expected: {
      name: 'John Doe',
      age: '30',
      city: 'New York',
      hobbies: ['reading', 'hiking'],
      status: 'active',
      empty: '',
      novalue: ''
    },
  },
  {
    name: 'should handle query string with special characters in values',
    input: 'email=test%40example.com&message=Hello%2C%20world%21',
    expected: { email: 'test@example.com', message: 'Hello, world!' },
  }
];

// Function to run tests (assuming parseQueryString is globally available)
function runTests() {
  console.log('Running parseQueryString tests...\n');
  let passedCount = 0;
  let failedCount = 0;

  // This is a placeholder. In a real environment, ensure parseQueryString is loaded.
  // For example, if parseQueryString.js just defines the function globally, this will work.
  // If it uses modules, you'd need an environment that supports them.
  if (typeof parseQueryString !== 'function') {
    console.error('FATAL ERROR: parseQueryString function is not defined. Cannot run tests.');
    console.log('Please ensure parseQueryString.js is loaded before running the tests, or include the function definition in this file.');
    return;
  }

  tests.forEach((test, index) => {
    const result = parseQueryString(test.input);
    const passed = deepEqual(result, test.expected);

    if (passed) {
      console.log(`Test ${index + 1}: ${test.name} - PASSED`);
      passedCount++;
    } else {
      console.error(`Test ${index + 1}: ${test.name} - FAILED`);
      console.error('  Input:    ', test.input);
      console.error('  Expected: ', JSON.stringify(test.expected));
      console.error('  Got:      ', JSON.stringify(result));
      failedCount++;
    }
    console.log('---');
  });

  console.log(`\nTests finished. Passed: ${passedCount}, Failed: ${failedCount}`);
}

// To run the tests, uncomment the line below or run it in a console
// where parseQueryString function is available.
// runTests();

// For the purpose of this environment, we will not call runTests() here
// but the structure is ready.
console.log("Test file 'parseQueryString.test.js' updated with a simple test runner structure.");
console.log("To execute tests: ensure 'parseQueryString' function is loaded/defined, then call 'runTests()'.");

// Note: The original parseQueryString function needs to be accessible for these tests to run.
// One way to ensure this for a standalone HTML file would be:
// <script src="parseQueryString.js"></script>
// <script src="parseQueryString.test.js"></script>
// <script>runTests();</script>
// Or in Node.js:
// const fs = require('fs');
// eval(fs.readFileSync('parseQueryString.js','utf8'));
// eval(fs.readFileSync('parseQueryString.test.js','utf8'));
// runTests();
