# Contributing to the Gemini API Cookbook

We would love to accept your patches and contributions to the Gemini API Cookbook. We are excited that you are considering donating some of your time, and this guide will help us be respectful of that time.

# Before you send anything

## Sign our contributor agreement

All contributions to this project must be accompanied by a [Contributor License Agreement](https://cla.developers.google.com/about) (CLA). You (or your employer) retain the copyright to your contribution; this simply gives us permission to use and redistribute your contributions as part of the project.

If you or your current employer have already signed the Google CLA (even if it was for a different project), you probably don't need to do it again.

Visit [https://cla.developers.google.com/](https://cla.developers.google.com/) to see your current agreements or to sign a new one.

## Style guides

Before you start writing, take a look at the [technical writing style guide](https://developers.google.com/style). You don’t need to fully digest the whole document, but do read the [highlights](https://developers.google.com/style/highlights) so you can anticipate the most common feedback.

Also check out the relevant [style guide](https://google.github.io/styleguide/) for the language you will be using. These apply strictly to raw code files (e.g. *.py, *.js), though code fragments in documentation (such as markdown files or notebooks) tend to favor readability over strict adherence.

For Python notebooks (*.ipynb files), consider running `pyink` over your notebook. It is not required, but it will avoid style-related nits.

# Making changes

## Small fixes

Small fixes, such as typos or bug fixes, can be submitted directly via a pull request.

## Content submission

Before you send a PR, or even write a single line, please file an [issue](https://github.com/google-gemini/cookbook/issues). There we can discuss the request and provide guidance about how to structure any content you write.

Adding a new guide often involves lots of detailed reviews and we want to make sure that your idea is fully formed and has full support before you start writing anything. If you want to port an existing guide across (e.g. if you have a guide for Gemini on your own GitHub), feel free to link to it in the issue.

When you're ready, start by using the [notebook
template](./templates/Template.ipynb) and following the guidance within.

## Things we consider

When accepting a new guide, we want to balance a few aspects.
* Originality - e.g. Is there another guide that does the same thing?
* Pedagogy - e.g. Does this guide teach something useful? Specifically for a Gemini API feature?
* Quality - e.g. Does this guide contain clear, descriptive prose? Is the code easy to understand?

It is not crucial for a submission to be strong along all of these dimensions, but the stronger the better. Old submissions may be replaced in favor of newer submissions that exceed these properties.

## Attribution
If you have authored a new guide from scratch, you are welcome to include a byline at the top of the document with your name and GitHub username.

## Handling WiFi and Proxy Issues

### Troubleshooting Common WiFi Problems

1. **Check your WiFi connection**: Ensure that your device is connected to the correct WiFi network and that the signal strength is strong.
2. **Restart your router**: Sometimes, simply restarting your router can resolve connectivity issues.
3. **Check for interference**: Other electronic devices can interfere with your WiFi signal. Try moving your router to a different location.
4. **Update your router firmware**: Check if there are any firmware updates available for your router and install them.
5. **Contact your ISP**: If you are still experiencing issues, contact your Internet Service Provider for assistance.

### Configuring Proxy Settings

1. **Identify your proxy server**: Obtain the proxy server address and port number from your network administrator or ISP.
2. **Configure your operating system**:
   - **Windows**: Go to Settings > Network & Internet > Proxy. Enter the proxy server address and port number.
   - **Mac**: Go to System Preferences > Network > Advanced > Proxies. Enter the proxy server address and port number.
   - **Linux**: The steps may vary depending on your distribution. Generally, you can configure the proxy settings in the network settings or by editing the `/etc/environment` file.
3. **Configure your browser**: Most browsers have their own proxy settings. Refer to the documentation for your specific browser to configure the proxy settings.
4. **Test your connection**: After configuring the proxy settings, test your connection to ensure that it is working correctly.

### Reporting WiFi and Proxy-Related Bugs

If you encounter any issues related to WiFi or proxy settings while using the Gemini API, please follow these steps to report the bug:

1. **Check existing issues**: Before reporting a new bug, check the [issue tracker](https://github.com/google-gemini/cookbook/issues) to see if the issue has already been reported.
2. **Create a new issue**: If the issue has not been reported, create a new issue in the [issue tracker](https://github.com/google-gemini/cookbook/issues/new).
3. **Provide detailed information**: Include as much information as possible about the issue, including:
   - A description of the problem
   - Steps to reproduce the issue
   - Any error messages or logs
   - Your operating system and browser version
   - Any other relevant information
4. **Follow up**: Monitor the issue tracker for any updates or requests for additional information from the maintainers.
