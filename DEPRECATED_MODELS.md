# Deprecated Models Report for Gemini API Cookbook

This report identifies models used in this repository that are deprecated according to the [official Gemini API deprecation documentation](https://ai.google.dev/gemini-api/docs/deprecations).

**Current Date:** February 5, 2026

## Summary of Findings

The following models found in the repository are either already shut down or scheduled for shutdown.

### Models Already Shut Down
These models are completely turned off and their endpoints are no longer available.

| Model ID | Shutdown Date | Recommended Replacement |
| :--- | :--- | :--- |
| `gemini-2.5-pro-preview-03-25` | Dec 2, 2025 | `gemini-3-pro-preview` |
| `gemini-2.5-pro-preview-05-06` | Dec 2, 2025 | `gemini-3-pro-preview` |
| `gemini-2.5-pro-preview-06-05` | Dec 2, 2025 | `gemini-3-pro-preview` |
| `gemini-2.5-flash-preview-05-20` | Nov 18, 2025 | `gemini-3-flash-preview` |
| `gemini-2.5-flash-image-preview` | Jan 15, 2026 | `gemini-2.5-flash-image` |
| `gemini-2.0-flash-preview-image-generation` | Nov 14, 2025 | `gemini-2.5-flash-image` |
| `gemini-2.0-flash-lite-preview` | Dec 9, 2025 | `gemini-2.5-flash-lite` |
| `gemini-2.0-flash-lite-preview-02-05` | Dec 9, 2025 | `gemini-2.5-flash-lite` |
| `gemini-2.0-flash-live-001` | Dec 9, 2025 | `gemini-2.5-flash-native-audio-preview-12-2025` |
| `gemini-live-2.5-flash-preview` | Dec 9, 2025 | `gemini-2.5-flash-native-audio-preview-12-2025` |
| `text-embedding-004` | Jan 14, 2026 | `gemini-embedding-001` |
| `imagen-3.0-generate-002` | Nov 10, 2025 | `imagen-4.0-generate-001` |
| `veo-3.0-generate-preview` | Nov 12, 2025 | `veo-3.1-generate-preview` |
| `veo-3.0-fast-generate-preview` | Nov 12, 2025 | `veo-3.1-fast-generate-preview` |

### Models Scheduled for Shutdown
These models are currently deprecated and will be shut down on or after the dates listed below.

| Model ID | Shutdown Date | Recommended Replacement |
| :--- | :--- | :--- |
| `gemini-2.5-flash-preview-09-25` | Feb 17, 2026 | `gemini-3-flash-preview` |
| `imagen-4.0-generate-preview-06-06` | Feb 17, 2026 | `imagen-4.0-generate-001` |
| `imagen-4.0-ultra-generate-preview-06-06` | Feb 17, 2026 | `imagen-4.0-ultra-generate-001` |
| `gemini-2.0-flash` | Mar 31, 2026 | `gemini-2.5-flash` |
| `gemini-2.0-flash-001` | Mar 31, 2026 | `gemini-2.5-flash` |
| `gemini-2.0-flash-lite` | Mar 31, 2026 | `gemini-2.5-flash-lite` |
| `gemini-2.0-flash-lite-001` | Mar 31, 2026 | `gemini-2.5-flash-lite` |
| `gemini-2.5-pro` | Jun 17, 2026 | `gemini-3-pro-preview` |
| `gemini-2.5-flash` | Jun 17, 2026 | `gemini-3-flash-preview` |
| `text-embedding-001` | Jul 14, 2026 | - |
| `gemini-2.5-flash-lite` | Jul 22, 2026 | - |

## Recommendation

It is highly recommended to update the notebooks and examples in this repository to use the current stable or recommended preview models (e.g., Gemini 3 series) to ensure continued functionality.
