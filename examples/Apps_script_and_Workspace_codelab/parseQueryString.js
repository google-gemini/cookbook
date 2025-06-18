/**
 * Parses a query string into an object.
 *
 * @param {string} queryString The query string to parse.
 * @return {object} An object containing the parsed key-value pairs.
 */
function parseQueryString(queryString) {
  const params = {};
  if (!queryString) {
    return params;
  }

  // Remove leading '?' if present
  if (queryString.startsWith('?')) {
    queryString = queryString.substring(1);
  }

  if (!queryString) { // Check again in case query string was only "?"
    return params;
  }

  const pairs = queryString.split('&');

  for (let i = 0; i < pairs.length; i++) {
    const pair = pairs[i].split('=');
    const key = decodeURIComponent(pair[0]);
    let value = '';
    if (pair.length > 1) {
      value = decodeURIComponent(pair[1] || '');
    }

    if (key in params) {
      if (Array.isArray(params[key])) {
        params[key].push(value);
      } else {
        params[key] = [params[key], value];
      }
    } else {
      params[key] = value;
    }
  }

  return params;
}
